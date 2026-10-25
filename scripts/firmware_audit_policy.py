"""A missing OEM driver is permitted only for the explicit fixed diagnostic mode."""


def omitted_oem_modules(build, fd_sha256):
    flag=build.get('firmware_configuration',{}).get('defines',{}).get('ENUMA_DIAG_DISABLE_UFS','0')
    declared=build.get('diagnostic_omitted_oem_modules',[])
    simple=build.get('firmware_configuration',{}).get('defines',{}).get('ENUMA_DIAG_SIMPLEFB','0')
    pixel=build.get('diagnostic_pixel_preview',False)
    pixel_flag=build.get('firmware_configuration',{}).get('defines',{}).get('ENUMA_DIAG_PIXEL_PREVIEW','0')
    video=build.get('inherited_video_audit_read_only',False)
    if type(video) is not bool: raise ValueError('unsupported video audit declaration')
    if video and (simple!='1' or pixel or build.get('diagnostic_gop_step')!=0 or
                  build.get('diagnostic_gop_query') not in (1,2) or build.get('value_probe',{}).get('source')!='off' or
                  build.get('gop_backend_selftest_ram_only')):
        raise ValueError('video audit requires exact read-only query profile')
    if type(pixel) is not bool or pixel_flag not in ('0','1'):raise ValueError('unsupported pixel diagnostic declaration')
    if pixel:
        if (pixel_flag!='1' or simple!='1' or build.get('diagnostic_gop_step')!=13 or
            build.get('diagnostic_gop_query')!=1 or build.get('hardware_review_required')!='R-005'):
            raise ValueError('Pixel build audit requires exact protected step13 declaration; this is not execution approval')
    elif pixel_flag!='0':raise ValueError('pixel write flag without explicit pixel profile')
    if simple not in ('0','1'):raise ValueError('unsupported SimpleFb diagnostic mode')
    if simple=='1':
        if (flag!='1' or build.get('complete') is not True or build.get('fd_sha256')!=fd_sha256 or
            build.get('diagnostic_simplefb_metadata_only') is not (not pixel and not video) or declared!=['CPRDxe','DisplayDxe','UFSDxe']):
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
