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
import re
import sys

undefre = re.compile(r'^\s*0\s+U\s+',re.A)
entriesre = re.compile(r'^\s*([0-9a-fA-F]+)\s+([0-9]+)\s+(\S+)\s+(.*)$',re.A)

tmplpart = r'''
<
 (?:
    [^<>]
  | (?:
     <
      (?:
        [^<>]
      | (?:
          <
            (?:
              [^<>]
            | (?:
                <
                  (?:
                    [^<>]
                  | (?:
                      <
                        (?:
                          [^<>]
                        | (?:
                            <
                              (?:
                                [^<>]
                              | (?:
                                  <
                                    (?:
                                      [^<>]
                                    | (?:
                                        <
                                          (?:
                                            [^<>]
                                          | (?:
                                              <
                                                [^<>]*
                                              >
                                            )
                                          )*
                                        >
                                      )
                                    )*
                                  >
                                )
                              )*
                            >
                          )
                        )*
                      >
                    )
                  )*
                >
              )
            )*
          >
        )
      )*
     >
    )
 )*
>
'''
parengroup = tmplpart.replace("<", r'\(').replace(">", r'\)')

#print("WOO", parengroup)

cpppath = '''
     (?:
        \([^)]*\)                   # (anonymous namespace)
      | \{[^}]*\}                   # {lambda ...}
      | ~?                          # maybe ~destructor
        (?:
           \$?\w+                      # name
         | operator(?:[^\(]+|\(\))  # special name
        )
        (?:'''+tmplpart+''')?       # maybe <tmpl params>
        (?:'''+parengroup+''')?     # maybe function args
        (?:\sconst)?                # maybe " const"
     )::
  | [a-zA-Z]+_
'''

cpppathre = re.compile(cpppath, re.X|re.A)

cppsymre = re.compile(r'''
^
# prefix
(?:guard\svariable\sfor\s)?
(
  # type
  (?:
    (?:
       \w
     | ::
     | -
     | \*
     | \&
     | (?:'''+tmplpart+''')
    )+
    \s
  )*
)
(
  # path / namespace
  (?:'''+cpppath+''')*
)
(
  \{[^}]*\}                   # {lambda ...}
|
  # object name
  ~?                          # maybe destructor
  (?:
     \$?\w+                      # name
   | operator(?:[^\(]+|\(\))  # special name
   | \._\d+                   # ._NNN
  )
  (?:\[[^][]*\])?              # ABI spec
  (?:'''+tmplpart+''')?       # maybe <tmpl params>
  (?:'''+parengroup+'''
      (?:\sconst)?                # maybe " const"
      (?:\s\[.*\])?               # maybe words
      (?:\s\(
          (?:\.(?:constprop|part|isra).\d+)+
      \))?    # maybe (.constprop.NNN)
  )?
  (?:\*+)?                    # maybe ptr
)
$
''', re.X|re.A)

gopathparts = r'''
    \(
      (?:
         [^()]
       | \( [^()]* \)
      )*
    \)\.                  # (*Foo)., (*struct{... () }).
  | (?: struct | interface)\s\{
     (?:
        [^{}]
      | \{[^{}]*\}
     )*
    \}\.                  # struct { ... }.
  | \$?(?: (?:\w|-|%)+ (?:\[ (?: [^\]] | \[ [^\]]* \])+ \])? )\.      # fun. (with opt templ params)
  | glob\.\.              # glob..
  | \.gobytes\.           # .gobytes.
  | \.dict\.              # .dict.
  | (?:\w|\.|-|%)+/       # path/
'''

gopathpartsre = re.compile(gopathparts, re.X|re.A)

#print("WOO", gopathpartsre.findall("runtime.LockOSThread"), file=sys.stderr)


golastpart = r'''
      (?:
        (?:
            \.?
            (?:
               (?:\w|-|%)+    # regular name
               (?:\[ (?: [^\]] | \[ [^\]]* \])+ \])?          # optional template params
             | \( [^()]* \)   # v1.x go
            )
            (?:-fm)?)  # name
      | struct\s\{
           (?:
              [^{}]
            | \{[^{}]*\}
           )*
          \}                    # struct { ... }
      )
      (?:,
         (?:
          (?:(?:\w|\.|-|%)+/)*
          (?:\w|-|%|\.)+
          | interface\s\{ (?: [^{}] | \{ [^{}]* \} )* \}
         )
         |
         (?: '''+gopathparts+''' ).*
      )?    # opt ,xxx interface suffix
    | initdone\.
    | initdone·
'''

