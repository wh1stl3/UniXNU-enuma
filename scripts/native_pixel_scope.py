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

def scope_for_review(review):
    return TEXT_SCOPE if review=="R-019" else SCOPE
