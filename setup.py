#!/usr/bin/env python3
"""
Setup script for Scrive - Pythonic Regex Pattern Builder.
"""

import os

from setuptools import find_packages, setup


# Read README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


setup(
    name="scrive",
    version="1.0.0",
    description="A Pythonic regex pattern builder",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Domenic Urso",
    author_email="domenicjurso@gmail.com",
    url="https://github.com/DomBom16/scrive",
    packages=find_packages(),
    py_modules=["scrive"],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    keywords="regex regexp regular-expressions pattern-matching fluent-api method-chaining pythonic operator-overloading",
    project_urls={
        "Bug Reports": "https://github.com/DomBom16/scrive/issues",
        "Source": "https://github.com/DomBom16/scrive",
        "Documentation": "https://github.com/DomBom16/scrive#readme",
    },
    include_package_data=True,
    zip_safe=False,
)
