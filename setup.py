import setuptools

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "qcoptimizer",
    version = "0.0.2.7",
    author = "Taren Patel",
    author_email = "tarenpatel1013@gmail.com",
    description = "A package for quantum circuit complexity-based optimization through Qiskit optimization level assignment",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    package_data={'': ['data/*.sav']},
    include_package_data=True,
    python_requires = ">=3.7"
)