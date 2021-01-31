import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="syjson",
    version="1.0.2",
    author="DomySh",
    author_email="me@domysh.com",
    description="A library for manage jsons file as dicts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DomySh/syjson",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
