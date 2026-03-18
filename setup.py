"""Setup script for openQCM Dual."""

from setuptools import setup, find_packages

from openqcm import __version__

setup(
    name="openqcm-dual",
    version=__version__,
    description="openQCM Dual Quartz Sensors monitoring software",
    author="openQCM",
    url="https://github.com/openQCM/openQCM-Dual",
    packages=find_packages(),
    package_data={"openqcm": ["gui/assets/*.ico"]},
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "PyQt5>=5.15",
        "pyqtgraph>=0.13",
        "pyserial>=3.5",
        "numpy>=1.21",
    ],
    entry_points={
        "console_scripts": [
            "openqcm-dual=openqcm.__main__:main",
        ],
    },
)
