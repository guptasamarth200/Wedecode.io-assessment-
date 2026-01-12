"""SQLAlchemy database models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base


class Company(Base):
    """Company model representing a startup company."""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    tagline = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    industry = Column(String(50), nullable=False, index=True)
    founded_year = Column(Integer, nullable=False)
    employee_count = Column(Integer, nullable=False)
    headquarters = Column(String(255), nullable=False)
    website_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship with cascade delete
    products = relationship(
        "Product",
        back_populates="company",
        cascade="all, delete-orphan"
    )


class Product(Base):
    """Product model representing a company's product."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    target_audience = Column(String(255), nullable=False)
    key_features = Column(Text, nullable=False)
    pricing_model = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship back to company
    company = relationship("Company", back_populates="products")
