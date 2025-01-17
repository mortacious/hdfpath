from setuptools import setup, find_packages


# standalone import of a module (https://stackoverflow.com/a/58423785)
def import_module_from_path(path):
    """Import a module from the given path without executing any code above it
    """
    import importlib
    import pathlib
    import sys

    module_path = pathlib.Path(path).resolve()
    module_name = module_path.stem  # 'path/x.py' -> 'x'
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)

    if module not in sys.modules:
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    else:
        module = sys.modules
    return module


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

version = import_module_from_path('hdfpath/_version.py').__version__


setup(
    name='hdfpath',
    version=version,
    description="Quick searches of Hierarchical Data Format (HDF)-Files and dict-like data structures based on JSONPath.",
    author='Felix Igelbrink',
    author_email='felix.igelbrink@uni-osnabrueck.de',
    url='https://github.com/mortacious/hdfpath',
    license='Apache 2.0',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        'ply', 'decorator', 'six'
    ],
    extras_require={
        'hdf5': ["h5py"],
        'zarr': ["zarr"]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
    zip_safe=True
)
