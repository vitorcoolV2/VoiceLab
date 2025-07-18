#!/usr/bin/env python3
"""
Setup script for Coqui TTS Project
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="coqui-tts-project",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A dedicated project for Coqui TTS functionality",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/coqui-tts-project",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "coqui-tts-server=src.tts_server:main",
            "coqui-tts-test=src.test_client:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json"],
    },
) 