# Startup Data Manager - Technical Documentation

**Interview Assessment Guide**

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture & Components](#2-architecture--components)
3. [Implementation Details](#3-implementation-details)
4. [Configuration Guide](#4-configuration-guide)
5. [API Reference](#5-api-reference)
6. [Database Schema](#6-database-schema)
7. [Common Interview Questions](#7-common-interview-questions)

---

## 1. Project Overview

### What Was Built

A complete **Startup Company Data Manager** system consisting of:

- **AI-Powered Data Generation Script**: Generates realistic startup company data using Google Gemini API
- **REST API Backend**: FastAPI application with 11 endpoints for full CRUD operations
- **Database Layer**: SQLite database with proper relationships and constraints
- **Docker Deployment**: Containerized application ready for deployment

### Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend Framework | FastAPI | Latest |
| Database | SQLite | 3.x |
| ORM | SQLAlchemy | 2.x |
| Validation | Pydantic | 2.x |
| AI API | Google Gemini | gemini-flash-lite-latest |
| Containerization | Docker | Latest |
| Server | Uvicorn | Latest |

### Project Statistics

- **10 Companies**: 2 per industry across 5 industries
- **30-40 Products**: 3-4 products per company
- **11 API Endpoints**: Complete CRUD operations
- **2 Database Tables**: Companies and Products with foreign key relationship
- **5 Industries**: FinTech, HealthTech, EdTech, E-commerce, SaaS

---

## 2. Architecture & Components

### File Structure

```
startup-data-api/
├── generate_data.py       # AI data generation script
├── main.py               # FastAPI application
├── models.py             # SQLAlchemy database models
├── schemas.py            # Pydantic validation schemas
├── database.py           # Database configuration
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker image configuration
├── docker-compose.yml   # Docker orchestration
├── .env.example         # Environment template
├── .gitignore          # Git ignore rules
├── startup_data.json   # Generated company data
└── startup_data.db     # SQLite database
```

### Component Breakdown

#### 1. Data Generation Layer (`generate_data.py`)

**Location**: [generate_data.py](file:///e:/weedcode.io/startup-data-api/generate_data.py)

**Purpose**: Generate realistic startup company data using AI

**Key Features**:
- Gemini API integration with retry logic
- Exponential backoff for rate limiting
- Industry-based company generation
- JSON output format
- Progress tracking

**Why This Approach**:
- AI generates more realistic data than templates
- Retry logic ensures reliability
- JSON format is portable and easy to work with

#### 2. API Layer (`main.py`)

**Location**: [main.py](file:///e:/weedcode.io/startup-data-api/main.py)

**Purpose**: REST API with CRUD operations

**Key Features**:
- 11 RESTful endpoints
- Pagination support
- Idempotent data loading
- Cascade delete operations
- CORS middleware
- Auto-generated API documentation

**Why FastAPI**:
- High performance (async support)
- Automatic OpenAPI documentation
- Built-in data validation
- Type safety with Python type hints
- Easy to test and maintain

#### 3. Database Layer (`models.py`, `database.py`)

**Location**: 
- [models.py](file:///e:/weedcode.io/startup-data-api/models.py)
- [database.py](file:///e:/weedcode.io/startup-data-api/database.py)

**Purpose**: Data persistence and relationships

**Key Features**:
- SQLAlchemy ORM models
- One-to-many relationship (Company → Products)
- Cascade delete configuration
- Indexed columns for performance
- Timestamp tracking

**Why SQLite**:
- Zero configuration required
- Single file database (portable)
- Perfect for development and small deployments
- Easy to backup and share

**Why SQLAlchemy**:
- Database-agnostic (easy to switch to PostgreSQL)
- Pythonic query interface
- Automatic relationship management
- Migration support (Alembic compatible)

#### 4. Validation Layer (`schemas.py`)

**Location**: [schemas.py](file:///e:/weedcode.io/startup-data-api/schemas.py)

**Purpose**: Request/response validation and serialization

**Key Features**:
- Pydantic models for validation
- Type constraints (min/max lengths, value ranges)
- Literal types for enums
- Separate schemas for Create/Update/Response
- Automatic JSON serialization

**Why Pydantic**:
- Runtime type validation
- Clear error messages
- Automatic documentation generation
- JSON schema generation
- Performance optimized

#### 5. Containerization (`Dockerfile`, `docker-compose.yml`)

**Location**: 
- [Dockerfile](file:///e:/weedcode.io/startup-data-api/Dockerfile)
- [docker-compose.yml](file:///e:/weedcode.io/startup-data-api/docker-compose.yml)

**Purpose**: Easy deployment and environment consistency

**Key Features**:
- Multi-stage Docker build
- Non-root user for security
- Volume mounts for persistence
- Port mapping
- Health checks

---

## 3. Implementation Details

### Data Generation Process

**File**: `generate_data.py`

**Flow**:
1. Configure Gemini API with API key
2. Loop through 5 industries, generating 2 companies each
3. For each company:
   - Generate company details (name, tagline, description, etc.)
   - Generate 3-4 products with details
4. Implement retry logic with exponential backoff
5. Save all data to `startup_data.json`

**Retry Logic**:
```python
# Rate limit (429): Wait 30 seconds
# Other errors: Exponential backoff (1s, 2s, 4s)
# Max retries: 3 attempts
```

**Why This Matters**:
- Handles API rate limits gracefully
- Ensures data generation completes successfully
- Prevents data loss from transient errors

### API Implementation

**File**: `main.py`

#### Idempotent Data Loading

**Endpoint**: `POST /load-data`

**Implementation**:
```python
# Check if company exists (case-insensitive)
existing = db.query(Company).filter(
    func.lower(Company.name) == company_data["name"].lower()
).first()

if existing:
    skipped += 1
    continue
```

**Why This Matters**:
- Safe to run multiple times
- Prevents duplicate data
- Returns clear summary of what was loaded/skipped

#### Pagination

**Endpoint**: `GET /companies`

**Implementation**:
```python
skip = (page - 1) * page_size
companies = db.query(Company).offset(skip).limit(page_size).all()
```

**Why This Matters**:
- Efficient for large datasets
- Reduces memory usage
- Better API performance

#### Cascade Delete

**Implementation** (in `models.py`):
```python
products = relationship(
    "Product",
    back_populates="company",
    cascade="all, delete-orphan"
)
```

**Why This Matters**:
- Maintains referential integrity
- Automatic cleanup of related data
- Prevents orphaned records

### Database Design

**File**: `models.py`

#### Company Model

**Fields**:
- `id`: Primary key (auto-increment)
- `name`: Unique, indexed for fast lookups
- `industry`: Indexed for filtering
- `created_at`: Timestamp tracking

**Indexes**:
- Primary key on `id`
- Unique index on `name`
- Index on `industry` for filtering

#### Product Model

**Fields**:
- `id`: Primary key
- `company_id`: Foreign key to Company
- `created_at`: Timestamp tracking

**Relationships**:
- Many-to-one with Company
- Cascade delete from parent

**Why This Design**:
- Normalized structure (no data duplication)
- Fast queries with proper indexes
- Referential integrity enforced
- Easy to extend with more fields

### Validation Strategy

**File**: `schemas.py`

**Validation Rules**:

| Field | Validation |
|-------|-----------|
| Company name | 1-255 characters, required |
| Tagline | 1-100 characters, required |
| Industry | Must be one of 5 predefined values |
| Founded year | Between 2015-2024 |
| Employee count | Greater than 0 |
| Pricing model | Must be Free/Freemium/Subscription/Enterprise |

**Why This Matters**:
- Data quality assurance
- Clear error messages for clients
- Prevents invalid data in database
- Self-documenting API

---

## 4. Configuration Guide

### Changing the Gemini API Key

#### Option 1: Direct Code Edit (Current Implementation)

**File**: `generate_data.py`

**Line**: 11

**Current**:
```python
genai.configure(api_key="AIzaSyBpNfBJqWdIe8Hh6eDqTcBrFJLDvGiJMxU")
```

**To Change**:
```python
genai.configure(api_key="YOUR_NEW_API_KEY_HERE")
```

#### Option 2: Environment Variable (Recommended for Production)

**Step 1**: Create `.env` file in project root:
```bash
GEMINI_API_KEY=your_api_key_here
```

**Step 2**: Update `generate_data.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
```

**Step 3**: Add `python-dotenv` to `requirements.txt`:
```
python-dotenv==1.0.0
```

**Step 4**: Update `.gitignore` to exclude `.env`:
```
.env
```

### Changing the Gemini Model

**File**: `generate_data.py`

**Line**: 12

**Current**:
```python
model = genai.GenerativeModel("gemini-flash-lite-latest")
```

**Available Models**:
- `gemini-pro` - Most capable model
- `gemini-flash-lite-latest` - Fast and efficient (current)
- `gemini-1.5-pro` - Latest version with extended context
- `gemini-1.5-flash` - Fast with good quality

**To Change**:
```python
model = genai.GenerativeModel("gemini-pro")  # or any other model
```

**Considerations**:
- Different models have different rate limits
- Some models may be more expensive
- Response quality and speed vary
- Check Google AI Studio for latest models

### Docker Configuration

**File**: `docker-compose.yml`

**Port Mapping**:
```yaml
ports:
  - "8000:8000"  # Change left side to use different host port
```

**Volume Mounts**:
```yaml
volumes:
  - ./startup_data.json:/app/startup_data.json
  - ./startup_data.db:/app/startup_data.db
```

**Environment Variables** (add to docker-compose.yml):
```yaml
environment:
  - GEMINI_API_KEY=${GEMINI_API_KEY}
```

---

## 5. API Reference

### Complete Endpoint List

#### Company Endpoints

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/load-data` | Load data from JSON | None | `{loaded, skipped, total}` |
| GET | `/companies` | List companies (paginated) | Query: `page`, `page_size` | `{items[], total, page, page_size}` |
| GET | `/companies/{id}` | Get company with products | None | Company object with products[] |
| POST | `/companies` | Create new company | CompanyCreate schema | Company object |
| PUT | `/companies/{id}` | Update company | CompanyUpdate schema | Company object |
| DELETE | `/companies/{id}` | Delete company (cascade) | None | `{message}` |

#### Product Endpoints

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/products` | List all products | None | Product[] |
| GET | `/products/{id}` | Get product details | None | Product object |
| POST | `/products` | Create new product | ProductCreate schema | Product object |
| PUT | `/products/{id}` | Update product | ProductUpdate schema | Product object |
| DELETE | `/products/{id}` | Delete product | None | `{message}` |

### Example Requests

#### Load Data
```bash
curl -X POST http://localhost:8000/load-data
```

#### Get Companies (Paginated)
```bash
curl "http://localhost:8000/companies?page=1&page_size=5"
```

#### Create Company
```bash
curl -X POST http://localhost:8000/companies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "TechVision AI",
    "tagline": "AI-powered solutions",
    "description": "Detailed description...",
    "industry": "SaaS",
    "founded_year": 2023,
    "employee_count": 25,
    "headquarters": "Austin, USA",
    "website_url": "www.techvision.com"
  }'
```

---

## 6. Database Schema

### Entity Relationship Diagram

```
┌─────────────────────────────────┐
│          Company                │
├─────────────────────────────────┤
│ id (PK)                         │
│ name (UNIQUE, INDEXED)          │
│ tagline                         │
│ description                     │
│ industry (INDEXED)              │
│ founded_year                    │
│ employee_count                  │
│ headquarters                    │
│ website_url                     │
│ created_at                      │
└─────────────────────────────────┘
           │
           │ 1:N (cascade delete)
           │
           ▼
┌─────────────────────────────────┐
│          Product                │
├─────────────────────────────────┤
│ id (PK)                         │
│ company_id (FK, INDEXED)        │
│ name                            │
│ description                     │
│ target_audience                 │
│ key_features                    │
│ pricing_model                   │
│ created_at                      │
└─────────────────────────────────┘
```

### Relationship Details

- **Type**: One-to-Many (Company → Products)
- **Cascade**: Delete company → Delete all products
- **Constraint**: Product must have valid company_id
- **Indexing**: Foreign key is indexed for fast joins

---

## 7. Common Interview Questions

### Q1: Why did you choose FastAPI over Flask or Django?

**Answer**:
- **Performance**: FastAPI is built on Starlette and Pydantic, offering async support and high performance
- **Auto Documentation**: Automatic OpenAPI/Swagger documentation saves development time
- **Type Safety**: Built-in support for Python type hints catches errors early
- **Modern**: Designed for modern Python (3.7+) with async/await support
- **Validation**: Pydantic integration provides automatic request/response validation

### Q2: How does the cascade delete work?

**Answer**:
Implemented in the SQLAlchemy relationship configuration:
```python
products = relationship("Product", cascade="all, delete-orphan")
```

When a company is deleted:
1. SQLAlchemy detects the cascade configuration
2. Automatically deletes all related products
3. Maintains referential integrity
4. Happens in a single transaction (atomic)

### Q3: Why use pagination for the companies endpoint?

**Answer**:
- **Performance**: Loading all records at once is inefficient for large datasets
- **Memory**: Reduces server memory usage
- **Network**: Smaller response payloads
- **UX**: Better user experience with faster initial load
- **Scalability**: System can handle growth without performance degradation

### Q4: How do you prevent duplicate companies?

**Answer**:
Two-layer approach:
1. **Database Level**: Unique constraint on company name
2. **Application Level**: Case-insensitive check before insertion
```python
existing = db.query(Company).filter(
    func.lower(Company.name) == company_data["name"].lower()
).first()
```

This makes the `/load-data` endpoint idempotent.

### Q5: What are the scaling considerations?

**Answer**:
Current implementation is suitable for small to medium deployments. For scaling:

**Database**:
- Switch from SQLite to PostgreSQL for concurrent writes
- Add connection pooling
- Implement database replication

**API**:
- Deploy multiple instances behind a load balancer
- Add Redis for caching
- Implement rate limiting

**Data Generation**:
- Use background tasks (Celery)
- Implement batch processing
- Add job queue for large datasets

### Q6: How would you secure this API in production?

**Answer**:
- **Authentication**: Add JWT or OAuth2 authentication
- **Authorization**: Role-based access control (RBAC)
- **HTTPS**: Use TLS/SSL certificates
- **Rate Limiting**: Prevent abuse with rate limits
- **Input Validation**: Already implemented with Pydantic
- **SQL Injection**: Protected by SQLAlchemy ORM
- **Environment Variables**: Move API keys to environment variables
- **CORS**: Configure specific allowed origins (not "*")

### Q7: Why use Pydantic schemas instead of just SQLAlchemy models?

**Answer**:
- **Separation of Concerns**: API layer separate from database layer
- **Validation**: Runtime validation of incoming data
- **Documentation**: Auto-generates OpenAPI schemas
- **Flexibility**: Different schemas for Create/Update/Response
- **Security**: Control what fields are exposed in responses
- **Type Safety**: Better IDE support and type checking

### Q8: How does the retry logic work in data generation?

**Answer**:
Implements exponential backoff with special handling for rate limits:
```python
# Rate limit (429): Wait 30 seconds
# Other errors: Wait 2^attempt seconds (1s, 2s, 4s)
# Max retries: 3 attempts
```

This ensures:
- Graceful handling of temporary failures
- Respect for API rate limits
- Automatic recovery from transient errors

### Q9: What testing strategy would you implement?

**Answer**:
- **Unit Tests**: Test individual functions (pytest)
- **Integration Tests**: Test API endpoints (TestClient)
- **Database Tests**: Test with in-memory SQLite
- **Mocking**: Mock Gemini API calls for consistent tests
- **Coverage**: Aim for 80%+ code coverage
- **CI/CD**: Automated testing in GitHub Actions

### Q10: How would you monitor this in production?

**Answer**:
- **Logging**: Structured logging with log levels
- **Metrics**: Track API response times, error rates
- **Health Checks**: Endpoint for monitoring systems
- **APM**: Application Performance Monitoring (e.g., New Relic)
- **Alerts**: Set up alerts for errors and performance issues
- **Database Monitoring**: Track query performance and connections

---

## Summary

This project demonstrates:
- ✓ Full-stack development (data generation, API, database)
- ✓ AI integration with error handling
- ✓ RESTful API design best practices
- ✓ Database modeling and relationships
- ✓ Input validation and data quality
- ✓ Docker containerization
- ✓ Production-ready considerations

**Key Strengths**:
- Clean, maintainable code structure
- Comprehensive error handling
- Idempotent operations
- Auto-generated documentation
- Easy to deploy and configure
- Scalable architecture

---

**Created for Interview Assessment**  
**Tech Stack**: FastAPI, SQLAlchemy, Google Gemini API, Docker, SQLite
