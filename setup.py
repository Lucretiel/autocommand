from setuptools import setup


def convert_to_rst(filename):
    try:
        import pypandoc
    except ImportError:
        print("pypandoc not available, couldn't create rst README")
        with open(filename) as file:
            return file.read()
    else:
        return pypandoc.convert(filename, 'rst')


setup(
    name='autocommand',
    version='0.9.0',
    py_modules=['autocommand'],
    package_dir={'': 'src'},
    platforms='any',
    license='LGPLv3',
    author='Nathan West',
    url='https://github.com/Lucretiel/autocommand',
    description='A library to create a command-line program from a function',
    long_description=convert_to_rst('README.md'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    setup_requires=['pypandoc']
)
