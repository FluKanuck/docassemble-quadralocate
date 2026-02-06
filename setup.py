import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='docassemble.quadralocate',
    version='1.0.0',
    description='Quadra Utility Locating Site Report Interview',
    long_description=read('README.md') if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    author='Quadra Utility Locating Ltd.',
    author_email='info@quadralocate.com',
    license='MIT',
    url='https://github.com/quadralocate/docassemble-quadralocate',
    packages=['docassemble.quadralocate'],
    namespace_packages=['docassemble'],
    install_requires=['docassemble'],
    zip_safe=False,
    package_data={
        'docassemble.quadralocate': [
            'data/questions/*',
            'data/templates/*',
            'data/static/*',
        ]
    },
)
