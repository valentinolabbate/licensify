"""
Product API Endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.services.product_service import ProductService
from app.api.deps import get_current_verified_user, get_current_admin_user
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    FeatureDefinition,
    FeatureCreate,
    FeatureUpdate,
    ProductFeaturesResponse,
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=ProductListResponse)
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """Get all products"""
    product_service = ProductService(db)
    
    # Only admins can see inactive products
    if include_inactive and not current_user.is_admin:
        include_inactive = False
    
    products, total = await product_service.get_all(
        skip=skip,
        limit=limit,
        include_inactive=include_inactive
    )
    
    # Add license count
    enriched = []
    for product in products:
        license_count = await product_service.count_licenses(product.id)
        enriched.append(ProductResponse(
            id=product.id,
            name=product.name,
            slug=product.slug,
            description=product.description,
            version=product.version,
            available_features=product.available_features or [],
            default_max_devices=product.default_max_devices,
            default_license_type=product.default_license_type,
            is_active=product.is_active,
            created_at=product.created_at,
            updated_at=product.updated_at,
            license_count=license_count
        ))
    
    return ProductListResponse(products=enriched, total=total)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """Get a specific product"""
    product_service = ProductService(db)
    product = await product_service.get_by_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    license_count = await product_service.count_licenses(product.id)
    
    return ProductResponse(
        id=product.id,
        name=product.name,
        slug=product.slug,
        description=product.description,
        version=product.version,
        available_features=product.available_features or [],
        default_max_devices=product.default_max_devices,
        default_license_type=product.default_license_type,
        is_active=product.is_active,
        created_at=product.created_at,
        updated_at=product.updated_at,
        license_count=license_count
    )


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Create a new product (admin only)"""
    product_service = ProductService(db)
    product = await product_service.create(product_data)
    
    return ProductResponse(
        id=product.id,
        name=product.name,
        slug=product.slug,
        description=product.description,
        version=product.version,
        available_features=product.available_features or [],
        default_max_devices=product.default_max_devices,
        default_license_type=product.default_license_type,
        is_active=product.is_active,
        created_at=product.created_at,
        updated_at=product.updated_at,
        license_count=0
    )


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Update a product (admin only)"""
    product_service = ProductService(db)
    product = await product_service.get_by_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product = await product_service.update(product, product_data)
    license_count = await product_service.count_licenses(product.id)
    
    return ProductResponse(
        id=product.id,
        name=product.name,
        slug=product.slug,
        description=product.description,
        version=product.version,
        available_features=product.available_features or [],
        default_max_devices=product.default_max_devices,
        default_license_type=product.default_license_type,
        is_active=product.is_active,
        created_at=product.created_at,
        updated_at=product.updated_at,
        license_count=license_count
    )


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Delete a product (admin only)"""
    product_service = ProductService(db)
    
    # Check if product has licenses
    license_count = await product_service.count_licenses(product_id)
    if license_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete product with {license_count} associated licenses"
        )
    
    success = await product_service.delete(product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return {"message": "Product deleted successfully"}


# ==================== Feature Management ====================

@router.get("/{product_id}/features", response_model=ProductFeaturesResponse)
async def get_product_features(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """Get all features for a product"""
    product_service = ProductService(db)
    product = await product_service.get_by_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Normalize features to FeatureDefinition objects
    features = []
    for f in (product.available_features or []):
        if isinstance(f, dict):
            features.append(FeatureDefinition(**f))
        elif isinstance(f, str):
            # Legacy string format - convert to object
            features.append(FeatureDefinition(slug=f, name=f.replace("_", " ").title()))
    
    return ProductFeaturesResponse(
        product_id=product.id,
        product_name=product.name,
        features=features
    )


@router.post("/{product_id}/features", response_model=ProductFeaturesResponse)
async def add_product_feature(
    product_id: int,
    feature: FeatureCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Add a new feature to a product (admin only)"""
    product_service = ProductService(db)
    product = await product_service.get_by_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Get current features and normalize
    current_features = []
    for f in (product.available_features or []):
        if isinstance(f, dict):
            current_features.append(f)
        elif isinstance(f, str):
            current_features.append({"slug": f, "name": f.replace("_", " ").title(), "description": None})
    
    # Check if feature already exists
    existing_slugs = [f["slug"] for f in current_features]
    if feature.slug in existing_slugs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Feature '{feature.slug}' already exists"
        )
    
    # Add new feature
    current_features.append({
        "slug": feature.slug,
        "name": feature.name,
        "description": feature.description
    })
    
    # Update product
    product.available_features = current_features
    await db.commit()
    await db.refresh(product)
    
    features = [FeatureDefinition(**f) for f in current_features]
    return ProductFeaturesResponse(
        product_id=product.id,
        product_name=product.name,
        features=features
    )


@router.put("/{product_id}/features/{feature_slug}", response_model=ProductFeaturesResponse)
async def update_product_feature(
    product_id: int,
    feature_slug: str,
    feature_update: FeatureUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Update a feature of a product (admin only)"""
    product_service = ProductService(db)
    product = await product_service.get_by_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Normalize and find feature
    current_features = []
    found = False
    for f in (product.available_features or []):
        if isinstance(f, dict):
            feature_dict = f.copy()
        elif isinstance(f, str):
            feature_dict = {"slug": f, "name": f.replace("_", " ").title(), "description": None}
        else:
            continue
        
        if feature_dict["slug"] == feature_slug:
            found = True
            if feature_update.name is not None:
                feature_dict["name"] = feature_update.name
            if feature_update.description is not None:
                feature_dict["description"] = feature_update.description
        
        current_features.append(feature_dict)
    
    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature '{feature_slug}' not found"
        )
    
    product.available_features = current_features
    await db.commit()
    await db.refresh(product)
    
    features = [FeatureDefinition(**f) for f in current_features]
    return ProductFeaturesResponse(
        product_id=product.id,
        product_name=product.name,
        features=features
    )


@router.delete("/{product_id}/features/{feature_slug}")
async def delete_product_feature(
    product_id: int,
    feature_slug: str,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Delete a feature from a product (admin only)"""
    product_service = ProductService(db)
    product = await product_service.get_by_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Find and remove feature
    current_features = []
    found = False
    for f in (product.available_features or []):
        slug = f["slug"] if isinstance(f, dict) else f
        if slug == feature_slug:
            found = True
            continue  # Skip this feature (delete it)
        
        if isinstance(f, dict):
            current_features.append(f)
        else:
            current_features.append({"slug": f, "name": f.replace("_", " ").title(), "description": None})
    
    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature '{feature_slug}' not found"
        )
    
    product.available_features = current_features
    await db.commit()
    
    return {"message": f"Feature '{feature_slug}' deleted successfully"}
