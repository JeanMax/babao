"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from glob import glob
from os.path import basename, dirname, join, splitext, abspath
from codecs import open as copen
from setuptools import find_packages, setup


here = abspath(dirname(__file__))

with copen(join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='babao',
    version='0.1.0',
    license='MIT',
    description='A bitcoin trading machine - '
    '"I\'ve got 99 problems But A Bot Ain\'t One".',
    long_description=long_description,
    author='JeanMax',
    author_email='mcanal@student.42.fr',
    url='https://github.com/JeanMax/babao',

    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Crazy Bot',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    keywords='bitcoin bot',
    install_requires=[
        'scikit-learn',
        'pandas',
        'configparser',
        'argparse',
        'krakenex'
    ],
    extras_require={
        'graph': ['matplotlib'],
        'test': ['pytest', 'pylint', 'flake8'],
    },
    package_data={
        # 'babao': ['package_data.dat'],
    },
    entry_points={
        'console_scripts': [
            'babao = babao.babao:main',
        ],
    },
)
