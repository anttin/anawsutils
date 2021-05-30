import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="anawsutils",
  version="0.1.3",
  author="anttin",
  author_email="muut.py@antion.fi",
  description="Module with miscallaneous AWS utils.",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/anttin/anawsutils",
  install_requires=[
    'boto3',
    'pandas'
  ],
  packages=setuptools.find_packages(),
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ]
)
