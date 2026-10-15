from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

from wende_transport import __version__ as version

setup(
    name="wende_transport",
    version=version,
    description="Comprehensive Fleet, Logistics, Maintenance, Store, Cashier and Operations Management System for Frappe v15",
    author="Wende Transport Team",
    author_email="info@wendetransport.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)
