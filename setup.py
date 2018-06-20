"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import os
from glob import glob
from os.path import basename, dirname, join, splitext, abspath
from codecs import open as copen
from setuptools import find_packages, setup

here = abspath(dirname(__file__))

with copen(join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# let's generate docs...
if os.environ.get("READTHEDOCS") and not os.path.isdir("docs"):
    os.mkdir("docs")
    os.system("make")
    os.system("make html")
else:

    setup(
        name='babao',
        version='0.1.0',
        license='BeerWare',
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
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: Implementation :: CPython',
        ],
        keywords='bitcoin bot',
        python_requires='>=3.5',
        install_requires=[
            # machine learning
            'keras>=2.2.0',
            'tensorflow>=1.8.0',
            'scipy>=1.1.0',
            'scikit-learn>=0.19.1',
            'joblib>=0.11',  # just for saving scikit models...

            # data handling
            'numpy>=1.14.5',
            'pandas>=0.23.1',
            'tables>=3.4.4',

            # parsing
            'configparser>=3.5.0',
            'argparse>=1.4.0',

            # api
            'krakenex>=2.1.0',
        ],
        extras_require={
            'graph': ['matplotlib'],
            'test': [
                'pytest-runner',
                'pytest',
                'pylint',
                'flake8',
                'coveralls',
                'sphinx'
            ],
        },
        setup_requires=['pytest-runner'],
        test_suite='pytest',
        package_data={
            # 'babao': ['package_data.dat'],
        },
        entry_points={
            'console_scripts': [
                'babao = babao.babao:main',
            ],
        },
    )
