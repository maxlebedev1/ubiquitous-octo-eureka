# Contributing to Recursive Agentic AI Platform

Thank you for your interest in contributing! This guide will help you get started.

## 🤝 How to Contribute

### Reporting Bugs

1. Check existing issues first
2. Create a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (Python version, OS, etc.)

### Suggesting Features

1. Open an issue describing the feature
2. Explain the use case and benefits
3. Discuss implementation approach if possible

### Code Contributions

#### 1. Fork and Clone

```bash
git clone https://github.com/your-username/agentic-platform.git
cd agentic-platform
```

#### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

#### 3. Set Up Development Environment

```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio
```

#### 4. Make Changes

- Follow existing code style
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

#### 5. Run Tests

```bash
pytest tests.py -v
```

#### 6. Commit Changes

```bash
git commit -m "Add: brief description of changes"
```

#### 7. Push and Create PR

```bash
git push origin feature/your-feature-name
# Then create a Pull Request on GitHub
```

## 📝 Code Style Guidelines

- Use Python 3.10+ features when appropriate
- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Write docstrings for public APIs
- Keep functions focused and small (<50 lines ideal)

### Example

```python
async def execute_task(self, task: Task) -> bool:
    """
    Execute a single task with retry logic.
    
    Args:
        task: The task to execute
        
    Returns:
        True if successful, False otherwise
    """
    # Implementation here
    pass
```

## 🧪 Testing Requirements

- All new features must have tests
- Maintain >80% code coverage
- Test both success and failure cases
- Include integration tests for major workflows

### Running Tests

```bash
# Run all tests
pytest tests.py -v

# Run specific test class
pytest tests.py::TestTask -v

# Run with coverage
pytest --cov=agentic_platform tests.py
```

## 📚 Documentation

- Update README.md for user-facing changes
- Add docstrings to new classes/functions
- Update QUICKSTART.md if setup changes
- Include examples for new features

## 🔍 Pull Request Process

1. **Review**: Ensure code follows guidelines
2. **Test**: All tests must pass
3. **Document**: Update relevant docs
4. **Describe**: Write clear PR description
5. **Respond**: Address reviewer feedback

## 💬 Communication

- Be respectful and constructive
- Ask questions if unsure
- Help review others' PRs
- Share knowledge freely

## 🎯 Areas Needing Contribution

- [ ] Performance optimizations
- [ ] Additional LLM provider support
- [ ] Enhanced web interface features
- [ ] More comprehensive examples
- [ ] Better error handling
- [ ] Improved task decomposition strategies
- [ ] Caching mechanisms
- [ ] Monitoring and observability tools

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Questions?** Open an issue or reach out to maintainers.

**Thank you for contributing! 🙏**
