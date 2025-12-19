from setuptools import setup, find_packages

setup(
    name="prompt-ai",
    version="0.0.1",
    description="",
    author="tiagolofi",
    author_email="tiagolofi@example.com",
    url="https://github.com/tiagolofi/prompt-ai",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "python-dotenv", "pytest"
    ],
    extras_require={
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
