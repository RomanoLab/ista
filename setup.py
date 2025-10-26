from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
import sys
import os
import subprocess

with open("README.md", 'r', encoding="utf-8") as fp:
    readme = fp.read()


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build C++ extensions")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        
        # Create build directory
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        cmake_args = [
            f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}',
            f'-DPYTHON_EXECUTABLE={sys.executable}',
            '-DBUILD_PYTHON_BINDINGS=ON',
        ]

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if sys.platform.startswith('win'):
            cmake_args += [f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{cfg.upper()}={extdir}']
            build_args += ['--', '/m']
        else:
            cmake_args += [f'-DCMAKE_BUILD_TYPE={cfg}']
            build_args += ['--', '-j2']

        env = os.environ.copy()
        env['CXXFLAGS'] = f"{env.get('CXXFLAGS', '')} -DVERSION_INFO=\\"{self.distribution.get_version()}\\""
        
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.', '--target', '_libista_owl2'] + build_args, cwd=self.build_temp)


setup(
    name="ista",
    version="0.1.1",
    author="Joseph D. Romano",
    description="A hybrid Python/C++ toolkit for building and manipulating knowledge graphs.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/JDRomano2/ista",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        'mysqlclient',
        'openpyxl',
        'owlready2',
        'pandas',
        'tqdm',
        'pybind11>=2.6.0',
    ],
    extras_require={
        'neo4j': ['neo4j'],
        'graph': ['networkx'],
        'dev': ['pytest', 'sphinx'],
    },
    ext_modules=[CMakeExtension('_libista_owl2', sourcedir='.')],
    cmdclass={'build_ext': CMakeBuild},
    entry_points={
        'console_scripts': [
            'ista=ista.ista:main'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: C++',
    ],
    zip_safe=False,
)
