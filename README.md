# Startup Company Data Manager

A complete REST API system for managing startup company data with AI-generated content using Google Gemini API. This project includes data generation, FastAPI backend with full CRUD operations, and Docker deployment.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate company data
python generate_data.py

# 3. Run the API server
uvicorn main:app --reload

# 4. Open browser and load data
# Visit: http://localhost:8000/docs
# Execute: POST /load-data
```

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Local Setup](#local-setup)
- [Running with Docker](#running-with-docker)
- [API Documentation](#api-documentation)
- [API Endpoints](#api-endpoints)
- [Testing the API](#testing-the-api)
- [Troubleshooting](#troubleshooting)

---

## Features

- **AI-Powered Data Generation**: Uses Google Gemini API to generate realistic startup company data
- **10 Companies**: 2 companies per industry across 5 industries (FinTech, HealthTech, EdTech, E-commerce, SaaS)
- **3-4 Products per Company**: Each company has multiple realistic products
- **Complete REST API**: 11 endpoints with full CRUD operations
- **SQLite Database**: Lightweight database with proper relationships
- **Pagination Support**: Efficient data retrieval with pagination
- **Duplicate Prevention**: Idempotent data loading
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Interactive API Docs**: Swagger UI for testing endpoints

---

## Prerequisites

- **Python 3.10+** (for local development)
- **Docker & Docker Compose** (for containerized deployment)
- **Google Gemini API Key** (configured in generate_data.py)

---

## Project Structure

```
startup-data-api/
├── generate_data.py          # Data generation script using Gemini API
├── startup_data.json          # Generated company data (created after running script)
├── main.py                    # FastAPI application with all endpoints
├── models.py                  # SQLAlchemy database models
├── schemas.py                 # Pydantic validation schemas
├── database.py                # Database configuration
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── Dockerfile                # Docker image configuration
├── docker-compose.yml        # Docker Compose orchestration
├── PROJECT_DOCUMENTATION.md  # Detailed technical documentation
└── README.md                 # This file
```

---

## Configuration

### Changing the Gemini API Key

#### Method 1: Direct Edit (Current)

Open `generate_data.py` and modify line 11:

```python
genai.configure(api_key="YOUR_NEW_API_KEY_HERE")
```

#### Method 2: Environment Variable (Recommended)

1. Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_api_key_here
```

2. Update `generate_data.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
```

3. Add `python-dotenv` to `requirements.txt`:
```
python-dotenv==1.0.0
```

4. Install the new dependency:
```bash
pip install python-dotenv
```

### Changing the Gemini Model

Open `generate_data.py` and modify line 12:

```python
model = genai.GenerativeModel("gemini-pro")  # or any other model
```

**Available Models**:
- `gemini-pro` - Most capable model
- `gemini-flash-lite-latest` - Fast and efficient (current)
- `gemini-1.5-pro` - Latest version with extended context
- `gemini-1.5-flash` - Fast with good quality

**Note**: Different models have different rate limits and pricing. Check Google AI Studio for the latest available models.

---

## Local Setup

### Step 1: Clone or Navigate to Project

```bash
cd startup-data-api
```

### Step 2: Create Virtual Environment (Recommended)

**Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux**:
```bash
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Generate Company Data

Run the data generation script to create `startup_data.json`:

```bash
python generate_data.py
```

**Expected Output**:
- Progress indicators showing "Generating company X/10"
- Company and product names as they're generated
- Final summary with total companies and products
- Creates `startup_data.json` file

**Note**: The script includes retry logic with exponential backoff. If API calls fail, it will automatically retry up to 3 times.

### Step 5: Run the FastAPI Application

```bash
uvicorn main:app --reload
```

The API will be available at: **http://localhost:8000**

### Step 6: Load Data into Database

1. Open your browser and go to: **http://localhost:8000/docs**
2. Execute the `POST /load-data` endpoint to load the generated data into the database

---

## Running with Docker

### Step 1: Ensure startup_data.json Exists

First, generate the data if you haven't already:

```bash
python generate_data.py
```

### Step 2: Build and Run with Docker Compose

```bash
docker-compose up -d
```

This command will:
- Build the Docker image
- Start the container in detached mode
- Mount volumes for database and JSON file persistence
- Expose the API on port 8000

### Step 3: View Logs

```bash
docker-compose logs -f
```

### Step 4: Stop the Container

```bash
docker-compose down
```

### Step 5: Rebuild After Code Changes

```bash
docker-compose up -d --build
```

---

## API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## API Endpoints

### Company Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/load-data` | Load data from startup_data.json (idempotent) |
| GET | `/companies` | List all companies with pagination |
| GET | `/companies/{id}` | Get company details with nested products |
| POST | `/companies` | Create new company |
| PUT | `/companies/{id}` | Update company |
| DELETE | `/companies/{id}` | Delete company (cascade deletes products) |

