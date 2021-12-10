# HDFPath
A python package to enable quick searches of Hierarchical Data Format (HDF)-Files based on JSONPath.
These files include the HDF5-Format provided by [`h5py`](https://github.com/h5py/h5py) as well as more recent libraries like 
[`zarr`](https://github.com/zarr-developers/zarr-python). Like `jsonpath-ng` any data structure
consisting of dict-like objects conforming to the `collections.abc.Mapping`-interface and lists is also supported.

This package is derived from the [`jsonpath-ng`](https://github.com/h2non/jsonpath-ng) library. 
For the query syntax and capabilities please refer to the original documentation at 
[https://github.com/h2non/jsonpath-ng](https://github.com/h2non/jsonpath-ng)

## Installation 

### Using pip
```
pip install hdfpath
```

### From source
```
git clone https://github.com/mortacious/hdfpath.git
cd hdfpath
python setup.py install
```

## Usage 

As HDF-Files are organized as groups containing datasets with both containing optional metadata attributes, this package
adds support to use these attributes directly inside queries. With the optional `metadata_attribute` parameter
to the parse function, the attribute to retrieve the metadata can be chosen.

```python
from hdfpath import parse
import h5py as h5

with h5.File("<HDF5-File>") as f:
    # query for all groups/datasets of type "scan" with the num_points attribute being larger than 40_000_000
    expr = parse('$..*[?(@._type == "scan" & @._num_points > 40000000)]', metadata_attribute='attrs')
    val = [match.value for match in expr.find(f)]
    print(val)
```

The metadata attributes are accessible inside the query using the `_` prefix.
Additionally, the use of regular expressions to match the fields is available through the `` `regex()` `` function.
For example `` `regex(\\\d+)` `` will only match groups/datasets that can be parsed into an integer number.

## TODOs

- code examples

## Copyright and License

Copyright 2021 - Felix Igelbrink

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.