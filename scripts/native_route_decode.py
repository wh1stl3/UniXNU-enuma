"""Decode route categories using the predeclared common five-code clock windows."""
from native_mask_decode import decode as decode_clock
CATEGORIES={'1':'collection-or-contract-rejected','2':'runtime-or-stability-rejected','3':'topology-rejected','4':'pipeline-capture-or-layout-rejected','5':'stable-candidate-address-and-downstream-unproven'}
DETAIL_CATEGORIES={'1':'non-topology-or-contract-rejected','2':'ctl-selection-topology-rejected','3':'source-staging-topology-rejected','4':'mixer-or-layout-topology-rejected','5':'stable-candidate-address-and-downstream-unproven'}
STAGING_CATEGORIES={'1':'not-classified-as-staging-rejection','2':'border-only-normalized-two-source-route','3':'known-source-count-or-stage-encoding-rejected','4':'unknown-or-virtual-staging-fields','5':'mixer-count-or-duplicate-source-rejected'}
LAYOUT_CATEGORIES={'1':'not-classified-as-layout-rejection','2':'mixer-dim-or-blend-rejected','3':'mixer-processing-mode-rejected','4':'mixer-or-source-geometry-rejected','5':'mixer-left-right-assignment-rejected'}
BLEND_CATEGORIES={'1':'not-classified-as-blend-rejection','2':'dim-at-selected-source-stage','3':'dim-outside-selected-source-stage','4':'selected-blend-operation-rejected','5':'selected-constant-alpha-rejected'}
def decode(clock,plan,detail=False,staging=False,layout=False,blend=False):
    if type(blend) is not bool or (blend and not layout): raise ValueError('invalid blend scope')
    if type(layout) is not bool or (layout and (not detail or staging)): raise ValueError('invalid layout scope')
    if type(detail) is not bool: raise ValueError('invalid detail selector')
    if type(staging) is not bool or (staging and not detail): raise ValueError('invalid staging selector')
    result=decode_clock(clock,plan)
    if result['stop_additional_trials']: return result
    code=result['warning_code']
    return dict(conclusion='route-category-inferred',category=(BLEND_CATEGORIES if blend else LAYOUT_CATEGORIES if layout else STAGING_CATEGORIES if staging else DETAIL_CATEGORIES if detail else CATEGORIES)[str(code)],warning_code=code,stop_additional_trials=False,direct_register_log=False)