### Product Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products` | List all products |
| GET | `/products/{id}` | Get product details |
| POST | `/products` | Create new product |
| PUT | `/products/{id}` | Update product |
| DELETE | `/products/{id}` | Delete product |

---

## Testing the API

### Example 1: Load Data

```bash
curl -X POST "http://localhost:8000/load-data"
```

**Response**:
```json
{
  "loaded": 10,
  "skipped": 0,
  "total": 10
}
```

### Example 2: Get All Companies (Paginated)

```bash
curl "http://localhost:8000/companies?page=1&page_size=5"
```

### Example 3: Get Company with Products

```bash
curl "http://localhost:8000/companies/1"
```

### Example 4: Create New Company

```bash
curl -X POST "http://localhost:8000/companies" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "TechVision AI",
    "tagline": "AI-powered solutions for modern businesses",
    "description": "TechVision AI is revolutionizing how businesses leverage artificial intelligence...",
    "industry": "SaaS",
    "founded_year": 2023,
    "employee_count": 25,
    "headquarters": "Austin, USA",
    "website_url": "www.techvisionai.com"
  }'
```

### Example 5: Create New Product

```bash
curl -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "name": "AI Assistant Pro",
    "description": "Advanced AI assistant for business automation",
    "target_audience": "Enterprise teams",
    "key_features": "• Natural language processing\n• Task automation\n• Integration with popular tools",
    "pricing_model": "Subscription"
  }'
```

### Example 6: Update Company

```bash
curl -X PUT "http://localhost:8000/companies/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Company Name",
    "tagline": "New tagline",
    "description": "Updated description...",
    "industry": "FinTech",
    "founded_year": 2020,
    "employee_count": 100,
    "headquarters": "New York, USA",
    "website_url": "www.updated.com"
  }'
```

### Example 7: Delete Company (Cascade Delete)

```bash
curl -X DELETE "http://localhost:8000/companies/1"
```

### Example 8: Get All Products

```bash
curl "http://localhost:8000/products"
```

---

## Troubleshooting

### Issue: "startup_data.json file not found"

**Solution**: Run the data generation script first:
```bash
python generate_data.py
```

### Issue: "Module not found" errors

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Gemini API rate limit errors

**Solution**: The script includes automatic retry logic with exponential backoff. If you still encounter issues:
- Wait a few minutes between runs
- The script includes 1-second delays between API calls
- Consider switching to a different model with higher rate limits

### Issue: Docker container won't start

**Solution**: Check logs:
```bash
docker-compose logs -f
```

Common fixes:
- Ensure port 8000 is not already in use
- Verify `startup_data.json` exists before running Docker
- Rebuild the image: `docker-compose up -d --build`

### Issue: Database is empty after running /load-data

**Solution**: 
- Check that `startup_data.json` exists and contains data
- Verify the file is in the same directory as `main.py`
- Check API response for errors in the Swagger UI

### Issue: "Company already exists" when loading data

**Solution**: This is expected behavior. The `/load-data` endpoint is idempotent and skips existing companies. The response will show:
```json
{
  "loaded": 0,
  "skipped": 10,
  "total": 10
}
```

### Issue: Cascade delete not working

**Solution**: The cascade delete is configured in the SQLAlchemy models. Ensure you're using the DELETE endpoint for companies, not manually deleting from the database.

---

## Data Quality Notes

The generated data is designed to be:
- **Realistic**: Company names, descriptions, and products sound professional
- **Diverse**: Covers 5 different industries with varied business models
- **Detailed**: 2-3 paragraph descriptions, specific features, clear target audiences
- **Consistent**: Proper formatting, valid data types, realistic metrics

---

## Security Notes

- The Gemini API key is currently hardcoded for evaluation purposes
- In production, use environment variables (`.env` file)
- Docker container runs as non-root user for security
- Database uses SQLite for simplicity (consider PostgreSQL for production)

---

## Additional Documentation

For detailed technical documentation, architecture decisions, and interview preparation, see:
- **[PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)** - Comprehensive technical guide

---

## License

This project is created as a technical assignment for evaluation purposes.

---

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review the API documentation at `/docs`
3. Check Docker logs: `docker-compose logs -f`
4. See PROJECT_DOCUMENTATION.md for detailed explanations

---

**Built with**: FastAPI, SQLAlchemy, Google Gemini API, Docker, SQLite
