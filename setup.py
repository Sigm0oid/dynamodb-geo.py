from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
      name="dynamodbgeo",
      version='0.1',
      description='A python port of awslabs/dynamodb-geo, for easier geospatial data manipulation and querying in DynamoDB',
      url='https://github.com/Sigm0oid/dynamodb-geo.py',
      author='Hamza Rhibi & Walid Sadallah',
      author_email='elrhibihamzas@gmail.com',
      license='MIT',
      long_description=readme(),
      long_description_content_type="text/markdown",
      classifiers=[
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
      ],
      packages=["dynamodbgeo"],
      include_package_data=True,
      install_requires=["boto3","s2sphere"],
      )
