# Contributing to PyMD

Thank you for your interest in contributing to PyMD! We welcome contributions from the community.

## 🚀 Quick Start

1. **Fork and clone the repository**

```bash
git clone https://github.com/treeleaves30760/PyMD.git
cd PyMD
```

2. **Set up your development environment**

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

3. **Create a branch for your changes**

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pymd --cov-report=html

# Run specific test file
pytest tests/test_basic_functionality.py

# Run with verbose output
pytest -v
```

## 🎨 Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting
- **Flake8**: Linting
- **isort**: Import sorting
- **mypy**: Type checking

```bash
# Format code with Black
black pymd/ tests/

# Check code style
flake8 pymd/

# Sort imports
isort pymd/ tests/

# Type check
mypy pymd/ --ignore-missing-imports
```

**Pre-commit hooks will automatically run these checks** before each commit.

## 📝 Commit Messages

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(renderer): add LaTeX math support with MathJax

Implements LaTeX rendering using MathJax library for inline
and block math expressions.

Closes #123
```

```
fix(server): resolve path traversal vulnerability

Sanitize file paths to prevent directory traversal attacks.

Fixes #456
```

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **PyMD version**: `pyexecmd --version` or `python -c "import pymd; print(pymd.__version__)"`
2. **Python version**: `python --version`
3. **Operating System**: e.g., Ubuntu 22.04, macOS 14, Windows 11
4. **Steps to reproduce**: Minimal code example
5. **Expected behavior**: What should happen
6. **Actual behavior**: What actually happens
7. **Error messages**: Full traceback if applicable

## ✨ Feature Requests

We love hearing about new feature ideas! When proposing features:

1. **Check existing issues** to avoid duplicates
2. **Describe the problem** your feature would solve
3. **Explain the proposed solution** with examples if possible
4. **Consider alternatives** you've thought about
5. **Additional context**: Use cases, mockups, etc.

## 🔧 Pull Request Process

1. **Update tests**: Add tests for new functionality
2. **Update documentation**: Update README.md, docstrings, etc.
3. **Run the full test suite**: Ensure all tests pass
4. **Update CHANGELOG.md**: Add your changes under "Unreleased"
5. **Create the PR**: Use a descriptive title and reference related issues

### PR Checklist

- [ ] Code follows the project's style guidelines
- [ ] Self-review of code completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated and passing
- [ ] No new warnings introduced
- [ ] CHANGELOG.md updated
- [ ] PR description explains changes clearly

## 🏗️ Development Workflow

### Adding a New Feature

1. **Plan the feature**: Open an issue for discussion first
2. **Write tests**: Test-driven development is encouraged
3. **Implement the feature**: Keep commits focused and logical
4. **Document the feature**: Add examples and API docs
5. **Test thoroughly**: Unit tests, integration tests, manual testing
6. **Submit PR**: Reference the original issue

### Fixing a Bug

1. **Reproduce the bug**: Create a failing test case
2. **Fix the bug**: Make the test pass
3. **Test edge cases**: Ensure the fix is robust
4. **Document the fix**: Update CHANGELOG.md
5. **Submit PR**: Include "Fixes #issue-number"

## 📚 Documentation

Good documentation is crucial! Help us by:

- Fixing typos and clarifying explanations
- Adding examples to the syntax guide
- Creating tutorials for common use cases
- Improving API documentation
- Adding diagrams and visual aids

## 🧑‍💻 Code Review Process

1. **Maintainers review** PRs as soon as possible
2. **Feedback is constructive**: We're all learning together
3. **Address comments**: Make requested changes or discuss alternatives
4. **Final approval**: At least one maintainer approval required
5. **Merge**: Squash and merge is preferred for clean history

## 🎯 Areas Needing Help

Check issues labeled:
- `good first issue`: Great for newcomers
- `help wanted`: We'd love community contributions
- `documentation`: Docs improvements needed
- `performance`: Speed and efficiency improvements
- `enhancement`: New features

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code of Conduct**: Be respectful and inclusive

## 🙏 Recognition

All contributors will be:
- Listed in CONTRIBUTORS.md
- Thanked in release notes
- Celebrated in our community!

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to PyMD! 🎉
