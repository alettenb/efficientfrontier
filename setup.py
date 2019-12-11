import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name='efficientfrontier',
    version='0.0.6',
    author='Alex Lettenberger',
    author_email='alex.lettenberger@gmail.com',
    description='Functions for calculating an efficient frontier.',
    long_description=long_description,
    long_description_content_type='ext/markdown',
    packages=setuptools.find_packages(),
    classifiepirs=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
)