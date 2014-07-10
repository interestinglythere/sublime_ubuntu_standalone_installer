#!/usr/bin/env python
# -*- coding: utf-8 -*-

INDENT = '   '
MAJOR_VERSION = 2
from sys import stderr


def main(args):
    if len(args) == 1:
        args.append(None)
    assert len(args) == 2
    infile, outfile = args
    print >> stderr, 'read yaml...'
    data = load_data_from_yaml(infile)
    print >> stderr, 'merge strings...'
    strings = merge_strings(data)
    print >> stderr, 'variable-substitute strings...'
    sub_strings(strings)
    print >> stderr, 'transform strings...'
    assignments = strings_to_assignments(strings)
    print >> stderr, 'sort strings...'
    assignments.sort()
    print >> stderr, 'write strings...'
    outcontents = ''.join(assignments)
    if outfile:
        writefile(outfile, outcontents)
    else:
        from sys import stdout
        stdout.write(outcontents)


def load_data_from_yaml(path):
    from yaml import load
    return load(file(path))


def writefile(path, contents):
    with file(path, 'w') as f:
        return f.write(contents)


def merge_strings(data):
    common = data['common']
    versioned = data[MAJOR_VERSION]

    # Insure no duplicates
    assert not [key for key in versioned if key in common]
    # Insure all lowercase keys
    assert all(key.islower() for key in versioned)
    assert all(key.islower() for key in common)

    strings = common.copy()
    strings.update(versioned)
    return strings


def sub_strings(strings):
    from re import compile, search
    general_search_pattern = compile(r'\$\((\w+?)\)')
    keys_to_check = strings.keys()

    def process_key(key0, seen_keys):
        if key0 in seen_keys:
            raise ValueError('Circular reference for key %r' % key0)
        val0 = strings[key0]
        if isinstance(val0, str):
            new_seen_keys = seen_keys + [key0]

            while True:
                m = search(general_search_pattern, val0)
                if not m:
                    break
                key1 = m.group(1)
                val1 = strings[key1]
                targeted_search_pattern = '$(%s)' % key1
                val0 = val0.replace(targeted_search_pattern, str(val1))
                if key1 in keys_to_check:
                    print >> stderr, INDENT + INDENT * len(seen_keys) + '└─ ' + key1
                    process_key(key1, new_seen_keys)
            strings[key0] = val0

        keys_to_check.remove(key0)

    while keys_to_check:
        key = keys_to_check[0]
        print >> stderr, INDENT + key
        process_key(key, [])


def strings_to_assignments(strings):
    return ['%s = %r\n' % (key.upper(), strings[key]) for key in strings.keys()]


if __name__ == '__main__':
    try:
        from sys import argv
        exit(main(argv[1:]))
    except (KeyboardInterrupt, EOFError), e:
        print >> stderr, e
        exit(1)
