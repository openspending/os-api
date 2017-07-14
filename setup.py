from setuptools import setup, find_packages

__version__ = '0.0.1'

setup(
    name='os_api',
    version=__version__,
    description='API for OpenSpending Next',
    long_description='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='api fiscal datapackage babbage openspending next',
    author='OpenSpending',
    author_email='info@openspending.org',
    url='https://github.com/openspending/babbage.fiscal-data-package',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'test']),
    namespace_packages=[],
    package_data={
        '': ['*.json'],
    },
    zip_safe=False,
    install_requires=[
        # We're using requirements.txt
    ],
    tests_require=[
        'tox',
    ]
)
