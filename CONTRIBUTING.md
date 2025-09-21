# Contribution Guidelines

> **Note**: For project overview, setup instructions, and technical details, see the main [README.md](README.md). This file contains guidelines specifically for contributing to the Legal Metrology Compliance Checker project.

## 1. Repository Access

- This repository is **public** and available for contributions.
- Fork the repository to your GitHub account before making contributions.
- Make sure you have the necessary development environment set up (see README.md).

---

## 2. Initial Setup

### Fork and Clone
First, fork the repository on GitHub, then run these commands to set up your local workspace:

```bash
# Clone your forked repository
git clone https://github.com/YOUR-USERNAME/SIH2025.git

# Move into the project folder
cd SIH2025

# Add the original repository as upstream remote
git remote add upstream https://github.com/AnirudhDattu/SIH2025.git

# Verify remotes
git remote -v
```

### Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables (see README.md for details)
cp .env.example .env  # Edit with your configuration
```

---

## 3. Development Workflow

Always follow this workflow to ensure clean contributions:

### Sync with Upstream
Before starting any work, sync your fork with the latest changes:

```bash
# Switch to main branch
git checkout main

# Fetch latest changes from upstream
git fetch upstream

# Merge upstream changes
git merge upstream/main

# Push updates to your fork
git push origin main
```

### Create Feature Branch
Always work on a **separate branch** for each feature or fix:

```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name

# Alternative: fix branch for bug fixes
git checkout -b fix/issue-description
```

**Branch Naming Conventions:**
- `feature/description` - New features (e.g., `feature/add-ocr-validation`)
- `fix/description` - Bug fixes (e.g., `fix/mongodb-connection-timeout`)
- `docs/description` - Documentation updates (e.g., `docs/update-api-reference`)
- `refactor/description` - Code refactoring (e.g., `refactor/extract-compliance-logic`)
- `test/description` - Adding or updating tests (e.g., `test/add-unit-tests-rag`)

---

## 4. Making Changes

### Code Standards
- Follow Python PEP 8 style guidelines
- Add docstrings to all functions and classes
- Include type hints where appropriate
- Write meaningful variable and function names

### Making Commits
Stage and commit your changes with clear, descriptive messages:

```bash
# Stage specific files (preferred over git add .)
git add path/to/modified/file.py

# Or stage all changes if appropriate
git add .

# Commit with a clear, conventional message
git commit -m "feat: add OCR validation for product labels"
```

**Commit Message Conventions:**
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code formatting (no functional changes)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks, dependency updates

### Examples:
```bash
git commit -m "feat: implement RAG-based compliance scoring"
git commit -m "fix: resolve MongoDB connection timeout issue"
git commit -m "docs: update API documentation for gemini integration"
git commit -m "refactor: extract database operations to separate module"
```

---

## 5. Testing Your Changes

Before pushing, always test your changes:

```bash
# Run the main pipeline to ensure it works
python main.py

# Test specific components if applicable
python -m ocr_data_extractor.image_processor
python -m rag.rag
```

---

## 6. Pushing Changes

Push your branch to your forked repository:

```bash
git push origin your-feature-branch-name
```

---

## 7. Creating a Pull Request (PR)

1. Go to your forked repository on GitHub
2. Click "Compare & pull request" button that appears after pushing
3. Ensure the PR is targeting the correct base branch (usually `main`)
4. Write a clear PR title and description:
   - **Title**: Brief summary of the change
   - **Description**: Detailed explanation of:
     - What was changed and why
     - How to test the changes
     - Any breaking changes or dependencies
     - Screenshots for UI changes

### PR Template:
```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Tested locally
- [ ] All existing tests pass
- [ ] New tests added (if applicable)

## Additional Notes
Any additional information, dependencies, or considerations.
```

---

## 8. Code Review Process

- The maintainer(s) will review your PR
- Address any feedback or requested changes
- Make additional commits to your branch as needed
- Once approved, your PR will be merged into `main`

### Updating Your PR
If changes are requested:

```bash
# Make the requested changes
# Stage and commit them
git add .
git commit -m "fix: address code review feedback"

# Push updates to your PR branch
git push origin your-feature-branch-name
```

---

## 9. Staying Updated

Keep your fork synchronized with the upstream repository:

```bash
# Switch to main and pull latest changes
git checkout main
git fetch upstream
git merge upstream/main
git push origin main

# Update your feature branch with latest main
git checkout your-feature-branch-name
git merge main
```

---

## 10. Important Guidelines

### Code Quality
- **Test your changes**: Ensure the main pipeline runs successfully
- **Follow existing patterns**: Match the coding style of existing code
- **Document your code**: Add comments for complex logic
- **Keep commits atomic**: Each commit should represent a single logical change

### Repository Etiquette
- **Don't commit directly to `main`** - Always use feature branches
- **Keep PR scope focused** - One feature/fix per PR
- **Write clear commit messages** - Others should understand your changes
- **Respond to code reviews promptly**
- **Clean up after yourself** - Delete feature branches after merging

### File Management
- **Don't commit sensitive data** - Use `.env` files (already in `.gitignore`)
- **Don't commit build artifacts** - Keep `temp/` folder out of commits
- **Add `.gitkeep` for empty directories** - If you need to track empty folders

### Getting Help
- Check existing issues and documentation first
- Create detailed issues for bugs or feature requests
- Ask questions in PR discussions if unsure about implementation
- Reference issue numbers in commits: `git commit -m "fix: resolve OCR timeout issue (#123)"`

---

**Thank you for contributing to the Legal Metrology Compliance Checker! Your contributions help improve food safety and regulatory compliance across India.**