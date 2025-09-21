# Contributing to Legal Metrology Compliance Checker

> **Note**: For project overview, setup instructions, and technical details, see the main [README.md](README.md). This document contains detailed guidelines for contributing to this Smart India Hackathon 2025 project.

Thank you for your interest in contributing! This AI-powered compliance checker helps automate Legal Metrology Act validation for packaged food products. Your contributions can help improve accuracy, add features, and enhance the system's capabilities.

## 📋 Table of Contents

1. [Repository Access](#1-repository-access)
2. [Development Environment Setup](#2-development-environment-setup)
3. [Project Structure Understanding](#3-project-structure-understanding)
4. [Development Workflow](#4-development-workflow)
5. [Code Standards](#5-code-standards)
6. [Testing Guidelines](#6-testing-guidelines)
7. [Documentation Requirements](#7-documentation-requirements)
8. [Pull Request Process](#8-pull-request-process)
9. [Issue Reporting](#9-issue-reporting)
10. [Getting Help](#10-getting-help)

## 1. Repository Access

- This repository is **private** and access has already been granted to you.
- Make sure you are signed into GitHub with the account that has been given access.

---

## 2. Development Environment Setup

### Initial Setup
Run these commands once to clone the repository and set up your local workspace:

```bash
# Clone the repository to your system
git clone https://github.com/AnirudhDattu/SIH2025.git

# Move into the project folder
cd SIH2025

# Verify remote configuration
git remote -v

# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file from template
cp .env.example .env  # If template exists, otherwise create manually

# Create configuration file
cp config.yaml.example config.yaml  # If template exists, otherwise create manually
```

### Required API Keys and Services
Before you can run the system, you'll need:

1. **Google Cloud Project** with Document AI API enabled
   ```bash
   # Enable required APIs
   gcloud services enable documentai.googleapis.com
   gcloud services enable storage-component.googleapis.com
   ```

2. **Google Gemini API Key**
   - Get from [Google AI Studio](https://aistudio.google.com/)
   - Add to `.env` as `GEMINI_API_KEY=your_key_here`

3. **MongoDB Atlas Connection**
   - Create cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Add connection string to `.env` as `MONGODB_URI=mongodb+srv://...`

4. **Google Cloud Service Account**
   - Download JSON key file
   - Set `GOOGLE_APPLICATION_CREDENTIALS` path in `.env`

### Verify Installation
```bash
# Test basic imports
python -c "import main; print('✅ Main module imports successfully')"

# Test database connection
python -c "from scraper.scrape_upload_data import get_mongo_collection; get_mongo_collection(); print('✅ MongoDB connection works')"

# Test Google Cloud credentials
python -c "from google.cloud import documentai; print('✅ Google Cloud SDK ready')"

# Check Chrome/Chromium for Selenium
google-chrome --version || chromium --version
```

---

## 3. Project Structure Understanding

Before making changes, familiarize yourself with the codebase structure:

```
SIH2025/
├── main.py                     # 🎯 Main orchestration pipeline
├── requirements.txt            # 📦 Python dependencies
├── .env                        # 🔐 Environment variables (not tracked)
├── config.yaml                 # ⚙️ Configuration file (not tracked)
│
├── scraper/                    # 🌐 Web scraping module
│   ├── __init__.py
│   ├── scrape_upload_data.py  # Selenium-based image extraction
│   └── object_ids.txt         # MongoDB object IDs log
│
├── ocr_data_extractor/        # 👁️ OCR and data processing
│   ├── __init__.py
│   ├── image_parser.py        # Google Document AI integration
│   ├── image_processor.py     # Image download and batch processing
│   ├── gemini_postprocess.py  # AI-powered data extraction
│   └── update_mongodb.py      # Database update operations
│
├── rag/                       # ⚖️ Compliance checking system
│   ├── rag.py                 # RAG-based compliance validator
│   ├── pdfs/                  # Legal Metrology Act documents
│   │   └── Final-Book-Legal-Metrology-with-amendments.pdf
│   └── rules_chroma_store/    # Vector database for legal rules
│
└── temp/                      # 📁 Temporary processing files (auto-created)
    ├── ocr_output.txt         # Consolidated OCR results
    └── product_output.json    # Final processed data
```

### Module Responsibilities

- **`main.py`**: Orchestrates the complete pipeline, handles configuration, and manages the workflow
- **`scraper/`**: Web scraping using Selenium, image URL extraction, initial MongoDB storage
- **`ocr_data_extractor/`**: Google Document AI integration, Gemini AI processing, data extraction
- **`rag/`**: Legal rule vector database, compliance checking, violation detection

### Key Data Flow
1. `main.py` → `scraper` → Extract image URLs from product page
2. `main.py` → `ocr_data_extractor` → Process images via Google Document AI
3. `main.py` → `ocr_data_extractor` → Extract structured data using Gemini AI
4. `main.py` → `rag` → Validate against Legal Metrology rules
5. `main.py` → MongoDB → Store final results with compliance analysis

---

## 4. Development Workflow

### Creating and Working on a Branch

Always work on a **separate branch** instead of `main`. This keeps the main branch stable.

```bash
# Fetch latest changes from main branch
git pull origin main

# Create and switch to a new branch
git checkout -b your-feature-branch-name

# Alternative: Create branch and switch in one command
git switch -c your-feature-branch-name
```

### Branch Naming Conventions
Use descriptive names with prefixes to indicate the type of change:

- **`feature/`**: New features or enhancements
  - `feature/add-flipkart-scraper`
  - `feature/nutrition-table-parser`
  - `feature/batch-processing`

- **`fix/`**: Bug fixes
  - `fix/selenium-timeout-issue`
  - `fix/gemini-api-retry-logic`
  - `fix/mongodb-connection-error`

- **`docs/`**: Documentation updates
  - `docs/update-setup-guide`
  - `docs/add-api-examples`
  - `docs/contributing-guidelines`

- **`refactor/`**: Code refactoring without changing functionality
  - `refactor/ocr-module-structure`
  - `refactor/error-handling`
  - `refactor/config-management`

- **`test/`**: Adding or updating tests
  - `test/add-unit-tests-scraper`
  - `test/integration-tests-pipeline`

### Making Changes

1. **Understand the scope**: Read existing code and understand the module you're working on
2. **Make incremental changes**: Small, focused commits are easier to review
3. **Test frequently**: Test your changes after each significant modification

```bash
# Stage specific files (preferred over git add .)
git add path/to/changed/file.py

# Commit with descriptive message following conventional commits
git commit -m "feat: add support for Amazon product scraping

- Add Amazon-specific selectors for image extraction
- Handle dynamic loading with explicit waits
- Add error handling for missing elements
- Update config.yaml example with Amazon URL"

# Push branch to GitHub
git push origin your-feature-branch-name
```

### Staying Updated with Main Branch

Regularly sync your branch with the latest changes:

```bash
# Switch to main and pull latest changes
git checkout main
git pull origin main

# Switch back to your branch and merge main
git checkout your-feature-branch-name
git merge main

# Alternative: Use rebase for cleaner history (advanced)
git rebase main
```

---

## 5. Code Standards

### Python Code Style

Follow [PEP 8](https://pep8.org/) guidelines and these project-specific conventions:

```python
# Use meaningful variable names
image_urls = extract_image_urls(product_url)  # ✅ Good
urls = get_imgs(url)  # ❌ Avoid

# Add docstrings for functions
def process_ocr_data(raw_text: str, config: dict) -> dict:
    """
    Extract structured product data from OCR text using Gemini AI.
    
    Args:
        raw_text: Raw OCR output from Document AI
        config: Configuration dictionary with API settings
        
    Returns:
        Dictionary containing extracted product information
        
    Raises:
        ValueError: If required config parameters are missing
        APIError: If Gemini API call fails
    """
    pass

# Use type hints
def check_compliance(vector_db: Chroma, product: dict) -> dict:
    pass

# Handle errors appropriately
try:
    result = api_call()
except APIError as e:
    logger.error(f"API call failed: {e}")
    return {"error": str(e)}
```

### Import Organization
```python
# Standard library imports first
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Third-party imports
import requests
import yaml
from selenium import webdriver
from pymongo import MongoClient

# Local imports last
from scraper.scrape_upload_data import extract_image_urls
from ocr_data_extractor.image_processor import process_images
```

### Configuration and Environment Variables
```python
# Use environment variables for sensitive data
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment")

# Provide meaningful defaults
timeout_seconds = int(os.getenv("SELENIUM_TIMEOUT", "30"))
headless_mode = os.getenv("SELENIUM_HEADLESS", "1") == "1"
```

---

## 6. Testing Guidelines

### Manual Testing
Always test your changes before submitting:

```bash
# Test the complete pipeline
python main.py

# Test individual modules
python -c "from scraper.scrape_upload_data import extract_image_urls; print('Scraper module works')"
python -c "from ocr_data_extractor.image_processor import process_images_to_ocr; print('OCR module works')"
python -c "from rag.rag import load_vector_db; print('RAG module works')"

# Test with different product URLs
# Update config.yaml with test URLs from different e-commerce sites
```

### Error Handling Testing
```bash
# Test with invalid URLs
# Test with missing API keys
# Test with network connectivity issues
# Test with malformed images
```

### Performance Testing
```bash
# Test with multiple images
# Monitor memory usage during processing
# Check processing time for different image sizes
```

---

## 7. Documentation Requirements

### Code Documentation
- Add docstrings to all functions and classes
- Include type hints for function parameters and return values
- Add inline comments for complex logic
- Update module-level docstrings when adding new functionality

### README Updates
When adding new features, update the relevant sections in README.md:
- Project structure (if adding new files/directories)
- Setup instructions (if requiring new dependencies)
- Usage examples (if changing API)
- Configuration options (if adding new settings)

### Configuration Examples
If your changes require new configuration options:
```yaml
# Add to config.yaml example in README.md
new_feature:
  enabled: true
  timeout: 30
  retry_attempts: 3
```

---

## 8. Pull Request Process

### Before Creating a Pull Request

1. **Test thoroughly**: Ensure your changes work as expected
2. **Update documentation**: Add/update relevant documentation
3. **Check formatting**: Ensure code follows style guidelines
4. **Commit clean history**: Use clear, descriptive commit messages

### Creating the Pull Request

1. **Go to GitHub repository**
2. **Click "New Pull Request"**
3. **Select your branch** as the source
4. **Write a clear title** following conventional commit format:
   - `feat: add support for Flipkart product scraping`
   - `fix: resolve Selenium timeout issues`
   - `docs: update setup instructions`

5. **Provide detailed description**:
   ```markdown
   ## Summary
   Brief description of what this PR does
   
   ## Changes Made
   - List specific changes
   - Include any breaking changes
   - Mention new dependencies if any
   
   ## Testing
   - How you tested the changes
   - What scenarios were covered
   - Any known limitations
   
   ## Screenshots (if UI changes)
   - Before/after screenshots if applicable
   
   ## Related Issues
   - Fixes #123
   - Relates to #456
   ```

6. **Request review** from maintainers
7. **Address feedback** promptly and professionally

### Pull Request Review Process

- Maintainers will review your code for functionality, style, and documentation
- Be responsive to feedback and questions
- Make requested changes promptly
- Keep discussions focused on the code and technical aspects
- Once approved, your PR will be merged into the main branch

---

## 9. Issue Reporting

### Before Creating an Issue

1. **Search existing issues** to avoid duplicates
2. **Check documentation** to ensure it's not a setup issue
3. **Test with minimal example** to isolate the problem

### Creating a Good Issue

**Bug Reports:**
```markdown
## Bug Description
Clear description of what went wrong

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should have happened

## Actual Behavior
What actually happened

## Environment
- OS: Ubuntu 20.04
- Python: 3.9.7
- Chrome: 96.0.4664.110

## Error Messages
```
Paste error messages or logs here
```

## Additional Context
Any other relevant information
```

**Feature Requests:**
```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why would this feature be useful?

## Proposed Implementation
Any ideas about how it could be implemented

## Alternatives Considered
Other approaches that were considered
```

---

## 10. Getting Help

### Communication Channels

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Comments**: For specific technical questions about implementation

### Common Questions

**Q: How do I add support for a new e-commerce platform?**
A: Look at `scraper/scrape_upload_data.py` and add platform-specific selectors and logic.

**Q: How can I improve OCR accuracy for specific product types?**
A: Consider adding specialized processing in `ocr_data_extractor/image_processor.py` or tuning Gemini prompts in `gemini_postprocess.py`.

**Q: How do I add new legal metrology rules?**
A: Update the PDF in `rag/pdfs/` and rebuild the vector database, or modify the validation logic in `rag/rag.py`.

**Q: Can I run this system on my own infrastructure?**
A: Yes! The system is designed to be self-hosted. You just need the required API keys and services.

### Getting Started Tips

1. **Start small**: Begin with documentation fixes or small bug fixes
2. **Read the code**: Understand the existing patterns before adding new features
3. **Ask questions**: Don't hesitate to ask for clarification in issues or discussions
4. **Test thoroughly**: Always test your changes with real data

---

## Important Notes and Best Practices

### Security Considerations
- **Never commit API keys** or credentials to the repository
- Use environment variables for all sensitive configuration
- Be careful with user input to prevent injection attacks
- Validate all external data before processing

### Performance Considerations
- **Monitor memory usage** when processing large images
- **Implement rate limiting** for API calls to avoid exceeding quotas
- **Use async processing** where appropriate for better performance
- **Clean up temporary files** to prevent disk space issues

### Legal and Ethical Guidelines
- **Respect robots.txt** when scraping websites
- **Don't overload servers** with too many concurrent requests
- **Follow API terms of service** for all external services
- **Respect data privacy** and handle personal information appropriately

### Project Maintenance
- **Keep dependencies updated** but test thoroughly before updating
- **Document breaking changes** clearly in PR descriptions
- **Maintain backward compatibility** when possible
- **Archive or clean up** obsolete code and files

---

Thank you for contributing to the Legal Metrology Compliance Checker! Your efforts help make this tool more effective for ensuring regulatory compliance in the food packaging industry. 🎯
