import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="attrs2bin",
    version="0.0.1",
    author="Francisco Vicent",
    author_email="franciscovicent@outlook.com",
    description="Binary serializer for attrs-based classes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fvicent/attrs2bin",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Rust"
    ],
    install_requires=[
        "zope.interface",
        "zope.component",
        "attrs",
    ],
    python_requires='>=3.6',
)