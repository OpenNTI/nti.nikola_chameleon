import codecs
from setuptools import setup, find_packages

entry_points = {
    'console_scripts': [
    ],
}

TESTS_REQUIRE = [
    'nti.testing',
    'zope.testrunner',
]


def _read(*fname):
    import os.path
    with codecs.open(os.path.join(*fname), encoding='utf-8') as f:
        return f.read()


setup(
    name='nti.nikola_chameleon',
    version='1.0.0',
    author='Jason Madden',
    author_email='jason@nextthought.com',
    description="NTI Nikola Chameleon",
    long_description=(
        _read('README.rst')
        + '\n\n'
        + _read('CHANGES.rst')),
    license='Apache',
    keywords='nikola chameleon template blog static',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    url="https://github.com/NextThought/nti.nikola_chameleon",
    zip_safe=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    namespace_packages=['nti'],
    tests_require=TESTS_REQUIRE,
    install_requires=[
        'setuptools',
        'Chameleon',
        'z3c.pt',
        'z3c.macro',
        'z3c.template',
        'z3c.ptcompat',
        'zope.browserpage',
        'zope.interface',
        'zope.dottedname',
        'zope.viewlet',
        'nikola >= 8.0.0b2',
    ],
    extras_require={
        'test': TESTS_REQUIRE,
        'docs': [
            'Sphinx',
            'repoze.sphinx.autointerface',
            'sphinx_rtd_theme',
        ],
    },
    # See the thread at https://github.com/pypa/pip/issues/2874#issuecomment-109429489
    # for why we don't try to use data_files.
    #data_files=[
    #    ('nikola', ['nti.nikola_chameleon.plugin',]),
    #],
    entry_points=entry_points,
    python_requires=">=3.5",
)
