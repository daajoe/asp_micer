#!/usr/bin/env python3
# Copyright (c) 2010, Roland Kaminski <kaminski@cs.uni-potsdam.de>
#
#
# lp2txt is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# lp2txt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with dasp2qbf. If not, see <http://www.gnu.org/licenses/>.

import sys
import optparse
import fileinput


class Rule:
    NORMAL = 0
    CHOICE = 1
    DISJUNCTION = 2

    def __init__(self, type):
        self.head = []
        self.body = []
        self.type = type

    def addHead(self, lit):
        self.head.append(lit)

    def add(self, lit, sign):
        self.body.append(-lit if sign else lit)

    def write(self, out, symtab):
        comma = False
        out.write("% ")
        if self.type == Rule.CHOICE: out.write("{")
        for lit in self.head:
            if comma:
                out.write("," if self.type == Rule.CHOICE else "|")
            else:
                comma = True
            out.write(symtab[lit])
        if self.type == Rule.CHOICE: out.write("}")
        comma = False
        for lit in self.body:
            if comma:
                out.write(",")
            else:
                out.write(":-")
                comma = True
            out.write(symtab[lit])
        out.write(".")


class Constraint:
    def __init__(self, weights):
        self.head = None
        self.body = []
        self.bound = None
        self.weights = [] if weights else None

    def addHead(self, lit):
        self.head = lit

    def add(self, lit, sign, weight=None):
        self.body.append(-lit if sign else lit)
        if self.weights != None: self.weights.append(weight)

    def write(self, out, symtab):
        out.write("% ")
        out.write(symtab[self.head])
        out.write(":-{0}{1}".format(self.bound, "{" if self.weights == None else "["))
        comma = False
        if self.weights != None:
            it = iter(self.weights)
        else:
            it = None
        for lit in self.body:
            if comma:
                out.write(",")
            else:
                comma = True
            out.write(symtab[lit])
            if it != None: out.write("={0}".format(next(it)))
        out.write("{0}.".format("}" if self.weights == None else "]"))


class Minimize:
    def __init__(self):
        self.lits = []
        self.weights = []

    def add(self, lit, sign, weight):
        self.lits.append(-lit if sign else lit)
        self.weights.append(weight)

    def write(self, out, symtab):
        out.write("% ")
        out.write("#minimize[")
        comma = False
        for lit, weight in zip(self.lits, self.weights):
            if comma:
                out.write(",")
            else:
                comma = True
            out.write(symtab[lit])
            out.write("={0}".format(weight))
        out.write("].")


class Compute:
    def __init__(self):
        self.lits = []

    def add(self, lit, sign):
        self.lits.append(-lit if sign else lit)

    def write(self, out, symtab):
        out.write("% ")
        out.write("#compute{")
        comma = False
        for lit in self.lits:
            if comma:
                out.write(",")
            else:
                comma = True
            out.write(symtab[lit])
        out.write("}.")


class SymTab:
    def __init__(self, prefix):
        self.prefix = prefix
        self.tab = {}
        self.rtab = {}

    def __setitem__(self, key, val):
        self.tab[key] = val
        self.rtab[val] = key

    def __getitem__(self, key):
        if key < 0:
            sign = "not "
            key = -key
        else:
            sign = ""
        val = self.tab.get(key, None)
        if val is not None:
            return sign + val
        else:
            return sign + self.prefix + str(key)


class Program:
    def __init__(self, prefix):
        self.compute = Compute()
        self.statements = []
        self.symtab = SymTab(prefix)

    def add(self, stm):
        self.statements.append(stm)

    def write(self, out):
        for x in self.statements:
            x.write(out, self.symtab)
            out.write("\n")
        self.compute.write(out, self.symtab)
        out.write("\n")


class LparseIter:
    def __init__(self, sin):
        self.sin = sin
        self.num = True

    def __iter__(self):
        for line in self.sin:
            while True:
                if self.num:
                    s = line.split(None, 1)
                    if len(s) > 0:
                        yield int(s[0])
                    if len(s) > 1:
                        line = s[1]
                    else:
                        break
                else:
                    yield line[:-1]
                    self.num = True
                    break


