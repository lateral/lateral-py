from setuptools import setup, find_packages

setup(
    name='apiwrappy',
    version='0.0.1',
    description='python interface to Lateral\'s APIs',
    url='https://github.com/lateral/apiwrappy',
    author='Christoph Schock',
    author_email='christoph@lateral.io',
    license='MIT',

    packages=find_packages(),
    install_requires=[
        'requests', 'responses',
    ],
)