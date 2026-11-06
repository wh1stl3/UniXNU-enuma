"""A missing OEM driver is permitted only for the explicit fixed diagnostic mode."""


def omitted_oem_modules(build, fd_sha256):
    full_defs=build.get('firmware_configuration',{}).get('defines',{})
    if full_defs.get('ENUMA_DEFERRED_MENU','0')!='0' or build.get('deferred_menu'):
        from deferred_menu_scope import SCOPE
        required={'ENUMA_DEFERRED_MENU':'1','ENUMA_FULL_MENU':'1','ENUMA_BOUNDED_MENU':'1','ENUMA_DIAG_SIMPLEFB':'1','ENUMA_DIAG_DISABLE_UFS':'1',
                  'ENUMA_DIAG_STAGE':'13','ENUMA_DIAG_DETAIL_POINT':'16','ENUMA_DIAG_GUID_ONLY':'1',
                  'ENUMA_DIAG_DISPATCH_FALLBACK':'0','ENUMA_DIAG_GOP_QUERY':'1','ENUMA_DIAG_GOP_STEP':'0',
                  'ENUMA_BOOT_LOG_REPLAY':'0','ENUMA_PROBE_JOURNAL_REPLAY':'0','ENUMA_NATIVE_ROUTE_CPU_TEXT':'0',
                  'ENUMA_NATIVE_ROUTE_CPU_PATTERN':'1','ENUMA_NATIVE_ROUTE_CPU_POLICY':'1',
                  'ENUMA_NATIVE_ROUTE_ALPHA_VIEW':'1'}
        if (build.get('deferred_menu') is not True or build.get('complete') is not True or
            build.get('fd_sha256')!=fd_sha256 or build.get('profile')!='deferred-menu' or
            build.get('deferred_menu_scope')!=SCOPE or build.get('hardware_review_required')!='R-027' or
            any(full_defs.get(k)!=v for k,v in required.items()) or
            build.get('diagnostic_omitted_oem_modules')!=['CPRDxe','DisplayDxe','UFSDxe']):
            raise ValueError('full application requires independent R027 scope; R026 is not reusable')
        return frozenset(['CPRDxe','DisplayDxe','UFSDxe'])
    if full_defs.get('ENUMA_FULL_MENU','0')!='0' or build.get('full_menu'):
        from full_menu_scope import SCOPE
        required={'ENUMA_FULL_MENU':'1','ENUMA_BOUNDED_MENU':'1','ENUMA_DIAG_SIMPLEFB':'1','ENUMA_DIAG_DISABLE_UFS':'1',
                  'ENUMA_DIAG_STAGE':'13','ENUMA_DIAG_DETAIL_POINT':'16','ENUMA_DIAG_GUID_ONLY':'1',
                  'ENUMA_DIAG_DISPATCH_FALLBACK':'0','ENUMA_DIAG_GOP_QUERY':'1','ENUMA_DIAG_GOP_STEP':'0',
                  'ENUMA_BOOT_LOG_REPLAY':'0','ENUMA_PROBE_JOURNAL_REPLAY':'0','ENUMA_NATIVE_ROUTE_CPU_TEXT':'0',
                  'ENUMA_NATIVE_ROUTE_CPU_PATTERN':'1','ENUMA_NATIVE_ROUTE_CPU_POLICY':'1',
                  'ENUMA_NATIVE_ROUTE_ALPHA_VIEW':'1'}
        if (build.get('full_menu') is not True or build.get('complete') is not True or
            build.get('fd_sha256')!=fd_sha256 or build.get('profile')!='full-menu' or
            build.get('full_menu_scope')!=SCOPE or build.get('hardware_review_required')!='R-026' or
            any(full_defs.get(k)!=v for k,v in required.items()) or
            build.get('diagnostic_omitted_oem_modules')!=['CPRDxe','DisplayDxe','UFSDxe']):
            raise ValueError('full application requires independent R026 scope; R025 is not reusable')
        return frozenset(['CPRDxe','DisplayDxe','UFSDxe'])
    menu_flag=build.get('firmware_configuration',{}).get('defines',{}).get('ENUMA_BOUNDED_MENU','0')
    if menu_flag!='0' or build.get('bounded_menu'):
        from menu_window_scope import SCOPE
        defs=build.get('firmware_configuration',{}).get('defines',{})
        required={'ENUMA_BOUNDED_MENU':'1','ENUMA_DIAG_SIMPLEFB':'1','ENUMA_DIAG_DISABLE_UFS':'1',
                  'ENUMA_DIAG_STAGE':'13','ENUMA_DIAG_DETAIL_POINT':'16','ENUMA_DIAG_GUID_ONLY':'1',
                  'ENUMA_DIAG_DISPATCH_FALLBACK':'0','ENUMA_DIAG_GOP_QUERY':'1','ENUMA_DIAG_GOP_STEP':'0',
                  'ENUMA_BOOT_LOG_REPLAY':'0','ENUMA_PROBE_JOURNAL_REPLAY':'0','ENUMA_NATIVE_ROUTE_CPU_TEXT':'0',
                  'ENUMA_NATIVE_ROUTE_CPU_PATTERN':'1','ENUMA_NATIVE_ROUTE_CPU_POLICY':'1',
                  'ENUMA_NATIVE_ROUTE_ALPHA_VIEW':'1'}
        if (build.get('bounded_menu') is not True or build.get('complete') is not True or
            build.get('fd_sha256')!=fd_sha256 or build.get('profile')!='menu-window' or
            build.get('menu_window_scope')!=SCOPE or build.get('hardware_review_required')!='R-025' or
            any(defs.get(k)!=v for k,v in required.items()) or
            build.get('diagnostic_omitted_oem_modules')!=['CPRDxe','DisplayDxe','UFSDxe']):
            raise ValueError('bounded menu requires independently bound R025 scope and exact diagnostic profile')
        return frozenset(['CPRDxe','DisplayDxe','UFSDxe'])
    flag=build.get('firmware_configuration',{}).get('defines',{}).get('ENUMA_DIAG_DISABLE_UFS','0')
    declared=build.get('diagnostic_omitted_oem_modules',[])
    simple=build.get('firmware_configuration',{}).get('defines',{}).get('ENUMA_DIAG_SIMPLEFB','0')
    pixel=build.get('diagnostic_pixel_preview',False)
    pixel_flag=build.get('firmware_configuration',{}).get('defines',{}).get('ENUMA_DIAG_PIXEL_PREVIEW','0')
    video=build.get('inherited_video_audit_read_only',False)
    pattern=build.get('native_route_cpu_pattern',False)
    text=build.get('native_route_cpu_text',False)
    replay=build.get('boot_log_replay',False)
    hold=build.get('boot_log_hold_seconds',2) if replay else 2
    defs=build.get('firmware_configuration',{}).get('defines',{})
    diagnostic=build.get('diagnostic_pixel_log',False)
    if type(diagnostic) is not bool or (diagnostic and (not replay or hold!=8 or defs.get('ENUMA_BOOT_LOG_REPLAY')!='3' or defs.get('ENUMA_PROBE_JOURNAL_REPLAY')!='1')):
        raise ValueError('unsupported diagnostic cached replay')
    attributed=build.get('attributed_pixel_log',False)
    if diagnostic and attributed: raise ValueError('conflicting cached replay profiles')
    inset=diagnostic or attributed
    if type(attributed) is not bool or (attributed and (not replay or hold!=8 or defs.get('ENUMA_BOOT_LOG_REPLAY')!='2')):
        raise ValueError('unsupported attributed cached replay')
    if type(text) is not bool or (text and not pattern) or defs.get('ENUMA_NATIVE_ROUTE_CPU_TEXT','0')!=str(int(text)): raise ValueError('unsupported native text declaration')
    if type(pattern) is not bool or defs.get('ENUMA_NATIVE_ROUTE_CPU_PATTERN','0')!=str(int(pattern)):
        raise ValueError('unsupported native pixel declaration')
    if hold not in (2,8) or (hold==8 and defs.get('ENUMA_BOOT_LOG_HOLD_US')!='8000000'): raise ValueError('unsupported cached hold duration')
    if type(replay) is not bool or (replay and (not pattern or text or defs.get('ENUMA_BOOT_LOG_REPLAY')!=('3' if diagnostic else '2' if attributed else '1') or defs.get('ENUMA_BOOT_JOURNAL')!='1')): raise ValueError('unsupported cached replay declaration')
    if pattern:
        required=['ENUMA_NATIVE_ROUTE_CPU_ROI','ENUMA_NATIVE_ROUTE_CPU_BARRIER','ENUMA_NATIVE_ROUTE_CPU_READ',
                  'ENUMA_NATIVE_ROUTE_CPU_POLICY','ENUMA_NATIVE_ROUTE_CPU_STAGE1','ENUMA_NATIVE_ROUTE_ALPHA_VIEW',
                  'ENUMA_NATIVE_ROUTE_GLOBAL_OUTPUT','ENUMA_NATIVE_ROUTE_STRUCTURE','ENUMA_NATIVE_ROUTE_AUDIT']
        contract=build.get('inherited_video_compiled_contract',{})
        if inset and build.get('attributed_pixel_scope')!={'origin_x':64,'origin_y':96,'width':320,'height':160,'hold_us':8000000,'barriers_max':3}:
            raise ValueError('attributed pixel bounds mismatch')
        if (video is not False or build.get('hardware_review_required')!=('R-024' if diagnostic else 'R-023' if attributed else 'R-022' if replay and hold==8 else 'R-020' if replay else 'R-019' if text else 'R-018') or
            any(defs.get(k)!='1' for k in required) or
            any(type(contract.get(k)) is not type(v) or contract.get(k)!=v for k,v in dict(maximum_read_callbacks=660,maximum_wait_calls=5,
                maximum_framebuffer_reads=153600 if inset else 73728 if replay else 12288 if text else 3072,framebuffer_writes=102400 if inset else 49152 if replay else 8192 if text else 2048,pixel_access=True,
                cache_maintenance=False,protocol_published=False).items())):
            raise ValueError('native pixel requires protected R-018/R-019 bounded profile; not execution approval')
    control=build.get('inherited_video_entry_control',False)
    if type(control) is not bool or (control and not video): raise ValueError('unsupported video entry control')
    terminal=build.get('inherited_video_terminal',False)
    if type(terminal) is not bool or (terminal and (not (video or pattern) or build.get('diagnostic_dispatch_completion_fallback') is not False or build.get('diagnostic_gop_query')!=1)) or (pattern and not terminal):
        raise ValueError('unsupported video terminal profile')
    if type(video) is not bool: raise ValueError('unsupported video audit declaration')
    topology=build.get('inherited_video_topology_query',0)
    topology_flag=build.get('firmware_configuration',{}).get('defines',{}).get('ENUMA_VIDEO_TOPOLOGY_QUERY','0')
    if (type(topology) is not int or topology not in (0,1,2) or topology_flag!=str(topology) or
        (topology and (not video or not terminal or control))):
        raise ValueError('unsupported topology status query profile')
    target=build.get('inherited_video_reason_target',0);query=build.get('inherited_video_reason_query',0)
    defs=build.get('firmware_configuration',{}).get('defines',{})
    if (type(target) is not int or target not in range(5) or type(query) is not int or query not in (0,1,2) or
        bool(target)!=bool(query) or defs.get('ENUMA_VIDEO_REASON_TARGET','0')!=str(target) or defs.get('ENUMA_VIDEO_REASON_QUERY','0')!=str(query) or
        (target and (not video or not terminal or control or topology))):
        raise ValueError('unsupported first-reason profile')
    if (video or pattern) and (simple!='1' or pixel or build.get('diagnostic_gop_step')!=0 or
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
            build.get('diagnostic_simplefb_metadata_only') is not (not pixel and not video and not pattern) or declared!=['CPRDxe','DisplayDxe','UFSDxe']):
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
