"""Compare current counter eligibility with fixed native code and prior observations."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    pin=next(x for x in json.loads((ROOT/'reports/enuma-native-display-diagnosis-sources.json').read_text())['files'] if x['path'].endswith('sde_hw_intf.c'))
    path=ROOT/'out/display-native-sources/sde_hw_intf.c';blob=path.read_bytes()
    if hashlib.sha256(blob).hexdigest()!=pin['sha256']:raise ValueError('native source changed')
    text=blob.decode();start=text.index('static void sde_hw_intf_v1_get_status(');end=text.index('static void sde_hw_intf_setup_misr',start);body=text[start:end]
    if 'INTF_STATUS) & BIT(0)' not in body or 'INTF_FRAME_COUNT' not in body or 'INTF_FRAME_LINE_COUNT_EN' in body:raise ValueError('native status behavior changed')
    relative='firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib/Evidence.c'
    current=(ROOT/relative).read_text();native=(ROOT/'firmware/diagnostics/EnumaDsiNativeProgress.h').read_text()
    if '(V->CounterEnable&3)!=3' not in current or '(X->CounterEnable&3)!=3' not in current:raise ValueError('current predicate changed; review before attributing')
    if '(Before[I].Enable & 3' in native:raise ValueError('historical native progress eligibility changed')
    strict=json.loads((ROOT/'reports/enuma-dsi-counters-device.json').read_text());progress=json.loads((ROOT/'reports/enuma-dsi-native-device.json').read_text())
    config=next(x for x in strict['pairs'] if x['predicate']=='configuration')
    if config['timing_classification']!='refused' or progress.get('bounded_two_window_progress_supported') is not True:raise ValueError('historical evidence differs')
    def sites(source,needle):return [i for i,line in enumerate(source.splitlines(),1) if needle in line]
    report=dict(scope='offline source/history consistency audit after S-011/S-012; no device action or predicate relaxation',
      source=pin,native_v1_status_function_line=text[:start].count('\n')+1,
      native_gate='INTF_STATUS bit0; reads FRAME_COUNT without requiring count-enable bits ==3',
      current_gate=dict(path=relative,sha256=hashlib.sha256((ROOT/relative).read_bytes()).hexdigest(),lines=sites(current,'CounterEnable&3'),predicate='both interfaces timing nonzero, enable&3==3, active bit0; repeated for stability'),
      historical_strict_counter_gate=config,historical_native_two_window_progress_supported=True,
      current_exact_counter_enable_value=None,current_first_status_observed=None,
      judgment='The inherited audit reinstates a stronger counter-enable precondition than native get_status and the historical successful native progress predicate. After non-Topology support, refresh/eligibility is the leading isolation target, not an established root cause.',
      alternatives=['metadata/PCD rejection','revision/mode or decode failure','successful sampling status0 is also non-Topology'],
      next='Classify RefreshMode10 versus its complement using a separately qualified new diagnostic; only then review exact native activity/dual-link criteria. Do not simply remove the gate to obtain PASS.',
      limitations='Historical compound timing is not a numeric counter dump, and old/new launches need not inherit identical state; native-source behavior alone does not prove this launch reached the gate.',
      refutation='First status outside RefreshMode10, or valid status0, or directly observed eligible counters would lower this hypothesis.')
    (ROOT/'reports/enuma-video-counter-gate-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: fixed native status behavior and historical strict/native predicate difference verified; current values remain unknown')


if __name__=='__main__':main()
