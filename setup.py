from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='model_playground',
    version='1.1.1',
    packages=find_packages(),
    author= 'Jonathan Zhang',
    author_email="jon.zhang@ucsf.edu",
    description='Python package for simulating mathematical models.',
    url='https://github.com/jzhang1198/model_playground',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts': [
            'run_app=modelPlayground.run_app:main'
        ],
    },
    install_requires=requirements,
)