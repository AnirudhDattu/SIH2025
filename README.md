# Legal Metrology Compliance Checker - SIH 2025

An AI-powered system that automatically checks packaged food products for compliance with India's Legal Metrology Act (Packaged Commodities Rules, 2011). This solution was developed for Smart India Hackathon 2025.

## 🎯 Project Overview

This system automates the compliance checking process by:
1. **Web Scraping** product images from e-commerce URLs
2. **OCR Processing** using Google Document AI for text extraction
3. **AI Analysis** using Google Gemini for intelligent data extraction
4. **Compliance Validation** against Legal Metrology rules using RAG (Retrieval Augmented Generation)
5. **Database Management** with MongoDB for storing results

## 🏗️ System Architecture

```
Product URL → Web Scraper → MongoDB → OCR Processor → Gemini AI → Compliance Checker → Results
```

## 📂 Project Structure

```
SIH2025/
├── main.py                     # Main orchestration pipeline
├── requirements.txt            # Python dependencies
├── config.yaml                 # Configuration file (not tracked)
├── .env                        # Environment variables (not tracked)
│
├── scraper/                    # Web scraping module
│   ├── scrape_upload_data.py  # Selenium-based image scraper
│   └── object_ids.txt         # Generated MongoDB IDs log
│
├── ocr_data_extractor/        # OCR and data processing
│   ├── image_parser.py        # Google Document AI integration
│   ├── image_processor.py     # Image download and processing
│   ├── gemini_postprocess.py  # AI-powered data extraction
│   └── update_mongodb.py      # Database update operations
│
├── rag/                       # Compliance checking system
│   ├── rag.py                 # RAG-based compliance validator
│   ├── pdfs/                  # Legal Metrology Act documents
│   │   └── FInal-Book-Legal-Metrology-with-amendments.pdf
│   └── rules_chroma_store/    # Vector database for legal rules
│
└── temp/                      # Temporary processing files
    ├── ocr_output.txt         # Consolidated OCR results
    └── product_output.json    # Final processed data
```

## 🚀 Core Components

### 1. Web Scraper (`scraper/`)
- **Technology**: Selenium WebDriver with Chrome
- **Purpose**: Extracts product images from e-commerce websites
- **Features**: 
  - Headless browser automation
  - Dynamic content loading
  - Image URL extraction and validation
  - MongoDB integration for initial data storage

### 2. OCR Data Extractor (`ocr_data_extractor/`)
- **Technology**: Google Document AI (Document & Form Parser)
- **Purpose**: Converts product images to structured text data
- **Components**:
  - `image_parser.py`: Google Cloud Document AI integration
  - `image_processor.py`: Batch image processing pipeline
  - `gemini_postprocess.py`: AI-powered data extraction using Gemini
  - `update_mongodb.py`: Database operations for processed data

### 3. RAG Compliance Checker (`rag/`)
- **Technology**: LangChain + ChromaDB + BERT Reranker + Google Gemini
- **Purpose**: Validates products against Legal Metrology Act requirements
- **Features**:
  - Vector database of legal rules
  - Semantic search and retrieval
  - BERT-based document reranking
  - AI-powered compliance analysis

### 4. Main Pipeline (`main.py`)
- **Purpose**: Orchestrates the entire workflow
- **Process**:
  1. Reads product URL from config
  2. Scrapes images and stores in MongoDB
  3. Processes all images through OCR
  4. Extracts structured data using AI
  5. Updates database with processed information

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8+
- Google Cloud Project with Document AI API enabled
- MongoDB Atlas account
- Google Gemini API access
- Chrome/Chromium browser for Selenium

### 1. Clone Repository
```bash
git clone https://github.com/AnirudhDattu/SIH2025.git
cd SIH2025
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create `.env` file with:
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB=productdb
MONGODB_COLLECTION=products
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
```

### 4. Create Configuration File
Create `config.yaml`:
```yaml
url: "https://example-ecommerce-site.com/product/123"

# Google Cloud Document AI Configuration
project_id: "your-gcp-project-id"
location: "us"  # or your preferred region

# Document Parser Configuration
doc_processor_id: "your-document-processor-id"
doc_processor_version: "your-processor-version"

# Form Parser Configuration  
form_processor_id: "your-form-processor-id"
form_processor_version: "your-processor-version"

# Gemini Configuration
gemini_model: "gemini-2.5-flash"
gemini_api_key_env: "GEMINI_API_KEY"
```

### 5. Setup Google Cloud Credentials
- Create a Google Cloud service account
- Download the JSON key file
- Place it in your project directory
- Update the path in `.env` file

## 🚦 Usage

### Basic Usage
```bash
python main.py
```

### Step-by-Step Process
1. **Configure URL**: Update `config.yaml` with the product URL
2. **Run Pipeline**: Execute `main.py`
3. **Monitor Progress**: Check console output for each stage
4. **View Results**: Check `temp/product_output.json` for extracted data
5. **Database**: Processed data is automatically stored in MongoDB

### Individual Module Usage

#### Run Only Scraper
```python
from scraper.scrape_upload_data import run_pipeline
object_id = run_pipeline("https://example.com/product")
```

