from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="amazon-bedrock-nova-chatbot",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A minimal Python-based chatbot using Amazon Bedrock and the new Nova models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/amazon-bedrock-nova-chatbot",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "nova-chatbot=src.main:main",
        ],
    },
)