golastpartre = re.compile('('+golastpart + ')$', re.X|re.A)
#print("WOO", golastpartre.findall("runtime.LockOSThread"), file=sys.stderr)
#print("WOO", golastpartre.findall("go.itab.*archive/zip.countWriter,io.Writer"), file=sys.stderr)

gosymre = re.compile(r'''
^
  (
    (?:
       (?:go[:\.]itab\.\*?)
     | go:
    )?
  )
  (
    (?:'''+gopathparts+''')*
  )
  (
    '''+golastpart+'''
  )
$
''', re.X|re.A)

#print("WOO", gosymre.match("runtime.LockOSThread").groups(), file=sys.stderr)

vtables_sz = 0
typeinfo_sz = 0
init_sz = 0
rest_sz = 0
gotyp_sz = 0

values = {}

def store_rec(values, path, sz):
    if len(path) == 0:
        v = values.get("value", 0)
        v += sz
        values["value"] = v
    else:
        n = path[0]
        d1 = values.get("children", {})
        d = d1.get(n, {})
        d1[n] = d
        values["children"] = d1
        store_rec(d, path[1:], sz)

def store(path, sz):
    global values
    store_rec(values, path, sz)

c = 0
with open(sys.argv[1]) as f:
    for line in f:
        if undefre.match(line) is not None:
            # undefined (external) symbol, skip
            continue
        if line.endswith('\n'):
            line = line[:-1]

        m = entriesre.match(line)
        if m is None:
            print("\nunknown format:", line, file=sys.stderr)
            continue

        typ = m.group(3).strip()
        if typ == 'U':
            # external object, skip
            continue

        sz = m.group(2).strip()
        try:
            sz = int(sz)
        except:
            print("\nunknown size format:", m.group(2), file=sys.stderr)
            continue
        if sz == 0:
            # skip over no-size objects
            continue

        sym = m.group(4).strip()
        if sym == '':
            continue
        if sym.startswith('construction vtable ') or sym.startswith('vtable for '):
            # c++ virtual diamond constructors
            vtables_sz += sz
            continue
        if sym.startswith('__static_initialization_and_destruction'):
            # c++ static initializers
            init_sz += sz
            continue
        if sym.startswith('typeinfo '):
            # c++ type metadata
            typeinfo_sz += sz
            continue
        if sym.startswith('type..') or sym.startswith('type:'):
            # go generated type equality and hash functions
            gotyp_sz += sz
            continue

        parts = cppsymre.match(sym)
        if parts is not None:
            prefix = ['c/c++ · ']
            partsre = cpppathre

        if parts is None:
            parts = gosymre.match(sym)
            if parts is not None:
                prefix = ['go · ']
                partsre = gopathpartsre

        if parts is None:
            print("\nunknown",typ,"sym format:", sym, file=sys.stderr)
            rest_sz += sz
            continue

        path = parts.group(2)
        path = partsre.findall(path)
        name = parts.group(1) + parts.group(3)

        #print(sz, "##", parts.group(2), "##", path, "##", parts.group(1), "##", parts.group(3), file=sys.stderr)

        fullpath = prefix+path+[name]
        # print(sz, "##", fullpath)

        store(fullpath, sz)
        
        if c % 1000 == 0:
            print(".", end="", file=sys.stderr)
            sys.stderr.flush()
        c+=1

store(['c/c++ · ','VTABLES'], vtables_sz)
store(['c/c++ · ','TYPEDATA'], typeinfo_sz)
store(['c/c++ · ','INITIALIZERS'], init_sz)
store(['go · ','TYPEDATA'], gotyp_sz)
store(['UNKNOWN'], rest_sz)

print("\noutput...", file=sys.stderr)

print(values)
#import pprint
#pprint.pprint(values)
