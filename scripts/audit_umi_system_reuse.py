import json,hashlib,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
from audit_inputs import parse_fdt,cells
specs=[('UniXNU-umi','https://github.com/reAAAq/UniXNU-umi.git','3eb72578597d2ca16471b172d45eddc096a34a04',[
 'LICENSE','NOTICE.md','source-lock.json','docs/BUILD.md','docs/validation.json',
 'scripts/umi_adt.py','scripts/make-umi-adt.py','package/UmiPlatformPower.cpp',
 'package/UmiUfsProbe.cpp','package/UmiNativeUfsHost.inc','package/UmiUfsRead.inc','package/UmiSmmuTakeover.h',
 'package/umi-hardware.json','overlay/Platforms/Xiaomi/umiPkg/Drivers/UmiRamPayloadDxe/UmiRamPayload.c',
 'bringup/tools/build_umi_prelink.py','bringup/tools/build_umi_data_display.py']),
 ('uefi-umi','https://github.com/reAAAq/uefi-umi.git','48bc41218c480519bfd299c22205f44e418df9d0',[
 'Platforms/Xiaomi/umiPkg/Drivers/UmiRamPayloadDxe/UmiRamPayload.c',
 'Platforms/Xiaomi/umiPkg/umi.dsc','Platforms/Xiaomi/umiPkg/Include/APRIORI.inc'])]
items=[]
for name,url,commit,files in specs:
 base=root/'out/sources'/name
 result={'repository':url,'evaluation_commit':commit,'local':str(base.relative_to(root)),
         'checkout_head':subprocess.check_output(['git','-C',str(base),'rev-parse','HEAD'],text=True).strip(),
         'files':{}}
 for rel in files:
  data=subprocess.check_output(['git','-C',str(base),'show',commit+':'+rel])
  result['files'][rel]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
 items.append(result)
lock={'scope':'read-only reference evaluation; not a dependency update or execution authorization',
      'references':items,'framework_pin_of_umi':'7b52e7968c76453cdc18b5aa174fc368d5293b91',
      'enuma_framework_unchanged':'5fdbd5d08518bc2d5c196264c56a377dd80cf5ca'}
(root/'config/system-reuse-sources.lock.json').write_text(json.dumps(lock,indent=2)+'\n')
u=json.loads((root/'out/sources/UniXNU-umi/package/umi-hardware.json').read_text())
enuma=json.loads((root/'reports/enuma-adt-fragment.json').read_text())
nodes=parse_fdt((root/'out/device/live-fdt.bin').read_bytes())
ufs=[{'path':name,'reg_cells':[hex(v) for v in cells(props.get('reg',b''))]} for name,props in nodes.items()
     if b'qcom,ufshc' in props.get('compatible',b'')]
report={'scope':'same-SoC source applicability evaluation; no enuma hardware success claimed',
 'source_lock':'config/system-reuse-sources.lock.json',
 'maintainer_claim':{'source':'https://unixnu.com/devices/umi','state':'Hello/Setup Assistant, UFS/root and persistent Data reported through attempt 80',
                     'independently_reproduced_on_enuma':False},
 'matching_observations':{'cpu_affinities':enuma['cpu_affinities'],
  'umi_cpu_affinities':[hex(v['affinity']) for v in u['cpus']],
  'virtual_timer_intid':[enuma['timer_intid'],u['timer']['virtual_timer_intid']],
  'GIC_distributor':[enuma['gic']['distributor_pa'],hex(u['gic']['distributor']['base'])],
  'GIC_redistributor':[enuma['gic']['redistributor_pa'],hex(u['gic']['redistributor']['base'])],
  'PSCI_method':[enuma['psci']['method'],u['psci']['method']],
  'enuma_ufs_nodes':ufs,'umi_ufs_controller_source_constant':'0x1d84000/0x3000'},
 'priority_reuse':['UmiRamPayloadDxe BlockIo/FAT bounds and handoff pattern',
                  'umi_adt.py hardware-versus-product identity and loader input composition',
                  'UmiPlatformPower original PMGR service ABI with explicit unsupported-operation failures',
                  'SM8250 UFS/SMMU takeover, descriptor/root publication and CPU display implementation'],
 'not_copied':['umi boot v1 format','12GiB DRAM banks or 0x130000000 owned-memory window',
               'userdata GPT geometry or partition-write procedures','1080x2340 GOP geometry/pitch',
               'FTS touchscreen/PMIC GPIO5 rail','private ABI/provenance, platform seed or recovery memory addresses'],
 'integration_gaps':['umi framework pin differs from modular enuma pin; package ABI/build integration must be reconciled',
                     'tested firmware pin differs from latest cloned firmware HEAD; use explicit tested commit for source selection',
                     'public BUILD documents required private storage ABI, trust/Data seed and firmware import records',
                     'enuma boot v3 combined ramdisk and real entry FDT need own transport validation',
                     'enuma display, UFS power/stream ownership and memory/partition layouts require own evidence'],
 'device_actions':False,'existing_pins_modified':False}
(root/'reports/enuma-umi-system-reuse.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: fixed umi sources and tested firmware pin; same-SoC applicability recorded, no integration or device claim')
