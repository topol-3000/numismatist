"""Test configuration and fixtures."""
from datetime import date
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from api.main import app
from api.dependency.database import get_session
from api.routes.fastapi_users import current_active_user, current_active_superuser, fastapi_users
from models.base import Base
from models.user import User
from models.item import Item
from models.item_price_history import ItemPriceHistory
from models.collection import Collection
from utils.tokens import generate_share_token
from utils.enums import PriceType


# Test database URL (in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_db_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with AsyncSession(test_db_engine) as session:
        yield session


@pytest.fixture(scope="function")
def client(test_session):
    """Create a test client with dependency override."""
    
    def override_get_session():
        return test_session
    
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
async def test_item(test_session, test_user) -> Item:
    """Create a test item with price history."""
    
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


def get_auth_headers(user_id: int) -> dict:
    """Get authentication headers for testing."""
    # For testing, we'll mock the authentication
    # In a real scenario, you'd generate a proper JWT token
    return {"Authorization": f"Bearer test_token_{user_id}"}
