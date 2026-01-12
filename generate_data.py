"""
Data generation script using Google Gemini API.
Generates 10 startup companies across 5 industries with 3-4 products each.
"""
import json
import time
import os
from typing import Dict, List, Any
import google.generativeai as genai

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyAoVYswbU_7yNJzeIxqbdhdWN3daTrtzpw"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model (using current supported model)
model = genai.GenerativeModel("gemini-flash-lite-latest")


# Industries and their counts
INDUSTRIES = ["FinTech", "HealthTech", "EdTech", "E-commerce", "SaaS"]
COMPANIES_PER_INDUSTRY = 2
TOTAL_COMPANIES = 10


def retry_with_backoff(func, max_retries=3):
    """
    Retry a function with intelligent backoff handling.
    - Rate limit errors (429): Wait 30 seconds and retry
    - Other errors: Exponential backoff (1s, 2s, 4s)
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        
    Returns:
        Result of the function call
        
    Raises:
        Exception: If all retries fail with non-rate-limit errors
    """
    attempt = 0
    while attempt < max_retries:
        try:
            return func()
        except Exception as e:
            error_message = str(e)
            
            # Check if it's a rate limit error (429 or quota exceeded)
            is_rate_limit = (
                "429" in error_message or 
                "quota" in error_message.lower() or
                "rate limit" in error_message.lower() or
                "resource exhausted" in error_message.lower()
            )
            
            if is_rate_limit:
                # Rate limit error - wait longer
                wait_time = 30
                print(f"  ⚠️  Rate limit hit (attempt {attempt + 1}): {error_message[:100]}")
                print(f"  ⏳ Waiting {wait_time} seconds for rate limit to reset...")
                time.sleep(wait_time)
                attempt += 1
                # Don't count rate limits against max_retries - keep trying
                if attempt >= max_retries:
                    # Give it one more chance after rate limit
                    print(f"  🔄 Retrying after rate limit cooldown...")
                    attempt = max_retries - 1
            else:
                # Regular error - exponential backoff
                if attempt == max_retries - 1:
                    raise e
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                print(f"  ⚠️  Attempt {attempt + 1} failed: {error_message[:100]}")
                print(f"  ⏳ Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                attempt += 1


def generate_company_data(industry: str, company_number: int) -> Dict[str, Any]:
    """
    Generate a single company with products using Gemini API.
    
    Args:
        industry: Industry category
        company_number: Company number for progress tracking
        
    Returns:
        Dictionary containing company data with nested products
    """
    print(f"\n{'='*60}")
    print(f"Generating company {company_number}/{TOTAL_COMPANIES}")
    print(f"Industry: {industry}")
    print(f"{'='*60}")
    
    # Generate company information
    company_prompt = f"""Generate a realistic startup company in the {industry} industry.

Requirements:
- Creative and professional company name (not generic like "TechCorp1")
- Compelling tagline under 100 characters
- Detailed description (2-3 well-written paragraphs) explaining what the company does, its value proposition, and market position
- Founded year between 2015-2024
- Realistic employee count (10-500 for startups)
- Headquarters as "City, Country" format
- Professional website URL

Return ONLY a valid JSON object with this exact structure:
{{
  "name": "Company Name",
  "tagline": "Compelling tagline under 100 chars",
  "description": "Multi-paragraph description...",
  "industry": "{industry}",
  "founded_year": 2021,
  "employee_count": 45,
  "headquarters": "San Francisco, USA",
  "website_url": "www.example.com"
}}

Make it sound professional and realistic, not generic."""

    def generate_company():
        response = model.generate_content(company_prompt)
        return response.text
    
    company_json = retry_with_backoff(generate_company)
    
    # Parse company JSON
    try:
        # Extract JSON from markdown code blocks if present
        if "```json" in company_json:
            company_json = company_json.split("```json")[1].split("```")[0].strip()
        elif "```" in company_json:
            company_json = company_json.split("```")[1].split("```")[0].strip()
        
        company_data = json.loads(company_json)
        print(f"✅ Company generated: {company_data['name']}")
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse company JSON: {e}")
        print(f"Raw response: {company_json[:200]}...")
        raise
    
    # Wait before generating products
    time.sleep(1)
    
    # Generate products for this company
    products_prompt = f"""Generate 3 realistic products for a company named "{company_data['name']}" in the {industry} industry.

Requirements for each product:
- Creative and relevant product name
- Detailed description (2-3 sentences) explaining what it does
- Specific target audience (be precise, not generic)
- 4-6 key features as bullet points (specific and valuable features, not generic)
- Appropriate pricing model: "Free", "Freemium", "Subscription", or "Enterprise"

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "name": "Product Name",
    "description": "Detailed description of what the product does and its benefits...",
    "target_audience": "Specific target audience description",
    "key_features": "• Feature 1\\n• Feature 2\\n• Feature 3\\n• Feature 4\\n• Feature 5",
    "pricing_model": "Subscription"
  }}
]

Make features specific and valuable, not generic. Use \\n for newlines in key_features."""

    def generate_products():
        response = model.generate_content(products_prompt)
        return response.text
    
    products_json = retry_with_backoff(generate_products)
    
    # Parse products JSON
    try:
        # Extract JSON from markdown code blocks if present
        if "```json" in products_json:
            products_json = products_json.split("```json")[1].split("```")[0].strip()
        elif "```" in products_json:
            products_json = products_json.split("```")[1].split("```")[0].strip()
        
        products_data = json.loads(products_json)
        print(f"✅ Generated {len(products_data)} products")
        for i, product in enumerate(products_data, 1):
            print(f"   {i}. {product['name']}")
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse products JSON: {e}")
        print(f"Raw response: {products_json[:200]}...")
        raise
    
    # Combine company and products
    company_data["products"] = products_data
    
    return company_data


def main():
    """Main function to generate all company data."""
    print("\n" + "="*60)
    print("🚀 STARTUP COMPANY DATA GENERATOR")
    print("="*60)
    print(f"📊 Generating {TOTAL_COMPANIES} companies across {len(INDUSTRIES)} industries")
    print(f"🏭 Industries: {', '.join(INDUSTRIES)}")
    print("="*60)
    
    all_companies = []
    company_counter = 1
    
    # Generate companies for each industry
    for industry in INDUSTRIES:
        for i in range(COMPANIES_PER_INDUSTRY):
            try:
                company_data = generate_company_data(industry, company_counter)
                all_companies.append(company_data)
                company_counter += 1
                
                # Rate limiting: wait 1 second between companies
                if company_counter <= TOTAL_COMPANIES:
                    time.sleep(1)
                    
            except Exception as e:
                print(f"\n❌ ERROR: Failed to generate company {company_counter}")
                print(f"Error: {str(e)}")
                print("Stopping generation...")
                break
    
    # Save to JSON file
    output_data = {"companies": all_companies}
    
    try:
        with open("startup_data.json", "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*60)
        print("✅ SUCCESS!")
        print("="*60)
        print(f"📁 Generated {len(all_companies)} companies")
        print(f"💾 Saved to: startup_data.json")
        print(f"📦 Total products: {sum(len(c['products']) for c in all_companies)}")
        print("="*60)
        
        # Summary by industry
        print("\n📊 Summary by Industry:")
        for industry in INDUSTRIES:
            count = sum(1 for c in all_companies if c['industry'] == industry)
            print(f"   • {industry}: {count} companies")
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to save JSON file")
        print(f"Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
