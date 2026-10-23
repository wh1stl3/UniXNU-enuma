"""A missing OEM driver is permitted only for the explicit fixed diagnostic mode."""


def omitted_oem_modules(build, fd_sha256):
    flag=build.get('firmware_configuration',{}).get('defines',{}).get('ENUMA_DIAG_DISABLE_UFS','0')
    declared=build.get('diagnostic_omitted_oem_modules',[])
    simple=build.get('firmware_configuration',{}).get('defines',{}).get('ENUMA_DIAG_SIMPLEFB','0')
    if simple not in ('0','1'):raise ValueError('unsupported SimpleFb diagnostic mode')
    if simple=='1':
        if (flag!='1' or build.get('complete') is not True or build.get('fd_sha256')!=fd_sha256 or
            build.get('diagnostic_simplefb_metadata_only') is not True or declared!=['CPRDxe','DisplayDxe','UFSDxe']):
            raise ValueError('SimpleFb metadata mode needs exact omissions and matching completed FD')
        return frozenset(declared)
    if build.get('diagnostic_simplefb_metadata_only',False):raise ValueError('SimpleFb declaration without enabled mode')
    if flag not in ('0','1'):
        raise ValueError('unsupported diagnostic UFS selection')
    if flag=='0':
        if declared:raise ValueError('driver omission without diagnostic mode')
        return frozenset()
    if (build.get('complete') is not True or build.get('fd_sha256')!=fd_sha256 or declared!=['UFSDxe']):
        raise ValueError('diagnostic omission needs matching completed FD and exact UFSDxe declaration')
    return frozenset(declared)
