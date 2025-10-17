# Security Policy

## ⚠️ Important Security Considerations

### Arbitrary Code Execution

**PyMD executes Python code within `.pymd` files.** This is a core feature but comes with important security implications:

#### 🚨 Critical Warnings

1. **NEVER execute untrusted `.pymd` files**
   - PyMD files have full access to your Python environment
   - They can read/write files, make network requests, and execute system commands
   - Only run `.pymd` files from trusted sources

2. **Server Mode Security**
   - Running `pyexecmd serve` allows code execution via the web editor
   - Only run the server on `localhost` (default) or trusted networks
   - Do NOT expose the PyMD server to the public internet without proper authentication
   - Consider using firewalls to restrict access

3. **Production Use**
   - PyMD is designed for development, documentation, and personal use
   - For production environments, render `.pymd` files to HTML in a sandboxed environment
   - Serve only the generated HTML files, not the PyMD server itself

#### Best Practices

```bash
# ✅ SAFE: Running your own trusted files
pyexecmd render my_document.pymd -o output.html
python my_trusted_script.pymd

# ✅ SAFE: Local development server
pyexecmd serve --file my_document.pymd --host localhost --port 8080

# ⚠️ RISKY: Running downloaded files (inspect first!)
# Always review the code before running:
cat downloaded_file.pymd  # Review the content
pyexecmd render downloaded_file.pymd

# 🚨 DANGEROUS: Public server without authentication
# pyexecmd serve --host 0.0.0.0 --port 80  # DON'T DO THIS
```

### Input Handling

- PyMD supports `input()` mocking via comments for non-interactive execution
- Be cautious with user-provided input in your `.pymd` scripts
- Always sanitize and validate input data

### File System Access

- PyMD can read/write files within your Python environment's permissions
- Images and videos are saved to `images/` and `videos/` directories
- Ensure proper file permissions on your output directories

### Dependencies

- PyMD depends on Flask, matplotlib, pandas, and other packages
- Keep dependencies updated to receive security patches
- Review our `requirements.txt` and `pyproject.toml` regularly

```bash
# Update dependencies
pip install --upgrade pyexecmd
```

## Reporting Security Issues

If you discover a security vulnerability in PyMD, please report it responsibly:

1. **Do NOT** open a public GitHub issue
2. Email the maintainers at: [security@pymd.dev](mailto:security@pymd.dev) (or via GitHub private vulnerability reporting)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work with you to address the issue.

## Security Updates

- Security patches will be released as soon as possible
- Critical vulnerabilities will be announced via GitHub Security Advisories
- Subscribe to releases on GitHub to stay informed

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Environment Isolation

For maximum security when working with untrusted code:

```bash
# Use a virtual environment
python -m venv pymd_env
source pymd_env/bin/activate  # On Windows: pymd_env\Scripts\activate
pip install pyexecmd

# Use Docker (future feature)
# docker run --rm -v $(pwd):/workspace pymd/pyexecmd render document.pymd
```

## Additional Resources

- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [OWASP Python Security](https://owasp.org/www-project-python-security/)
- [Flask Security Considerations](https://flask.palletsprojects.com/en/latest/security/)

---

**Remember: PyMD is a powerful tool. With great power comes great responsibility.** 🕷️
