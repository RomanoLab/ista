from http.client import PROXY_AUTHENTICATION_REQUIRED
import setuptools

with open("README.md", 'r', encoding="utf-8") as fp:
    readme = fp.read()

setuptools.setup(
    name="ista",
    version="0.1.0",
    author="Joseph D. Romano",
    description="A toolkit for building semantic graph knowledge bases.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/JDRomano2/ista",
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    install_requires=[
        'mysqlclient',
        'openpyxl',
        'owlready2',
        'pandas',
        'tqdm'
    ],
    entry_points={
        'console_scripts': [
            'ista=ista.ista:main'
        ]
    }
)