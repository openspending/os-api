from setuptools import setup, find_packages

__version__ = '0.0.1'

setup(
    name='os_api',
    version=__version__,
    description="API for OpenSpending Next",
    long_description="",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
    keywords='api fiscal datapackage babbage openspending next',
    author='OpenSpending',
    author_email='info@openspending.org',
    url='https://github.com/openspending/babbage.fiscal-data-package',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'test']),
    namespace_packages=[],
    package_data={},
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    install_requires=[
        # TODO: Add other dependencies once they go into pypi
        'flask-cors',
        'flask-jsonpify',
        'sqlalchemy',
        'six',
    ],
    tests_require=[
        'pytest',
        'flask-testing',
    ]
)