#### Run Only OCR Processing
```python
from ocr_data_extractor.image_processor import process_images_to_ocr
process_images_to_ocr("config.yaml", image_urls, "output.txt")
```

#### Run Only Compliance Check
```python
from rag.rag import main as run_compliance_check
run_compliance_check()
```

## 📊 Data Flow

### MongoDB Document Structure
```json
{
  "_id": "ObjectId",
  "product_title": "Product Name",
  "image_urls": ["url1", "url2"],
  "product_url": "source_url",
  "status": "ocr_uploaded",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "ocr_data": {
    "manufacturer": "Company Name",
    "manufacturer_address": "Address",
    "country_of_origin": "India",
    "common_product_name": "Biscuits",
    "net_quantity": "100g",
    "mrp": "Rs. 50",
    "unit_sale_price": "Rs. 45",
    "date_of_manufacture": "01/2024",
    "best_before": "12/2024",
    "raw_ocr_text": "Full OCR content..."
  },
  "compliance": {
    "score": "85%",
    "status": "non-compliant",
    "violations": [
      {
        "field": "manufacturer_address",
        "issue": "Address incomplete",
        "rule_reference": "Rule 6(1)",
        "reason": "Missing pin code"
      }
    ],
    "reasoning": "Detailed analysis...",
    "analysis_timestamp": "2024-01-01T00:00:00"
  }
}
```

## 🎯 Legal Metrology Compliance Checks

The system validates against these key requirements:

### Mandatory Information
- ✅ **Manufacturer Name and Address**
- ✅ **Common/Generic Name of Commodity**
- ✅ **Net Quantity** (weight, measure, or number)
- ✅ **Maximum Retail Price (MRP)**
- ✅ **Date of Manufacture/Packing**
- ✅ **Best Before/Use By Date**
- ✅ **Country of Origin** (for imported goods)

### Validation Rules
- **Net Quantity**: Must contain measurement units (g, kg, ml, l, etc.)
- **MRP**: Must contain currency symbols (₹, Rs, INR)
- **Address**: Must be complete with proper formatting
- **Dates**: Must follow standard date formats

## 🔧 Technical Features

### AI-Powered OCR
- **Google Document AI**: Industry-leading OCR accuracy
- **Form Parser**: Extracts key-value pairs from product labels
- **Table Parser**: Handles nutritional information tables

### Intelligent Data Extraction
- **Google Gemini**: Advanced language model for data interpretation
- **Structured Output**: Consistent JSON format generation
- **Error Handling**: Robust retry mechanisms and fallbacks

### Compliance Validation
- **Vector Database**: ChromaDB for efficient rule retrieval
- **Semantic Search**: Finds relevant legal provisions
- **BERT Reranking**: Improves search result relevance
- **AI Analysis**: Gemini-powered compliance assessment

### Web Scraping
- **Selenium Automation**: Handles dynamic content loading
- **Multi-image Support**: Extracts all product images
- **Error Recovery**: Handles common web scraping issues

## 🔒 Security & Privacy

- Environment variables for sensitive configuration
- Secure MongoDB connections with authentication
- Google Cloud IAM for API access control
- No sensitive data stored in repository
- Temporary file cleanup after processing

## 🐛 Troubleshooting

### Common Issues

#### OCR Processing Fails
```bash
# Check Google Cloud credentials
echo $GOOGLE_APPLICATION_CREDENTIALS
# Verify Document AI API is enabled
# Check processor IDs in config.yaml
```

#### MongoDB Connection Error
```bash
# Verify MongoDB URI in .env
# Check network connectivity
# Ensure database and collection exist
```

#### Gemini API Issues
```bash
# Verify API key in .env
# Check API quota and billing
# Review model name in config
```

#### Web Scraping Fails
```bash
# Check Chrome/Chromium installation
# Verify website accessibility
# Review URL format in config.yaml
```

## 📈 Performance Optimization

- **Batch Processing**: Multiple images processed together
- **Vector Caching**: Legal rules stored in persistent vector database
- **Connection Pooling**: Efficient database connections
- **Memory Management**: Temporary files cleaned automatically

## 🤝 Contributing

This repository follows standard Git workflow practices:

### Development Workflow
1. **Fork & Clone**: Create your local copy
2. **Branch**: Always work on feature branches
3. **Develop**: Make your changes with proper testing
4. **Test**: Verify your changes don't break existing functionality
5. **Pull Request**: Submit for review

### Branch Naming Convention
- `feature/description` - New features
- `fix/description` - Bug fixes  
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### Commit Guidelines
- Use clear, descriptive commit messages
- Follow conventional commit format
- Keep commits focused and atomic

## 📄 License & Legal

This project is developed for Smart India Hackathon 2025. The Legal Metrology compliance rules are based on the official Government of India regulations.

## 🆘 Support

For technical issues or questions:
1. Check the troubleshooting section above
2. Review error logs in console output
3. Verify all configuration files are properly set up
4. Create an issue in the repository with detailed error information

---

**Note**: This system is designed for educational and demonstration purposes as part of SIH 2025. For production use in regulatory compliance, additional validation and legal review may be required.