from setuptools import setup, find_packages


def readme():
    with open('README.md', encoding='utf-8') as f:
        return f.read()


setup(
    name="dynamodbgeo",
    version='0.0.4',
    description='A python port of awslabs/dynamodb-geo, for easier geospatial data manipulation and querying in DynamoDB',
    url='https://github.com/Sigm0oid/dynamodb-geo.py',
    author='Hamza Rhibi & Walid Sadallah & Brandon Sneider',
    author_email='elrhibihamzas@gmail.com',
    license='MIT',
    long_description=readme(),
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    exclude_package_data={"": [".DS_Store"]},
    install_requires=["boto3>=1.11.8", "s2sphere>=0.2.5"],
)
