"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


# Product Schemas
class ProductBase(BaseModel):
    """Base product schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    target_audience: str = Field(..., min_length=1, max_length=255)
    key_features: str = Field(..., min_length=1)
    pricing_model: Literal["Free", "Freemium", "Subscription", "Enterprise"]


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    company_id: int = Field(..., gt=0)


class ProductUpdate(ProductBase):
    """Schema for updating a product."""
    pass


class ProductResponse(ProductBase):
    """Schema for product response."""
    id: int
    company_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Company Schemas
class CompanyBase(BaseModel):
    """Base company schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    tagline: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    industry: Literal["FinTech", "HealthTech", "EdTech", "E-commerce", "SaaS"]
    founded_year: int = Field(..., ge=2015, le=2024)
    employee_count: int = Field(..., gt=0)
    headquarters: str = Field(..., min_length=1, max_length=255)
    website_url: Optional[str] = Field(None, max_length=255)


class CompanyCreate(CompanyBase):
    """Schema for creating a company."""
    pass


class CompanyUpdate(CompanyBase):
    """Schema for updating a company."""
    pass


class CompanyResponse(CompanyBase):
    """Schema for company response without products."""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanyWithProducts(CompanyResponse):
    """Schema for company response with nested products."""
    products: List[ProductResponse] = []

    model_config = ConfigDict(from_attributes=True)


# Pagination Schema
class PaginatedResponse(BaseModel):
    """Generic paginated response schema."""
    items: List[CompanyResponse]
    total: int
    page: int
    page_size: int


# Load Data Response Schema
class LoadDataResponse(BaseModel):
    """Schema for load-data endpoint response."""
    loaded: int
    skipped: int
    total: int