class Parser:
    def parse(self, prefix, sin):
        p = Program(prefix)
        lpIt = LparseIter(sin)
        it = iter(lpIt)
        while True:
            n = next(it)
            if n == 0:
                break
            elif n == 1:
                s = Rule(Rule.NORMAL)
                s.addHead(next(it))
                l = next(it)
                n = next(it)
                for i in range(0, l): s.add(next(it), i < n)
                p.add(s)
            elif n == 2:
                s = Constraint(False)
                s.addHead(next(it))
                l = next(it)
                n = next(it)
                s.bound = next(it)
                for i in range(0, l): s.add(next(it), i < n)
                p.add(s)
                raise NotImplemented("Not suitable for MIC encoding.")
            elif n == 3:
                s = Rule(Rule.CHOICE)
                h = next(it)
                for i in range(0, h): s.addHead(next(it))
                l = next(it)
                n = next(it)
                for i in range(0, l): s.add(next(it), i < n)
                p.add(s)
                # raise NotImplemented("Not suitable for MIC encoding. Use lp2normal by Tomi Janhunen...")
            elif n == 5:
                s = Constraint(True)
                s.addHead(next(it))
                s.bound = next(it)
                l = next(it)
                n = next(it)
                ls = []
                ws = []
                for _ in range(0, l): ls.append(next(it))
                for _ in range(0, l): ws.append(next(it))
                for lit, w, i in zip(ls, ws, range(0, l)): s.add(lit, i < n, w)
                p.add(s)
                raise NotImplemented("Not suitable for MIC encoding.")
            elif n == 6:
                s = Minimize()
                next(it)
                l = next(it)
                n = next(it)
                ls = []
                ws = []
                for _ in range(0, l): ls.append(next(it))
                for _ in range(0, l): ws.append(next(it))
                for lit, w, i in zip(ls, ws, range(0, l)): s.add(lit, i < n, w)
                p.add(s)
                raise NotImplemented("Not suitable for MIC encoding.")
            elif n == 8:
                s = Rule(Rule.DISJUNCTION)
                h = next(it)
                for i in range(0, h): s.addHead(next(it))
                l = next(it)
                n = next(it)
                for i in range(0, l): s.add(next(it), i < n)
                p.add(s)
            else:
                assert (False)

        while True:
            n = next(it)
            if n == 0:
                break
            else:
                lpIt.num = False
                p.symtab[n] = next(it)

        for sign in [False, True]:
            lpIt.num = False
            s = next(it)
            while True:
                n = next(it)
                if n == 0:
                    break
                else:
                    p.compute.add(n, sign)

        return p


class Application:
    def run(self):
        usage = "usage: %prog [options] [files]"
        parser = optparse.OptionParser(usage=usage)
        parser.add_option("-p", "--prefix", dest="prefix", type="string",
                          help="Prefix for unnamed symbols (default: 'x_')", default="x_")
        opts, files = parser.parse_args(sys.argv[1:])
        p = Parser()
        sin = fileinput.input(files)
        try:
            l = p.parse(opts.prefix, sin)
            l.write(sys.stdout)

            sys.stdout.write("% Created for MIC \n")
            sys.stdout.write("% SYMBOL TABLE\n")
            for i in l.symtab.tab:
                sys.stdout.write(f"% atom({i},{l.symtab[i]}).\n")
                sys.stdout.write(f"atom({i}).\n")

            sys.stdout.write("\n")

            col = set()
            for i, e in enumerate(l.statements):
                for a in e.head:
                    if a in l.symtab.tab:
                        x=l.symtab.tab[a]
                        if x.startswith('ddd'):
                            sel=x.split('ddd(')[1][:-1]
                            col.add(l.symtab.rtab[sel])
                            #print(l.symtab.rtab[sel])

            # body(R,_); head(R,_).
            query=set()
            for i, e in enumerate(l.statements):
                e.write(sys.stdout, l.symtab)
                sys.stdout.write("\n")

                for a in e.head:
                    if a in l.symtab.tab:
                        x=l.symtab.tab[a]
                        if x.startswith('ddd'):
                            continue
                        if a in col:
                            query.add(i+1)
                        sys.stdout.write(f"head({i + 1},{a}).\n")
                for b in e.body:
                    sys.stdout.write(f"body({i + 1},{b}).\n")

            sys.stdout.write("\n")
            for x in query:
                sys.stdout.write(f"e({x}).\n")
            return 0
        except IOError:
            sys.stderr.write("error reading from: {0}\n".format(sin.filename()))
            sys.stderr.flush()
            return 1


if __name__ == "__main__":
    sys.exit(Application().run())
