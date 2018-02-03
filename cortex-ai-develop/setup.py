from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
requirements = open(os.path.join(here, 'requirements.txt')).read().split('\n')

name = "cortex"
version = '0.0.1'

install_requires = requirements


setup(
    name=name,
    version=version,
    description="An Artificial Brain",
    long_description=README,
    classifiers=[
      
    ],
    keywords='',
    author='',
    author_email='',
    url='',
    license='',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['cortex=cortex:main']
    }
)

