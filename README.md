# Go executable size visualization

This directory contains code and data to visualize the contents of Go
binaries.

Apply tools in order (Python 3 required):

1. `go tool nm -size <binary file> | c++filt` and redirect to some file, e.g. `symtab.txt`

  provided with the Go toolchain.

2.`tab2pydic.py` on the previously generated file, redirect to e.g. `out.py`

3. `simplify.py` on the previously generated file, redirect to `data.js` **specifically**

4. `python -m http.server`

5. open browser on https://localhost:8000/treemap_v3.html
