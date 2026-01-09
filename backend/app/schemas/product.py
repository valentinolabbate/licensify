"""
Product Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel, Field
import re


def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from name"""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug


class FeatureDefinition(BaseModel):
    """Schema for a feature definition with metadata"""
    slug: str = Field(..., min_length=1, max_length=100, description="Unique feature identifier")
    name: str = Field(..., min_length=1, max_length=255, description="Display name")
    description: Optional[str] = Field(default=None, description="Feature description")
    
    class Config:
        from_attributes = True


class FeatureCreate(BaseModel):
    """Schema for creating a new feature"""
    slug: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class FeatureUpdate(BaseModel):
    """Schema for updating a feature"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None


class ProductBase(BaseModel):
    """Base product schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    version: Optional[str] = None
    available_features: List[Union[str, FeatureDefinition]] = []
    default_max_devices: int = Field(default=1, ge=0)
    default_license_type: str = "limited"


class ProductCreate(ProductBase):
    """Schema for product creation"""
    slug: Optional[str] = None  # Auto-generated if not provided


class ProductUpdate(BaseModel):
    """Schema for product update"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    version: Optional[str] = None
    available_features: Optional[List[Union[str, FeatureDefinition]]] = None
    default_max_devices: Optional[int] = Field(default=None, ge=0)
    default_license_type: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Schema for product response"""
    id: int
    slug: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    license_count: int = 0
    
    class Config:
        from_attributes = True


class ProductFeaturesResponse(BaseModel):
    """Schema for product features response"""
    product_id: int
    product_name: str
    features: List[FeatureDefinition]


class ProductListResponse(BaseModel):
    """Schema for product list response"""
    products: List[ProductResponse]
    total: int


class ProductSimple(BaseModel):
    """Simple product info for license responses"""
    id: int
    name: str
    slug: str
    version: Optional[str] = None
    
    class Config:
        from_attributes = True
