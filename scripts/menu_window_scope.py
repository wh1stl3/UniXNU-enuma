"""R025 experimental window; independent of all consumed log scopes."""
SCOPE=dict(experiment='unixnu-live-menu-window-v1',origin_x=64,origin_y=96,width=800,height=600,
    pixels=480000,menu_timeout_seconds=8,physical_input=False,full_unixnu_run=False,bds_reached=False,
    gop='transient-private-PixelBltOnly',raw_framebuffer_exposed=False,
    mdp_reads_max=660,mdp_wait_calls_max=4,mdp_wait_us=100000,
    framebuffer_reads_max=6720000,framebuffer_writes_max=6240000,
    present_writes_max=5760000,restore_writes_max=480000,gop_present_calls_max=8192,barriers_max=8194,
    mdp_base='0xae00000',mdp_bytes='0x85000',cpu_splash_view_base='0x9c000000',cpu_splash_view_bytes='0x2400000',
    required_current_el=1,required_cpu_policy='whole-frame-identity-WT',requirements_retained=22,
    cache_line_operations=0,partition_writes=False,raw_media_local_only=True,
    final_stage2_unproven=True,device_smmu_unproven=True,alpha_semantics_unproven=True,
    production_gop_admitted=False,return_codes={'1':'no store','2':'restored drawing fault or protocol cleanup failure','4':'restoration unestablished','5':'CPU window restored'})
