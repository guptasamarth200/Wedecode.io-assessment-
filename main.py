"""FastAPI application with complete CRUD operations for companies and products."""
import json
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import engine, get_db, Base
from models import Company, Product
from schemas import (
    CompanyCreate, CompanyUpdate, CompanyResponse, CompanyWithProducts,
    ProductCreate, ProductUpdate, ProductResponse,
    PaginatedResponse, LoadDataResponse
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Startup Company Data Manager API",
    description="REST API for managing startup companies and their products",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== COMPANY ENDPOINTS ====================

@app.post("/load-data", response_model=LoadDataResponse, status_code=status.HTTP_200_OK)
def load_data_from_json(db: Session = Depends(get_db)):
    """
    Load data from startup_data.json into the database.
    Prevents duplicates by checking company names (case-insensitive).
    Returns summary of loaded, skipped, and total companies.
    """
    try:
        with open("startup_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="startup_data.json file not found"
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON format in startup_data.json"
        )

    companies_data = data.get("companies", [])
    loaded_count = 0
    skipped_count = 0
    total_count = len(companies_data)

    for company_data in companies_data:
        # Check if company already exists (case-insensitive)
        existing_company = db.query(Company).filter(
            func.lower(Company.name) == func.lower(company_data["name"])
        ).first()

        if existing_company:
            skipped_count += 1
            continue

        # Extract products from company data
        products_data = company_data.pop("products", [])

        # Create company
        company = Company(**company_data)
        db.add(company)
        db.flush()  # Get the company ID

        # Create products for this company
        for product_data in products_data:
            product = Product(company_id=company.id, **product_data)
            db.add(product)

        loaded_count += 1

    db.commit()

    return LoadDataResponse(
        loaded=loaded_count,
        skipped=skipped_count,
        total=total_count
    )


@app.get("/companies", response_model=PaginatedResponse, status_code=status.HTTP_200_OK)
def get_companies(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get all companies with pagination.
    Default: 10 companies per page.
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page number must be >= 1"
        )
    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page size must be between 1 and 100"
        )

    # Get total count
    total = db.query(Company).count()

    # Get paginated results
    skip = (page - 1) * page_size
    companies = db.query(Company).offset(skip).limit(page_size).all()

    return PaginatedResponse(
        items=companies,
        total=total,
        page=page,
        page_size=page_size
    )


@app.get("/companies/{company_id}", response_model=CompanyWithProducts, status_code=status.HTTP_200_OK)
def get_company(company_id: int, db: Session = Depends(get_db)):
    """
    Get a specific company by ID with all nested products.
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} not found"
        )
    return company


@app.post("/companies", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    """
    Create a new company.
    """
    # Check if company name already exists
    existing = db.query(Company).filter(
        func.lower(Company.name) == func.lower(company.name)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company with name '{company.name}' already exists"
        )

    db_company = Company(**company.model_dump())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


@app.put("/companies/{company_id}", response_model=CompanyResponse, status_code=status.HTTP_200_OK)
def update_company(
    company_id: int,
    company: CompanyUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing company.
    """
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if not db_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} not found"
        )

    # Check if new name conflicts with existing company
    if company.name != db_company.name:
        existing = db.query(Company).filter(
            func.lower(Company.name) == func.lower(company.name)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Company with name '{company.name}' already exists"
            )

    # Update fields
    for key, value in company.model_dump().items():
        setattr(db_company, key, value)

    db.commit()
    db.refresh(db_company)
    return db_company


@app.delete("/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    """
    Delete a company and all its products (cascade delete).
    """
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if not db_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} not found"
        )

    db.delete(db_company)
    db.commit()
    return None


# ==================== PRODUCT ENDPOINTS ====================

@app.get("/products", response_model=List[ProductResponse], status_code=status.HTTP_200_OK)
def get_products(db: Session = Depends(get_db)):
    """
    Get all products.
    """
    products = db.query(Product).all()
    return products


@app.get("/products/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get a specific product by ID.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    return product


@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Create a new product.
    Validates that the company_id exists.
    """
    # Validate company exists
    company = db.query(Company).filter(Company.id == product.company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company with id {product.company_id} does not exist"
        )

    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.put("/products/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing product.
    """
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )

    # Update fields
    for key, value in product.model_dump().items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Delete a product.
    """
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )

    db.delete(db_product)
    db.commit()
    return None


# ==================== ROOT ENDPOINT ====================

@app.get("/", status_code=status.HTTP_200_OK)
def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Startup Company Data Manager API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "companies": "/companies",
            "products": "/products",
            "load_data": "/load-data"
        }
    }
