"""
Enterprise MCP Framework setup
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="enterprise-mcp-framework",
    version="0.1.0",
    author="Cognio AI Lab",
    author_email="dev@cogniolab.com",
    description="Production-grade security, observability, and governance for MCP servers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cogniolab/enterprise-mcp-framework",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "aiohttp>=3.9.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "ruff>=0.1.0",
        ],
        "observability": [
            "prometheus-client>=0.19.0",
            "opentelemetry-api>=1.20.0",
            "opentelemetry-sdk>=1.20.0",
        ],
        "security": [
            "cryptography>=41.0.0",
            "pyjwt>=2.8.0",
        ],
    },
)
