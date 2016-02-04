from setuptools import setup


def read(filename):
    with open(filename, 'r') as fp:
        return fp.read()


setup(
    name="earful",
    version="0.1",
    packages=["earful"],
    install_requires=[],
    tests_require=['nose2'],
    test_suite='nose2.collector.collector',
    author="Alec Elton",
    author_email="alec.elton@gmail.com",
    description=read("README.md"),
    license="MIT",
    url="https://github.com/BasementCat/earful",
)