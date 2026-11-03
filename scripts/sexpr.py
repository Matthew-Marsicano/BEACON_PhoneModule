"""Minimal S-expression reader/writer for KiCad files."""
import re

_tok = re.compile(r'\s*(?:(\()|(\))|"((?:[^"\\]|\\.)*)"|([^\s()"]+))', re.S)
_unesc = re.compile(r'\\(.)')


class Sym(str):
    """Unquoted atom."""


def parse(text):
    stack, cur = [], []
    pos, n = 0, len(text)
    while pos < n:
        m = _tok.match(text, pos)
        if not m:
            if not text[pos:].strip():
                break
            raise ValueError('bad token at %d' % pos)
        pos = m.end()
        if m.group(1):
            stack.append(cur)
            cur = []
        elif m.group(2):
            done = cur
            cur = stack.pop()
            cur.append(done)
        elif m.group(3) is not None:
            cur.append(_unesc.sub(lambda mm: '\n' if mm.group(1) == 'n' else mm.group(1), m.group(3)))
        else:
            cur.append(Sym(m.group(4)))
    return cur[0] if len(cur) == 1 else cur


def _atom(x):
    if isinstance(x, Sym):
        return str(x)
    if isinstance(x, bool):
        return 'yes' if x else 'no'
    if isinstance(x, int):
        return str(x)
    if isinstance(x, float):
        s = ('%.4f' % x).rstrip('0').rstrip('.')
        return '0' if s in ('-0', '') else s
    s = str(x).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    return '"' + s + '"'


def dump(x, indent=0):
    if not isinstance(x, list):
        return _atom(x)
    if not x:
        return '()'
    if all(not isinstance(e, list) for e in x):
        return '(' + ' '.join(_atom(e) for e in x) + ')'
    out = ['(' + _atom(x[0])]
    for e in x[1:]:
        if isinstance(e, list):
            out.append('\n' + '\t' * (indent + 1) + dump(e, indent + 1))
        else:
            out.append(' ' + _atom(e))
    return ''.join(out) + ')'


def find(node, key):
    for e in node:
        if isinstance(e, list) and e and e[0] == key:
            yield e


def first(node, key):
    return next(find(node, key), None)
