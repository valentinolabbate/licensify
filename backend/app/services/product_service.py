"""
Product Service - Business logic for product management
"""
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import re

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from name"""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug


class ProductService:
    """Service for product operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, product_data: ProductCreate) -> Product:
        """Create a new product"""
        # Generate slug if not provided
        slug = product_data.slug or generate_slug(product_data.name)
        
        # Ensure unique slug
        existing = await self.get_by_slug(slug)
        if existing:
            # Append number to make unique
            counter = 1
            while await self.get_by_slug(f"{slug}-{counter}"):
                counter += 1
            slug = f"{slug}-{counter}"
        
        product = Product(
            name=product_data.name,
            slug=slug,
            description=product_data.description,
            version=product_data.version,
            available_features=product_data.available_features,
            default_max_devices=product_data.default_max_devices,
            default_license_type=product_data.default_license_type,
        )
        
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        
        return product
    
    async def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        result = await self.db.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_slug(self, slug: str) -> Optional[Product]:
        """Get product by slug"""
        result = await self.db.execute(
            select(Product).where(Product.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False
    ) -> tuple[List[Product], int]:
        """Get all products"""
        query = select(Product)
        count_query = select(func.count(Product.id))
        
        if not include_inactive:
            query = query.where(Product.is_active == True)
            count_query = count_query.where(Product.is_active == True)
        
        result = await self.db.execute(
            query.order_by(Product.name)
            .offset(skip)
            .limit(limit)
        )
        products = result.scalars().all()
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        return products, total
    
    async def update(self, product: Product, product_data: ProductUpdate) -> Product:
        """Update a product"""
        update_data = product_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(product, field, value)
        
        await self.db.commit()
        await self.db.refresh(product)
        
        return product
    
    async def delete(self, product_id: int) -> bool:
        """Delete a product"""
        product = await self.get_by_id(product_id)
        if not product:
            return False
        
        await self.db.delete(product)
        await self.db.commit()
        return True
    
    async def count_licenses(self, product_id: int) -> int:
        """Count licenses for a product"""
        from app.models.license import License
        result = await self.db.execute(
            select(func.count(License.id)).where(License.product_id == product_id)
        )
        return result.scalar() or 0
