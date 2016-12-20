#!/usr/bin/python
# coding: UTF-8
#-
# Dump data files encoded by PHP’s “serialize” function, similar to:
# http://php.net/manual/en/function.unserialize.php
# Originally from: http://blog.desudesudesu.org/?p=1046
#
# Copyright (c) 2014, 2016
#   mirabilos <t.glaser@tarent.de>
# Copyright (c) 2009
#   L Campbell <llc2w@virginia.edu>
#
# Provided that these terms and disclaimer and all copyright notices
# are retained or reproduced in an accompanying document, permission
# is granted to deal in this work without restriction, including un-
# limited rights to use, publicly perform, distribute, sell, modify,
# merge, give away, or sublicence.
#
# This work is provided "AS IS" and WITHOUT WARRANTY of any kind, to
# the utmost extent permitted by applicable law, neither express nor
# implied; without malicious intent or gross negligence. In no event
# may a licensor, author or contributor be held liable for indirect,
# direct, other damage, loss, or other issues arising in any way out
# of dealing in the work, even if advised of the possibility of such
# damage or existence of a defect, except proven that it results out
# of said person's immediate fault when using the work as intended.

def unserialize(s):
    return _unserialize_var(s)[0]

def _unserialize_var(s):
    return (
        { 'i' : _unserialize_int
        , 'b' : _unserialize_bool
        , 'd' : _unserialize_double
        , 'N' : _unserialize_null
        , 's' : _unserialize_string
        , 'a' : _unserialize_array
        , 'O' : _unserialize_object
        , 'C' : _unserialize_custom
        , 'R' : _unserialize_reference_value
        , 'r' : _unserialize_reference_object
        }[s[0]](s[2:]))

def _unserialize_int(s):
    x = s.partition(';')
    return (int(x[0]), x[2])

def _unserialize_bool(s):
    x = s.partition(';')
    return (x[0] == '1', x[2])

def _unserialize_double(s):
    x = s.partition(';')
    return (float(x[0]), x[2])

def _unserialize_null(s):
    return (None, s)

def _unserialize_string(s):
    (l, _, s) = s.partition(':')
    return (s[1:int(l)+1], s[int(l)+3:])

def _unserialize_array(s):
    (l, _, s) = s.partition(':')
    a, k, s = {}, None, s[1:]

    for i in range(0, int(l) * 2):
        (v, s) = _unserialize_var(s)

        if k is not None:
            a[k] = v
            k = None
        else:
            k = v

    return (a, s[1:])

def _unserialize_custom(s):
    (l, _, s) = s.partition(':')
    (n, _, s) = s.partition(':')
    (l, _, s) = s.partition(':')

    l = int(l)
    d = s[1:l+1]
    aa = { 'custom': n[1:-1], 'data': d }

    try:
        aa['parsed'] = unserialize(d)
    except Exception, e:
        aa['error'] = repr(e)

    return (aa, s[l+2:])

def _unserialize_object(s):
    (l, _, s) = s.partition(':')
    (n, _, s) = s.partition(':')
    (l, _, s) = s.partition(':')
    a, k, s = {}, None, s[1:]

    for i in range(0, int(l) * 2):
        (v, s) = _unserialize_var(s)

        if k is not None:
            a[k] = v
            k = None
        else:
            k = v

    aa = { 'class': n[1:-1], 'data': a }
    return (aa, s[1:])

# we should probably decode that, but JSON doesn’t support it anyway
# cf. http://www.phpinternalsbook.com/classes_objects/serialization.html
def _unserialize_reference(what, s):
    x = s.partition(';')
    return (['reference', what, int(x[0])], x[2])

def _unserialize_reference_value(s):
    return _unserialize_reference('value', s)

def _unserialize_reference_object(s):
    return _unserialize_reference('object', s)


# this is mostly for debugging (php_unserialize.py <foo | less)
if __name__ == "__main__":
    import sys
    import json

    serialised = sys.stdin.read()
    unserialised = unserialize(serialised)
    # we need sort_keys because they are internally unordered anyway
    print json.dumps(unserialised, sys.stdout, indent=True, sort_keys=True)
