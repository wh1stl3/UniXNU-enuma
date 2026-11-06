"""Offline scanout evidence inventory; never invoke device tools or infer geometry.

Exit 2 denotes missing entry-time geometry, not permission to substitute another
board's values. Captured Android log hints are distinguished from UEFI evidence.
"""
import hashlib
import json
from pathlib import Path
import sys
if sys.version_info < (3,11):
    import tomli
    sys.modules['tomllib']=tomli
from audit_inputs import parse_fdt, cells, strings

ROOT=Path(__file__).resolve().parents[1]


def main():
    inputs={}
    def read(name):
        data=(ROOT/name).read_bytes()
        inputs[name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
        return data
    blob=read('out/device/live-fdt.bin')
    if hashlib.sha256(blob).hexdigest()!='643aa3ec450139d38f8cde9a94bca6d9e8e75e752cb7aa992685d34267434c62':
        raise ValueError('unreviewed FDT sample')
    nodes=parse_fdt(blob);reserved=[];simple=[]
    for path,props in nodes.items():
        if b'simple-framebuffer' in props.get('compatible',b''):simple.append(path)
        if path.startswith('/reserved-memory/') and any(s in path for s in ('cont_splash','dfps')):
            values=cells(props['reg'])
            if len(values)!=4:raise ValueError('unsupported saved reservation')
            reserved.append({'node':path,'base':hex((values[0]<<32)|values[1]),
                'size':hex((values[2]<<32)|values[3]),'label':strings(props['label'])})
    collection=json.loads(read('out/device/collection.json'));results={x['name']:x for x in collection}
    absent=[]
    for name in ('framebuffer','drm-state'):
        data=read('out/device/'+name+'.stdout')
        matches=(len(data)==results[name]['bytes'] and
                 hashlib.sha256(data).hexdigest()==results[name]['sha256'])
        # A later framebuffer listing replaced the original empty attempt.
        # Do not attach that attempt's exit status to different bytes.
        text=data.decode(errors='replace').splitlines()
        markers_only=bool(text) and all(line.startswith('FILE:') for line in text)
        if data and not markers_only:raise ValueError('new saved geometry needs manual interpretation: '+name)
        absent.append({'capture':name,'original_collection_record':results[name],
            'matches_original_collection':matches,
            'current_exit_code':results[name]['exit_code'] if matches else None,
            'empty':not data,'file_labels_without_values':markers_only,
            'can_supply_scanout_geometry':False,
            'note':'Different current stdout: retain original metadata separately; no inferred status for replacement' if not matches else 'Original attempt metadata matches'})
    hints=[]
    for name in ('out/log-readback/reservation-device-02/dmesg.txt',
                 'out/device-tests/20261022T201404/post-dmesg.stdout'):
        data=read(name).decode(errors='replace')
        for line,text in enumerate(data.splitlines(),1):
            if 'cont_splash enabled in' in text:
                hints.append({'source':name,'line':line,'text':text,
                    'meaning':'Android continuous splash handoff hint; not custom UEFI entry geometry'})
    platform=json.loads(read('reports/enuma-platform-config.json'))
    observations=json.loads(read('reports/enuma-platform-observations.json'))
    missing=['entry_scanout_base','entry_stride_bytes','entry_pixel_format',
             'entry_linear_uncompressed_layout','entry_valid_pixel_span',
             'scanout_survival_during_custom_uefi']
    if any(platform['gop'][k] is not None for k in ('boot_framebuffer_address','boot_stride','boot_pixel_format')):
        raise ValueError('saved platform evidence changed; review instead of automatic qualification')
    report={'scope':'saved input audit only; no device commands, memory access or image generation',
        'inputs':inputs,'saved_fdt_reservations':reserved,'simple_framebuffer_nodes':simple,
        'unavailable_captures':absent,'android_splash_hints':hints,
        'known_android_modes':observations['panel']['drm_modes'],
        'panel_link_bpp_is_not_framebuffer_format':observations['panel']['link_bpp'],
        'missing_entry_time_evidence':missing,'simplefb_write_eligible':False,
        'candidate_generated':False,'memory_fields_changed':False,'verification_flags_changed':False,
        'next_observation':'Read-only current DRM/bootloader handoff evidence after device work resumes; if absent use bounded early logs, never guessed framebuffer/MMIO writes',
        'same_soc_references':'See enuma-simplefb-reuse-audit.json; alioth/elish are evaluated sources, not enuma runtime proof'}
    (ROOT/'reports/enuma-scanout-evidence-gap.json').write_text(json.dumps(report,indent=2)+'\n')
    print('STOP: 6 entry-time scanout facts missing; saved Android splash hints do not qualify SimpleFb writes; no candidate generated')
    return 2

if __name__=='__main__':raise SystemExit(main())
