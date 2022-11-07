#    go-binsize-viz, Go executable vizualisation
#    Copyright (C) 2018-2022 Raphael 'kena' Poss
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
import sys

print("loading...", file=sys.stderr)
with open(sys.argv[1]) as f:
    values = eval(f.read())

values['name'] = '>'
def flatten(d):
    vals = []
    for k, v in d.items():
        if isinstance(v, dict):
            v['name'] = k
            vals.append(v)
    return vals

def transform(d):
    # transform [A, B., X] into  [A, B/, _self_, X]  if [A, B/] also exists already.
    maybecopy = None
    for k in d:
        if k.endswith('.'):
            dirkey = k[:-1] + '/'
            if dirkey in d:
                if maybecopy is None:
                    maybecopy = d.copy()
                maybecopy[dirkey]['children']['· self'] = d[k]
                del(maybecopy[k])
    if maybecopy is not None:
        d = maybecopy

    for k, v in list(d.items()):
        if type(v) == type({}):
            ename, v = transform(v)
            del d[k]
            d[k+ename] = v
    ename = ""
    if "children" in d:
        c = flatten(d['children'])
        if len(c) == 1 and "children" in c[0]:
            c0 = c[0]
            ename = c0["name"]
            c = c0["children"]
        d['children'] = c
    return ename, d

print("transforming...", file=sys.stderr)
_, values = transform(values)

print("output...", file=sys.stderr)
import json
json.dump(values, sys.stdout)
