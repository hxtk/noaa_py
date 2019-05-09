import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="noaa_py",
    version="0.2.1.dev0",
    author="Peter Sanders",
    description="NOAA Python API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hxtk/noaa_py",
    packages=setuptools.find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

