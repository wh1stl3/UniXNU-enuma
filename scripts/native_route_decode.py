"""Decode route categories using the predeclared common five-code clock windows."""
from native_mask_decode import decode as decode_clock
CATEGORIES={'1':'collection-or-contract-rejected','2':'runtime-or-stability-rejected','3':'topology-rejected','4':'pipeline-capture-or-layout-rejected','5':'stable-candidate-address-and-downstream-unproven'}
def decode(clock,plan):
    result=decode_clock(clock,plan)
    if result['stop_additional_trials']: return result
    code=result['warning_code']
    return dict(conclusion='route-category-inferred',category=CATEGORIES[str(code)],warning_code=code,stop_additional_trials=False,direct_register_log=False)
