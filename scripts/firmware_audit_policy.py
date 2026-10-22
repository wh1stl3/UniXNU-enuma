"""A missing OEM driver is permitted only for the explicit fixed diagnostic mode."""


def omitted_oem_modules(build, fd_sha256):
    flag=build.get('firmware_configuration',{}).get('defines',{}).get('ENUMA_DIAG_DISABLE_UFS','0')
    declared=build.get('diagnostic_omitted_oem_modules',[])
    if flag not in ('0','1'):
        raise ValueError('unsupported diagnostic UFS selection')
    if flag=='0':
        if declared:raise ValueError('driver omission without diagnostic mode')
        return frozenset()
    if (build.get('complete') is not True or build.get('fd_sha256')!=fd_sha256 or declared!=['UFSDxe']):
        raise ValueError('diagnostic omission needs matching completed FD and exact UFSDxe declaration')
    return frozenset(declared)
