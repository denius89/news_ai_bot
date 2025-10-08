# Contributing to PulseAI

Thank you for your interest in contributing to **PulseAI**!  
This project is open to pull requests, suggestions, and improvements.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Testing](#testing)
- [Code Style](#code-style)
- [Git Workflow](#git-workflow)
- [Pull Request Process](#pull-request-process)
- [Documentation](#documentation)
- [Tips](#tips)
- [License](#license)

## Getting Started

1. **Fork and Clone**
   ```bash
   git clone https://github.com/<your-username>/news_ai_bot.git
   cd news_ai_bot
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate      # Windows
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   - Copy `.env.example` → `.env`
   - Add keys for **Supabase, OpenAI, DeepL**

## Development Setup

### Prerequisites
- Python 3.11+
- Git
- Supabase account
- OpenAI API key (optional)
- DeepL API key (optional)

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest -m "not integration"

# Start web application
python src/webapp.py

# Run Telegram bot
python -m telegram_bot.bot
```

### Development Commands
```bash
# Run all checks
make check

# Format code
make format

# Run linter
make lint

# Run tests
make test
```

## Testing

### Unit Tests (Fast)
```bash
pytest -m "not integration"
```

### Integration Tests (Requires API Keys)
```bash
pytest -m "integration"
```

### Test Coverage
```bash
pytest --cov --cov-report=term-missing
```

### Writing Tests
- Place tests in `tests/` directory
- Use descriptive test names
- Include both positive and negative test cases
- Mock external dependencies when possible

## Code Style

### Linting and Formatting
We use **flake8** and **black**:

```bash
# Check code style
flake8 .

# Check formatting
black --check .

# Auto-format code
black .
```

### Code Standards
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write descriptive docstrings
- Keep functions small and focused
- Use meaningful variable names

### Import Organization
```python
# Standard library imports
import os
import sys

# Third-party imports
import requests
from flask import Flask

# Local imports
from models.news import NewsItem
from services.digest_service import DigestService
```

## Git Workflow

### Branch Naming
- **Feature branches:** `feature/description`
- **Bug fixes:** `fix/bug-description`
- **Documentation:** `docs/update-readme`
- **Daily work:** `day-XX-feature-name`

### Commit Messages
Use conventional commit format:

```
feat: add support for topic filters
fix: resolve bug in rss_parser
docs: update README.md
chore: update CI pipeline
test: add tests for new feature
refactor: improve code structure
```

### Pre-commit Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No breaking changes without notice
- [ ] Commit message is descriptive

## Pull Request Process

### Before Submitting
1. **Ensure CI is green** ✅
2. **Update documentation** if needed
3. **Add tests** for new features
4. **Update TASKS.md** if applicable

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

### Review Process
- Maintainers will review within 48 hours
- Address feedback promptly
- Keep PRs focused and small
- Use draft PRs for work in progress

## Documentation

### Document Updates
- **README.md** — Project overview and quick start
- **docs/** — Detailed technical documentation
- **TASKS.md** — Current tasks and backlog
- **MASTER_FILE.md** — Project rules and decisions

### Documentation Standards
- Use clear, concise language
- Include code examples where helpful
- Keep documentation up to date
- Use consistent formatting

## Tips

### Project Structure
- **Tasks** — Document in `TASKS.md`
- **Decisions** — Record in `MASTER_FILE.md`
- **New files** — Auto-hook updates `CODEMAP.md`

### Development Workflow
1. **Check current tasks** in `TASKS.md`
2. **Review project rules** in `MASTER_FILE.md`
3. **Create feature branch** from `main`
4. **Implement changes** with tests
5. **Update documentation** as needed
6. **Submit pull request**

### Getting Help
- Check existing issues and discussions
- Ask questions in GitHub Discussions
- Review documentation in `docs/`
- Look at existing code for examples

### Common Issues
- **Import errors** — Check virtual environment activation
- **Test failures** — Verify environment variables
- **Style issues** — Run `black .` and `flake8 .`
- **Documentation** — Keep docs in sync with code

## License

This project is licensed under the [MIT License](LICENSE).  
By contributing, you agree that your contributions will be licensed under the same license.