from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, text
from sqlalchemy.orm import selectinload

from api.dependency.database import SessionDependency
from api.routes.fastapi_users import current_active_user
from models import Collection, Item, User
from schemas.collection import (
    CollectionAddItem,
    CollectionCreate,
    CollectionMove,
    CollectionPath,
    CollectionRead,
    CollectionRemoveItem,
    CollectionTree,
    CollectionUpdate,
    CollectionWithItems,
    SharedCollectionRead,
)
from schemas.item import ItemRead
from utils.tokens import generate_share_token

router = APIRouter(prefix="/collections", tags=["Collections"])


@router.get("/", response_model=list[CollectionRead])
async def get_user_collections(
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
    filter: str = Query(
        None,
        description="Filter collections by type: 'shared' for collections with share tokens",
    ),
):
    """Get collections for the current user. Use filter='shared' to get only shared collections."""
    query = select(Collection).where(Collection.user_id == current_user.id)

    if filter == "shared":
        query = query.where(Collection.share_token.isnot(None))

    query = query.order_by(Collection.created_at.desc())
    result = await session.execute(query)
    collections = result.scalars().all()
    return collections


@router.post("/", response_model=CollectionRead, status_code=status.HTTP_201_CREATED)
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


@router.get("/shared/{share_token}", response_model=SharedCollectionRead)
async def get_shared_collection(
    share_token: str,
    session: SessionDependency,
):
    """Get a publicly shared collection by its share token."""
    result = await session.execute(
        select(Collection).options(selectinload(Collection.items)).where(Collection.share_token == share_token)
    )
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shared collection not found")

    return SharedCollectionRead(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        items=[ItemRead.model_validate(item) for item in collection.items],
        created_at=collection.created_at,
        updated_at=collection.updated_at,
    )


@router.get("/tree", response_model=list[CollectionTree])
async def get_collections_tree(
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """Get all root collections with their subcollections as trees."""
    result = await session.execute(
        select(Collection)
        .where(Collection.user_id == current_user.id, Collection.parent_id.is_(None))
        .options(selectinload(Collection.children))
    )
    root_collections = result.scalars().all()

    async def build_tree(coll: Collection) -> CollectionTree:
        children_result = await session.execute(
            select(Collection).options(selectinload(Collection.children)).where(Collection.parent_id == coll.id)
        )
        children = children_result.scalars().all()

        children_trees = []
        for child in children:
            children_trees.append(await build_tree(child))

        items_count_result = await session.execute(
            select(func.count()).select_from(Item).where(Item.collection_id == coll.id)
        )
        direct_items_count = items_count_result.scalar() or 0

        return CollectionTree(
            id=coll.id,
            name=coll.name,
            description=coll.description,
            user_id=coll.user_id,
            parent_id=coll.parent_id,
            share_token=coll.share_token,
            created_at=coll.created_at,
            updated_at=coll.updated_at,
            is_leaf=len(children) == 0,
            is_root=coll.parent_id is None,
            direct_items_count=direct_items_count,
            children=children_trees,
        )

    trees = []
    for collection in root_collections:
        trees.append(await build_tree(collection))

    return trees


@router.get("/{collection_id}", response_model=CollectionWithItems)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    return collection


@router.put("/{collection_id}", response_model=CollectionRead)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    # Update only provided fields
    update_data = collection_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(collection, field, value)

    await session.commit()
    await session.refresh(collection)
    return collection


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    await session.delete(collection)
    await session.commit()


@router.post("/{collection_id}/items", status_code=status.HTTP_204_NO_CONTENT)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    children_result = await session.execute(
        select(func.count()).select_from(Collection).where(Collection.parent_id == collection_id)
    )
    children_count = children_result.scalar() or 0

    if children_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Items can only be added to collections without subcollections (leaf collections)",
        )

    # Check if item exists and belongs to user
    item_result = await session.execute(
        select(Item).where(Item.id == item_data.item_id, Item.user_id == current_user.id)
    )
    item = item_result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    # Check if item is already in a collection
    if item.collection_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item is already in the collection",
        )

    # Add item to collection
    item.collection_id = collection_id
    await session.commit()


@router.delete("/{collection_id}/items", status_code=status.HTTP_204_NO_CONTENT)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    # Check if item exists and belongs to user
    item_result = await session.execute(
        select(Item).where(Item.id == item_data.item_id, Item.user_id == current_user.id)
    )
    item = item_result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    # Check if item is in this collection
    if item.collection_id != collection_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item is not in the collection",
        )

    # Remove item from collection
    item.collection_id = None
    await session.commit()


@router.post("/{collection_id}/share", response_model=CollectionRead)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    # Generate share token if not exists
    if not collection.share_token:
        collection.share_token = generate_share_token()
        await session.commit()
        await session.refresh(collection)

    return collection


@router.put("/{collection_id}/share", response_model=CollectionRead)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    # Always generate a new token, even if one exists
    collection.share_token = generate_share_token()
    await session.commit()
    await session.refresh(collection)
    return collection


