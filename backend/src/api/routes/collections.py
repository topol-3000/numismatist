from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.dependency.database import SessionDependency
from api.routes.fastapi_users import current_active_user
from models import Collection, Item, User
from schemas.collection import (
    CollectionCreate, 
    CollectionRead, 
    CollectionUpdate, 
    CollectionWithItems,
    CollectionAddItem,
    CollectionRemoveItem,
    SharedCollectionRead
)
from schemas.item import ItemRead
from utils.tokens import generate_share_token

router = APIRouter(prefix='/collections', tags=['Collections'])


@router.get('/', response_model=list[CollectionRead])
async def get_user_collections(
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
    filter: str = Query(None, description="Filter collections by type: 'shared' for collections with share tokens"),
):
    """Get collections for the current user. Use filter='shared' to get only shared collections."""
    query = select(Collection).where(Collection.user_id == current_user.id)
    
    if filter == "shared":
        query = query.where(Collection.share_token.isnot(None))
    
    query = query.order_by(Collection.created_at.desc())
    result = await session.execute(query)
    collections = result.scalars().all()
    return collections

@router.post('/', response_model=CollectionRead, status_code=status.HTTP_201_CREATED)
async def create_collection(
    collection_data: CollectionCreate,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """Create a new collection."""
    collection = Collection(**collection_data.model_dump(), user_id=current_user.id)
    session.add(collection)
    await session.commit()
    await session.refresh(collection)
    return collection

@router.get('/shared/{share_token}', response_model=SharedCollectionRead)
async def get_shared_collection(
    share_token: str,
    session: SessionDependency,
):
    """Get a publicly shared collection by its share token."""
    result = await session.execute(
        select(Collection)
        .options(selectinload(Collection.items))
        .where(Collection.share_token == share_token)
    )
    collection = result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared collection not found"
        )
    
    return SharedCollectionRead(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        items=[ItemRead.model_validate(item) for item in collection.items],
        created_at=collection.created_at,
        updated_at=collection.updated_at
    )


@router.get('/{collection_id}', response_model=CollectionWithItems)
async def get_collection(
    collection_id: str,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """Get a specific collection by ID with its items."""
    result = await session.execute(
        select(Collection)
        .options(selectinload(Collection.items))
        .where(Collection.id == collection_id, Collection.user_id == current_user.id)
    )
    collection = result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    return collection

@router.put('/{collection_id}', response_model=CollectionRead)
async def update_collection(
    collection_id: str,
    collection_data: CollectionUpdate,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """Update an existing collection."""
    result = await session.execute(
        select(Collection).where(Collection.id == collection_id, Collection.user_id == current_user.id)
    )
    collection = result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    # Update only provided fields
    update_data = collection_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(collection, field, value)
    
    await session.commit()
    await session.refresh(collection)
    return collection


@router.delete('/{collection_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: str,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """Delete a collection."""
    result = await session.execute(
        select(Collection).where(Collection.id == collection_id, Collection.user_id == current_user.id)
    )
    collection = result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    await session.delete(collection)
    await session.commit()


@router.post('/{collection_id}/items', status_code=status.HTTP_204_NO_CONTENT)
async def add_item_to_collection(
    collection_id: str,
    item_data: CollectionAddItem,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """Add an item to a collection."""
    # Check if collection exists and belongs to user
    collection_result = await session.execute(
        select(Collection).where(Collection.id == collection_id, Collection.user_id == current_user.id)
    )
    collection = collection_result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    # Check if item exists and belongs to user
    item_result = await session.execute(
        select(Item).where(Item.id == item_data.item_id, Item.user_id == current_user.id)
    )
    item = item_result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Check if item is already in a collection
    if item.collection_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item is already in the collection"
        )
    
    # Add item to collection
    item.collection_id = collection_id
    await session.commit()


@router.delete('/{collection_id}/items', status_code=status.HTTP_204_NO_CONTENT)
async def remove_item_from_collection(
    collection_id: str,
    item_data: CollectionRemoveItem,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """Remove an item from a collection."""
    # Check if collection exists and belongs to user
    collection_result = await session.execute(
        select(Collection).where(Collection.id == collection_id, Collection.user_id == current_user.id)
    )
    collection = collection_result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    # Check if item exists and belongs to user
    item_result = await session.execute(
        select(Item).where(Item.id == item_data.item_id, Item.user_id == current_user.id)
    )
    item = item_result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Check if item is in this collection
    if item.collection_id != collection_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item is not in the collection"
        )
    
    # Remove item from collection
    item.collection_id = None
    await session.commit()


@router.post('/{collection_id}/share', response_model=CollectionRead)
async def generate_share_link(
    collection_id: str,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """
    Generate a share token for a collection.
    
    Creates a unique token that allows public access to the collection
    when it's marked as public. If a token already exists, returns
    the existing token. Use PUT to regenerate a new token.
    """
    result = await session.execute(
        select(Collection).where(Collection.id == collection_id, Collection.user_id == current_user.id)
    )
    collection = result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    # Generate share token if not exists
    if not collection.share_token:
        collection.share_token = generate_share_token()
        await session.commit()
        await session.refresh(collection)
    
    return collection


@router.put('/{collection_id}/share', response_model=CollectionRead)
async def regenerate_share_link(
    collection_id: str,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """
    Regenerate a new share token for a collection, invalidating the old one.
    
    This is useful when:
    - User wants to revoke access using the old token
    - User lost the original token and needs a new one
    - Security concerns about the current token
    """
    result = await session.execute(
        select(Collection).where(Collection.id == collection_id, Collection.user_id == current_user.id)
    )
    collection = result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    # Always generate a new token, even if one exists
    collection.share_token = generate_share_token()
    await session.commit()
    await session.refresh(collection)
    return collection


@router.delete('/{collection_id}/share', response_model=CollectionRead)
async def revoke_share_link(
    collection_id: str,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """
    Revoke the share token for a collection.
    
    Completely removes the share token, making the collection
    no longer accessible via any share URL. The collection
    will also be removed from the user's shared collections list.
    """
    result = await session.execute(
        select(Collection).where(Collection.id == collection_id, Collection.user_id == current_user.id)
    )
    collection = result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    collection.share_token = None
    await session.commit()
    await session.refresh(collection)
    return collection
