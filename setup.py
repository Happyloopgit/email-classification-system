from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="email-classification-system",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A system for classifying emails and extracting information",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Happyloopgit/email-classification-system",
    packages=find_packages(where="src"),
    package_dir={"":"src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.95.0",
        "uvicorn>=0.22.0",
        "pydantic>=1.10.7",
        "python-multipart>=0.0.6",
        "sentence-transformers>=2.2.2",
        "faiss-cpu>=1.7.4",
        "numpy>=1.24.2",
        "python-dotenv>=1.0.0",
        "reportlab>=3.6.13",
        "mail-parser>=3.15.0",
    ],
)