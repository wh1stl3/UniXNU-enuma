"""Exact protected contrast and text request scopes. A pending record grants no device execution."""
SCOPE=dict(experiment='native-roi-contrast-restore-v1',origin_x=0,origin_y=0,width=128,height=8,
    required_current_el=1,hold_us=500000,hold_calls_max=1,mdp_reads_max=660,
    mdp_wait_calls_max=4,mdp_wait_us=100000,framebuffer_reads_max=3072,
    framebuffer_writes_max=2048,barriers_max=3,cache_line_operations=0,
    mdp_base='0xae00000',mdp_bytes='0x85000',cpu_splash_view_base='0x9c000000',cpu_splash_view_bytes='0x2400000',
    final_stage2_unproven=True,device_smmu_unproven=True,alpha_semantics_unproven=True,
    publish_gop=False,partition_writes=False,raw_media_local_only=True)

TEXT_SCOPE={**SCOPE,"experiment":"native-roi-uefi-text-restore-v1","height":32,
    "framebuffer_reads_max":12288,"framebuffer_writes_max":8192,
    "text":"UEFI","font":"fixed-five-by-seven","scale":4,"left_margin":4,"top_margin":2}

LOG_SCOPE={**SCOPE,"experiment":"native-dxe-cached-return-replay-v1","width":256,"height":96,
    "hold_us":2000000,"framebuffer_reads_max":73728,"framebuffer_writes_max":49152,
    "source":"Core point13 actual return snapshot","font":"three-by-five-hex","scale":4,
    "rows":3,"columns":16,"global_debug":False,"cached_replay":True}

LONG_LOG_SCOPE={**LOG_SCOPE,"experiment":"native-dxe-cached-return-replay-8s-v1","hold_us":8000000}

def scope_for_review(review):
    if review=="R-022": return LONG_LOG_SCOPE
    if review=="R-020": return LOG_SCOPE
    return TEXT_SCOPE if review=="R-019" else SCOPE
