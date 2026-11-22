#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Patch isolated IOUserClient source, never the upstream tree."""
import re

def patch(source):
    anchor = '#include "IOKitKernelInternal.h"'
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor + '\nextern "C" void enuma_match_record(unsigned int);')
    names = (
        'is_io_service_get_matching_services_ool',
        'is_io_service_get_matching_services_bin',
        'is_io_service_get_matching_service_ool',
        'is_io_service_get_matching_service_bin',
        'is_io_service_add_notification_bin',
        'is_io_service_add_notification_bin_64',
        'is_io_service_add_notification_ool',
        'is_io_service_add_notification_ool_64',
    )
    for name in names:
        match = re.search(r'\n' + name + r'\s*\([^;]*?\)\s*\n\{', source)
        assert match, name
        start = match.end()
        depth, end = 1, start
        while depth:
            depth += (source[end] == '{') - (source[end] == '}')
            end += 1
        body = source[start:end - 1]
        test = 'v == KERN_SUCCESS && *result == KERN_SUCCESS' if name.endswith(('_ool', '_ool_64')) else 'v == KERN_SUCCESS'
        prefix = ('\n\tenuma_match_record(0);\n'
                  '\tauto enuma_match_finish = [&](kern_return_t v) -> kern_return_t {\n'
                  '\t\tif (' + test + ') enuma_match_record(1);\n'
                  '\t\treturn v;\n\t};\n')
        body, n = re.subn(r'(?m)^([ \t]*)return\s+([^;]+);',
                          r'\1return enuma_match_finish(\2);', body)
        assert n, name
        source = source[:start] + prefix + body + source[end - 1:]
    return source
