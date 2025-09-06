import tempfile
import os
from datetime import date
from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from api.dependency.database import get_session
from api.main import app
from api.routes.fastapi_users import current_active_superuser, current_active_user, fastapi_users
from models.base import Base
from models.collection import Collection
from models.grading_company import GradingCompany
from models.grading_info import GradingInfo
from models.item import Item
from models.item_price_history import ItemPriceHistory
from models.user import User
from utils.enums import PriceType
from utils.tokens import generate_share_token


# Global variable to store shared test database path
_test_db_path = None


def get_test_db_path():
    """Get or create the path for the shared test database."""
    global _test_db_path
    if _test_db_path is None:
        # Create a temporary file for the test database
        fd, _test_db_path = tempfile.mkstemp(suffix='.db', prefix='test_numismatist_')
        os.close(fd)  # Close the file descriptor, we just need the path
    return _test_db_path


@pytest_asyncio.fixture(scope="session")
async def shared_db_engine():
    """Create a shared database engine with pre-loaded grading data for the entire test session."""
    db_path = get_test_db_path()
    database_url = f"sqlite+aiosqlite:///{db_path}"
    
    engine = create_async_engine(
        database_url,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    
    # Create tables and load grading data once for all tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Load grading data once for all tests
    async with AsyncSession(engine) as session:
        from tests.utils.sql_data_loader import SQLDataLoader
        loader = SQLDataLoader()
        await loader.load_all_grading_data_with_orm(session)
    
    yield engine
    
    # Cleanup
    await engine.dispose()
    try:
        os.unlink(db_path)
    except (OSError, FileNotFoundError):
        pass


@pytest_asyncio.fixture(scope="function")
async def test_db_engine(shared_db_engine):
    """Create a test database engine that reuses shared grading data."""
    yield shared_db_engine


@pytest_asyncio.fixture(scope="function") 
async def test_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session with cleanup after each test."""
    async with AsyncSession(test_db_engine) as session:
        yield session
        
        # Clean up user-generated data after each test
        # This preserves grading companies and grades data
        await session.execute(text("DELETE FROM grading_info"))
        await session.execute(text("DELETE FROM item_price_history"))
        await session.execute(text("DELETE FROM item_images"))
        await session.execute(text("DELETE FROM transaction_items"))
        await session.execute(text("DELETE FROM transaction_collections"))
        await session.execute(text("DELETE FROM transactions"))
        await session.execute(text("DELETE FROM items"))
        await session.execute(text("DELETE FROM collections"))
        await session.execute(text("DELETE FROM counterparties"))
        await session.execute(text("DELETE FROM access_tokens"))
        await session.execute(text("DELETE FROM users"))
        await session.commit()


@pytest.fixture(scope="function")
def client(test_db_engine):
    """Create a test client with dependency override."""
    
    async def override_get_session():
        async with AsyncSession(test_db_engine) as session:
            yield session
    
    app.dependency_overrides[get_session] = override_get_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def authenticated_client(test_session, test_user):
    """Create a test client with authentication override."""
    
    def override_get_session():
        return test_session
    
    def override_current_user():
        return test_user
    
    # Override the dependencies
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[current_active_user] = override_current_user
    
    # Also override FastAPI-Users internal dependencies
    app.dependency_overrides[fastapi_users.current_user(active=True)] = override_current_user
    app.dependency_overrides[fastapi_users.current_user(active=True, verified=True)] = override_current_user
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function") 
def superuser_client(test_session, test_superuser):
    """Create a test client with superuser authentication override."""
    
    def override_get_session():
        return test_session
    
    def override_current_superuser():
        return test_superuser
    
    # Override the dependencies  
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[current_active_user] = override_current_superuser
    app.dependency_overrides[current_active_superuser] = override_current_superuser
    
    # Also override FastAPI-Users internal dependencies
    app.dependency_overrides[fastapi_users.current_user(active=True)] = override_current_superuser
    app.dependency_overrides[fastapi_users.current_user(active=True, superuser=True)] = override_current_superuser
    app.dependency_overrides[fastapi_users.current_user(active=True, verified=True)] = override_current_superuser
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(test_session) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password="$2b$12$test_hash",  # This is a dummy hash
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    # Expunge from session to avoid greenlet issues in tests
    test_session.expunge(user)
    return user


@pytest_asyncio.fixture
async def test_superuser(test_session) -> User:
    """Create a test superuser."""
    user = User(
        email="admin@example.com",
        hashed_password="$2b$12$test_hash",  # This is a dummy hash
        is_active=True,
        is_superuser=True,
        is_verified=True,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    # Expunge from session to avoid greenlet issues in tests
    test_session.expunge(user)
    return user


@pytest_asyncio.fixture
async def test_item(test_session, test_user, test_grading_companies) -> Item:
    """Create a test item with price history and grading info."""
    
    item = Item(
        name="Test Coin",
        year="2024",
        description="A test coin for testing purposes",
        material="gold",
        weight=10.5,
        user_id=test_user.id,
    )
    test_session.add(item)
    await test_session.flush()  # Get the item ID
    
    # Create a purchase price history entry
    price_history = ItemPriceHistory(
        item_id=item.id,
        price=50000,  # $500 in pennies
        type=PriceType.PURCHASE,
        date=date.today()
    )
    test_session.add(price_history)
    
    ngc_company = next((c for c in test_grading_companies if c.short_name == "NGC"), None)
    if ngc_company:
        grading_info = GradingInfo(
            item_id=item.id,
            company_id=ngc_company.id,
            certificate_number='5712634-005',
            grade='MS 65',
            grade_details='CLEANED',
            note='Test coin with original surfaces'
        )
        test_session.add(grading_info)
    
    await test_session.commit()
    await test_session.refresh(item)
    # Expunge from session to avoid greenlet issues in tests
    test_session.expunge(item)
    return item


@pytest_asyncio.fixture
async def test_item_no_grading_info(test_session, test_user) -> Item:
    """Create a test item with price history but no grading info."""
    
    item = Item(
        name="Test Coin No Grading",
        year="2024", 
        description="A test coin without grading info",
        material="gold",
        weight=10.5,
        user_id=test_user.id,
    )
    test_session.add(item)
    await test_session.flush()  # Get the item ID
    
    # Create a purchase price history entry
    price_history = ItemPriceHistory(
        item_id=item.id,
        price=50000,  # $500 in pennies
        type=PriceType.PURCHASE,
        date=date.today()
    )
    test_session.add(price_history)
    
    await test_session.commit()
    await test_session.refresh(item)
    # Expunge from session to avoid greenlet issues in tests
    test_session.expunge(item)
    return item


@pytest_asyncio.fixture
async def test_collection(test_session, test_user) -> Collection:
    """Create a test collection."""
    collection = Collection(
        name="Test Collection",
        description="A test collection for testing purposes",
        user_id=test_user.id,
    )
    test_session.add(collection)
    await test_session.commit()
    await test_session.refresh(collection)
    # Expunge from session to avoid greenlet issues in tests
    test_session.expunge(collection)
    return collection


@pytest_asyncio.fixture
async def test_collection_with_item(test_session, test_user) -> tuple[str, str]:
    """Create a test collection with an item and return their IDs."""
    # Create collection
    collection = Collection(
        name="Collection with Item",
        description="A collection that contains an item",
        user_id=test_user.id,
    )
    test_session.add(collection)
    await test_session.commit()
    await test_session.refresh(collection)
    
    # Store the collection ID
    collection_id = str(collection.id)
    
    # Create item and assign it to the collection
    item = Item(
        name="Collection Item",
        year="2024",
        description="An item in a collection",
        material="silver",
        weight=15.0,
        user_id=test_user.id,
        collection_id=collection.id,
    )
    test_session.add(item)
    
    await test_session.commit()
    await test_session.refresh(item)
    
    # Store the item ID
    item_id = str(item.id)
    
    # Expunge from session to avoid greenlet issues in tests
    test_session.expunge(collection)
    test_session.expunge(item)
    
    return collection_id, item_id


@pytest_asyncio.fixture
async def test_public_collection_with_share(test_session, test_user) -> tuple[Collection, str]:
    """Create a public collection with share token."""
    share_token = generate_share_token()
    collection = Collection(
        name="Public Shared Collection",
        description="A public collection that can be shared",
        share_token=share_token,
        user_id=test_user.id,
    )
    test_session.add(collection)
    await test_session.commit()
    await test_session.refresh(collection)
    # Expunge from session to avoid greenlet issues in tests
    test_session.expunge(collection)
    return collection, share_token


@pytest_asyncio.fixture
async def another_user(test_session) -> User:
    """Create another test user for isolation testing."""
    user = User(
        email="another@example.com",
        hashed_password="$2b$12$another_test_hash",
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    # Expunge from session to avoid greenlet issues in tests
    test_session.expunge(user)
    return user


@pytest_asyncio.fixture
async def another_user_collection(test_session, another_user) -> Collection:
    """Create a collection belonging to another user."""
    collection = Collection(
        name="Another User Collection",
        description="A collection that belongs to another user",
        user_id=another_user.id,
    )
    test_session.add(collection)
    await test_session.commit()
    await test_session.refresh(collection)
    # Expunge from session to avoid greenlet issues in tests
    test_session.expunge(collection)
    return collection


@pytest.fixture(scope="function") 
def another_user_client(test_session, another_user):
    """Create a test client with another user authentication override."""
    
    def override_get_session():
        return test_session
    
    def override_current_user():
        return another_user
    
    # Override the dependencies  
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[current_active_user] = override_current_user
    
    # Also override FastAPI-Users internal dependencies
    app.dependency_overrides[fastapi_users.current_user(active=True)] = override_current_user
    app.dependency_overrides[fastapi_users.current_user(active=True, verified=True)] = override_current_user
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_grading_companies(test_session) -> list[GradingCompany]:
    """Get grading companies loaded from SQL files."""
    from sqlalchemy import select
    
    # Simply query companies from the test database (they should already be loaded)
    result = await test_session.execute(select(GradingCompany))
    companies = result.scalars().all()
    
    # Expunge to avoid session issues
    for company in companies:
        test_session.expunge(company)
    
    return companies


@pytest_asyncio.fixture
async def test_grades(test_session, test_grading_companies) -> list[dict[str, Any]]:
    """Get grades loaded from SQL files."""
    from sqlalchemy import select
    from models.grade import Grade
    from models.grading_company import GradingCompany
    
    # Query grades with company info
    result = await test_session.execute(
        select(Grade, GradingCompany)
        .join(GradingCompany, Grade.company_id == GradingCompany.id)
    )
    
    grades_data = []
    for grade, company in result.all():
        grades_data.append({
            'id': str(grade.id),
            'company_id': str(grade.company_id),
            'company_short_name': company.short_name,
            'category': grade.category,
            'value': grade.value,
            'sort_order': grade.sort_order
        })
    
    return grades_data


@pytest.fixture(scope="function")
def get_auth_headers(user_id: int) -> dict:
    """Get authentication headers for testing."""
    # For testing, we'll mock the authentication
    # In a real scenario, you'd generate a proper JWT token
    return {"Authorization": f"Bearer test_token_{user_id}"}