@router.delete("/{collection_id}/share", response_model=CollectionRead)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    collection.share_token = None
    await session.commit()
    await session.refresh(collection)
    return collection


# Hierarchy endpoints


@router.post("/{parent_id}/subcollections", response_model=CollectionRead, status_code=status.HTTP_201_CREATED)
async def create_subcollection(
    parent_id: str,
    collection_data: CollectionCreate,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """
    Create a subcollection under the specified parent collection.

    WARNING: Creating a subcollection will automatically remove all items
    from the parent collection, as items can only exist in leaf collections.
    """

    parent_result = await session.execute(
        select(Collection)
        .options(selectinload(Collection.items))
        .where(Collection.id == parent_id, Collection.user_id == current_user.id)
    )
    parent_collection = parent_result.scalar_one_or_none()

    if not parent_collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent collection not found")

    # Clear all items from parent collection before creating subcollection
    # Items can only exist in leaf collections
    if parent_collection.items:
        for item in parent_collection.items:
            item.collection_id = None
        # Note: You might want to log this action or notify the user

    collection_dict = collection_data.model_dump()
    collection_dict["parent_id"] = parent_id
    subcollection = Collection(**collection_dict, user_id=current_user.id)

    session.add(subcollection)
    await session.commit()
    await session.refresh(subcollection)
    return subcollection


@router.get("/{collection_id}/tree", response_model=CollectionTree)
async def get_collection_tree(
    collection_id: str,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """Get a specific collection with all its subcollections as a tree."""
    result = await session.execute(
        select(Collection).where(Collection.id == collection_id, Collection.user_id == current_user.id)
    )
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    async def build_tree(coll: Collection) -> CollectionTree:
        children_result = await session.execute(
            select(Collection).options(selectinload(Collection.children)).where(Collection.parent_id == coll.id)
        )
        children = children_result.scalars().all()

        children_trees = []
        for child in children:
            children_trees.append(await build_tree(child))

        items_count_result = await session.execute(
            select(func.count()).select_from(Item).where(Item.collection_id == coll.id)
        )
        direct_items_count = items_count_result.scalar() or 0

        return CollectionTree(
            id=coll.id,
            name=coll.name,
            description=coll.description,
            user_id=coll.user_id,
            parent_id=coll.parent_id,
            share_token=coll.share_token,
            created_at=coll.created_at,
            updated_at=coll.updated_at,
            is_leaf=len(children) == 0,
            is_root=coll.parent_id is None,
            direct_items_count=direct_items_count,
            children=children_trees,
        )

    return await build_tree(collection)


@router.get("/{collection_id}/path", response_model=CollectionPath)
async def get_collection_path(
    collection_id: str,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """Get the path from root to the specified collection."""
    result = await session.execute(
        select(Collection).where(Collection.id == collection_id, Collection.user_id == current_user.id)
    )
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    path = []
    current = collection

    while current:
        path.insert(0, current)
        if current.parent_id:
            parent_result = await session.execute(select(Collection).where(Collection.id == current.parent_id))
            current = parent_result.scalar_one_or_none()
        else:
            current = None

    return CollectionPath(path=path)


@router.put("/{collection_id}/move", response_model=CollectionRead)
async def move_collection(
    collection_id: str,
    move_data: CollectionMove,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """Move a collection to a new parent."""
    result = await session.execute(
        select(Collection).where(Collection.id == collection_id, Collection.user_id == current_user.id)
    )
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    if move_data.new_parent_id:
        parent_result = await session.execute(
            select(Collection).where(Collection.id == move_data.new_parent_id, Collection.user_id == current_user.id)
        )
        parent_collection = parent_result.scalar_one_or_none()

        if not parent_collection:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent collection not found")

    if move_data.new_parent_id and move_data.new_parent_id == str(collection.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Collection cannot be parent of itself",
        )

    if move_data.new_parent_id:
        all_collections = await session.execute(
            text("SELECT id, parent_id FROM collections WHERE user_id = :user_id"), {"user_id": current_user.id}
        )
        all_data = [(str(row[0]), str(row[1]) if row[1] else None) for row in all_collections.fetchall()]

        def is_descendant(parent_id, target_id, all_collections_data):
            """Check if target_id is a descendant of parent_id"""
            parent_id_norm = parent_id.replace("-", "")
            target_id_norm = target_id.replace("-", "")

            for coll_id, coll_parent_id in all_collections_data:
                if coll_parent_id and coll_parent_id.replace("-", "") == parent_id_norm:
                    if coll_id.replace("-", "") == target_id_norm:
                        return True
                    if is_descendant(coll_id, target_id, all_collections_data):
                        return True
            return False

        if is_descendant(str(collection.id), move_data.new_parent_id, all_data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Moving this collection would create a circular dependency",
            )

    collection.parent_id = move_data.new_parent_id
    await session.commit()
    await session.refresh(collection)
    return collection
