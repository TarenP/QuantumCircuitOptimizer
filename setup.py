from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.2'
DESCRIPTION = 'A package for quantum circuit optimization'
LONG_DESCRIPTION = 'A package that modifies an existing quantum circuit, built with qiskit, to reduce the amount of gates, computing time, and error rates'

# Setting up
setup(
    name="qcoptimizer",
    version=VERSION,
    author="Taren Patel",
    author_email="<Tarenpatel1013@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['numpy', 'pandas', 'qiskit', 'csv'],
    keywords=['python', 'quantum', 'quantum computing', 'qiskit', 'quantum circuit', 'optimization'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)