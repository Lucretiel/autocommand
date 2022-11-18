from setuptools import setup


def getfile(filename):
    with open(filename) as file:
        return file.read()

setup(
    name='autocommand',
    version='2.2.2',
    packages=[
        'autocommand'
    ],
    package_dir={'': 'src'},
    platforms='any',
    license='LGPLv3',
    author='Nathan West',
    url='https://github.com/Lucretiel/autocommand',
    description='A library to create a command-line program from a function',
    long_description=getfile('README.md'),
    classifiers=[
        'Development Status :: 6 - Mature',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
