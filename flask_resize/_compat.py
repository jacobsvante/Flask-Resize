import sys


PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY3:
    string_types = str,

    def b(s):
        return s.encode("latin-1")

else:
    string_types = basestring,  # noqa

    def b(s):
        return s
