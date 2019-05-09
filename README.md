# NOAA Tides API [![Build Status](https://travis-ci.org/hxtk/noaa_py.svg?branch=master)](https://travis-ci.org/hxtk/noaa_py) [![codecov](https://codecov.io/gh/hxtk/noaa_py/branch/master/graph/badge.svg)](https://codecov.io/gh/hxtk/noaa_py)

This is intended to be a Python library for using the NOAA APIs. The milestone currently being targeted is the Tides and Currents API, which does not have a Python library yet.

## Installation

### From the command line

`pip install git+https://github.com/hxtk/noaa_py.git`

### In your `setup.py` file

```python
setup(
    ...
    install_requires=[
        ...
        "noaa_py @ git+https://github.com/hxtk/noaa_py.git@master",
        ...
    ]
    ...
)
```

### In your `requirements.txt` file

`noaa_py @ git+https://github.com/hxtk/noaa_py.git@master`

