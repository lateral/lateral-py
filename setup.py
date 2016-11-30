from setuptools import setup, find_packages

setup(
    name='lateral.py',
    version='0.0.1',
    description='python interface to Lateral\'s APIs',
    url='https://github.com/lateral/lateral.py',
    author='Christoph Schock',
    author_email='christoph@lateral.io',
    license='MIT',

    packages=find_packages(),
    install_requires=[
        'requests', 'responses',
    ],
)