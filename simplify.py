import sys

print("loading...", file=sys.stderr)
with open(sys.argv[1]) as f:
    values = eval(f.read())

values['name'] = '>'
def flatten(d):
    vals = []
    for k, v in d.items():
        v['name'] = k
        vals.append(v)
    return vals

def transform(d):
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
