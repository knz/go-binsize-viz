# Go executable size visualization using D3

This directory contains code and data to visualize the contents of Go
binaries.

## Example output

![screenshot](size-demo-ss.png)

## How to use

Apply tools in order (Python 3 required):

1. `go tool nm -size <binary file> | c++filt` and redirect to some file, e.g. `symtab.txt`

   (provided with the Go toolchain.)

2. `python3 tab2pydic.py` on the previously generated file, redirect to e.g. `out.py`

3. `python3 simplify.py` on the previously generated file, redirect to `data.js` **specifically**

4. `python3 -m http.server`

5. open browser on http://localhost:8000/treemap_v3.html

## Included example data using CockroachDB

1. `python3 -m http.server`

2. open browser on http://localhost:8000/cockroach_sizes.html

## Origin of the D3 viz source code

This repo uses D3 visualization code inspired from / modifying the
following sources:

-  Jacques Jahnichen's zoomable treemap at http://bl.ocks.org/JacquesJahnichen/42afd0cde7cbf72ecb81

- ported to D3 v4 by Guglielmo Celata at http://bl.ocks.org/guglielmo/16d880a6615da7f502116220cb551498
