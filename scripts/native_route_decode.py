"""Decode route categories using the predeclared common five-code clock windows."""
from native_mask_decode import decode as decode_clock
CATEGORIES={'1':'collection-or-contract-rejected','2':'runtime-or-stability-rejected','3':'topology-rejected','4':'pipeline-capture-or-layout-rejected','5':'stable-candidate-address-and-downstream-unproven'}
DETAIL_CATEGORIES={'1':'non-topology-or-contract-rejected','2':'ctl-selection-topology-rejected','3':'source-staging-topology-rejected','4':'mixer-or-layout-topology-rejected','5':'stable-candidate-address-and-downstream-unproven'}
STAGING_CATEGORIES={'1':'not-classified-as-staging-rejection','2':'border-only-normalized-two-source-route','3':'known-source-count-or-stage-encoding-rejected','4':'unknown-or-virtual-staging-fields','5':'mixer-count-or-duplicate-source-rejected'}
LAYOUT_CATEGORIES={'1':'not-classified-as-layout-rejection','2':'mixer-dim-or-blend-rejected','3':'mixer-processing-mode-rejected','4':'mixer-or-source-geometry-rejected','5':'mixer-left-right-assignment-rejected'}
BLEND_CATEGORIES={'1':'not-classified-as-blend-rejection','2':'dim-at-selected-source-stage','3':'dim-outside-selected-source-stage','4':'selected-blend-operation-rejected','5':'selected-constant-alpha-rejected'}
STRUCTURE_CATEGORIES={'1':'collection-or-contract-rejected','2':'runtime-or-stability-rejected','3':'route-or-geometry-rejected','4':'source-capture-or-layout-rejected','5':'stable-structure-blend-address-and-downstream-unproven'}

GEOMETRY_CATEGORIES={'1':'not-classified-as-stable-geometry-rejection','2':'stable-mixer-size-rejected','3':'stable-source-local-output-rejected','4':'stable-left-right-assignment-rejected','5':'stable-combined-mixer-width-rejected'}

GLOBAL_OUTPUT_CATEGORIES={'1':'collection-or-contract-rejected','2':'runtime-or-stability-rejected','3':'exact-global-coordinate-contract-rejected','4':'source-capture-or-layout-rejected','5':'stable-global-coordinate-structure-blend-address-and-downstream-unproven'}

GLOBAL_DETAIL_CATEGORIES={'1':'not-classified-as-source-decode-rejection','2':'source-geometry-or-coverage-rejected','3':'source-format-or-encoding-rejected','4':'source-address-or-layout-consistency-rejected','5':'source-security-or-other-decode-rejected'}

ALPHA_VIEW_CATEGORIES={'1':'collection-or-contract-rejected','2':'runtime-or-stability-rejected','3':'global-or-8888-alpha-contract-rejected','4':'source-capture-or-layout-rejected','5':'stable-8888-logical-structure-alpha-blend-address-and-downstream-unproven'}

CPU_STAGE1_CATEGORIES={'1':'prior-contract-or-cpu-context-rejected','2':'cpu-stage1-translation-or-permission-fault','3':'cpu-stage1-output-not-identity','4':'cpu-stage1-memory-attribute-not-write-through','5':'cpu-stage1-all-pages-read-write-identity-wt-data-and-smmu-unproven'}

CPU_ATTRIBUTE_CATEGORIES={'1':'not-classified-as-non-wt-attribute','2':'first-non-wt-attribute-normal-non-cacheable','3':'first-non-wt-attribute-normal-write-back','4':'first-non-wt-attribute-device','5':'first-non-wt-attribute-other-encoding'}

CPU_POLICY_CATEGORIES={'1':'prior-context-translation-or-identity-rejected','2':'all-pages-stage1-rw-identity-normal-nc','3':'all-pages-stage1-rw-identity-normal-wt','4':'all-pages-stage1-rw-identity-normal-wb','5':'all-pages-stage1-rw-identity-mixed-or-other-attributes'}

CPU_READ_CATEGORIES={'1':'prior-context-translation-or-identity-rejected','2':'normal-policy-differs-from-wt-baseline','3':'mixed-or-other-cache-policy-rejected','4':'single-word-read-contract-or-callback-rejected','5':'single-aligned-cpu-word-read-completed-no-data-export'}

CPU_BARRIER_CATEGORIES={**CPU_READ_CATEGORIES,'4':'single-barrier-or-word-read-contract-rejected','5':'single-dsb-sy-and-aligned-cpu-read-completed-no-data-export'}

def decode(clock,plan,detail=False,staging=False,layout=False,blend=False,structure=False,structure_detail=False,global_output=False,global_detail=False,alpha_view=False,cpu_stage1=False,cpu_attribute=False,cpu_policy=False,cpu_read=False,cpu_barrier=False):
    if type(cpu_barrier) is not bool or (cpu_barrier and not cpu_read): raise ValueError('invalid CPU barrier scope')
    if type(cpu_read) is not bool or (cpu_read and not cpu_policy): raise ValueError('invalid single CPU read scope')
    if type(cpu_policy) is not bool or (cpu_policy and (not cpu_stage1 or cpu_attribute)): raise ValueError('invalid whole-range CPU policy scope')
    if type(cpu_attribute) is not bool or (cpu_attribute and not cpu_stage1): raise ValueError('invalid CPU attribute scope')
    if type(cpu_stage1) is not bool or (cpu_stage1 and not alpha_view): raise ValueError('invalid CPU stage1 scope')
    if type(alpha_view) is not bool or (alpha_view and (not global_output or global_detail)): raise ValueError('invalid alpha view scope')
    if type(global_detail) is not bool or (global_detail and not global_output): raise ValueError('invalid global source detail scope')
    if type(global_output) is not bool or (global_output and (not structure or structure_detail)): raise ValueError('invalid global output scope')
    if type(structure_detail) is not bool or (structure_detail and not structure): raise ValueError('invalid structural geometry scope')
    if type(structure) is not bool or (structure and (detail or staging or layout or blend)): raise ValueError('invalid structure scope')
    if type(blend) is not bool or (blend and not layout): raise ValueError('invalid blend scope')
    if type(layout) is not bool or (layout and (not detail or staging)): raise ValueError('invalid layout scope')
    if type(detail) is not bool: raise ValueError('invalid detail selector')
    if type(staging) is not bool or (staging and not detail): raise ValueError('invalid staging selector')
    result=decode_clock(clock,plan)
    if result['stop_additional_trials']: return result
    code=result['warning_code']
    return dict(conclusion='route-category-inferred',category=(CPU_BARRIER_CATEGORIES if cpu_barrier else CPU_READ_CATEGORIES if cpu_read else CPU_POLICY_CATEGORIES if cpu_policy else CPU_ATTRIBUTE_CATEGORIES if cpu_attribute else CPU_STAGE1_CATEGORIES if cpu_stage1 else ALPHA_VIEW_CATEGORIES if alpha_view else GLOBAL_DETAIL_CATEGORIES if global_detail else GLOBAL_OUTPUT_CATEGORIES if global_output else GEOMETRY_CATEGORIES if structure_detail else STRUCTURE_CATEGORIES if structure else BLEND_CATEGORIES if blend else LAYOUT_CATEGORIES if layout else STAGING_CATEGORIES if staging else DETAIL_CATEGORIES if detail else CATEGORIES)[str(code)],warning_code=code,stop_additional_trials=False,direct_register_log=False)
