from setuptools import setup, find_packages

setup(
    name='xbeach-mi',
    version='0.0',
    author='Bas Hoonhout',
    author_email='bas.hoonhout@deltares.nl',
    packages=find_packages(),
    description='A wrapper for running multiple parallel instances of the XBeach model',
    long_description=open('README.txt').read(),
    install_requires=[
        'numpy',
        'docopt',
        'mako',
        'multiprocessing',
    ],
    #setup_requires=[
    #    'sphinx',
    #    'sphinx_rtd_theme'
    #],
    tests_require=[
        'nose'
    ],
    test_suite='nose.collector',
    entry_points={'console_scripts': [
        '{0} = xbeachmi.console:xbeachmi'.format(
            'xbeach-mi'),
    ]},
)
