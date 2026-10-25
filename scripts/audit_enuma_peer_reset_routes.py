"""Verify fixed peer source bytes and explicit reset/log route findings; no device."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def audit():
    lock=json.loads((ROOT/'config/enuma-elish-reset-sources.lock.json').read_text(encoding='utf-8'))
    references=lock['references'];checked=0
    def source(repo,path):
        rec=next(x for x in references if x['repository']=='https://github.com/'+repo)
        data=(ROOT/rec['files'][path]['cache_file']).read_bytes()
        return data.decode('utf-8'),rec['files'][path]['url']
    for ref in references:
        for path,item in ref['files'].items():
            data=(ROOT/item['cache_file']).read_bytes()
            if hashlib.sha256(data).hexdigest()!=item['sha256']:raise ValueError('source SHA mismatch: '+path)
            git_blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            if git_blob!=item['git_blob']:raise ValueError('Git blob mismatch: '+path)
            checked+=1
    probes=[
      ('enuma_log_is_pipa_reference','Tlrenhb/uefi-enuma','Platforms/Xiaomi/enumaPkg/Library/RamoopsLogLib/RamoopsLogLib.c',
       ['TODO(enuma)','VERBATIM COPY','PrepareWarmFastboot','PON_KPDPWR_S2_CTL','SCM_HALT_PMIC_ARB']),
      ('enuma_reset_still_unported','Tlrenhb/uefi-enuma','Platforms/Xiaomi/enumaPkg/enuma.dsc',
       ['TODO(enuma): umi also provides','UmiResetSystemLib','needs its own']),
      ('elish_unixnu_not_hardware_closure','hpadmx/UniXNU-elish','README.md',
       ['不能直接构建出可烧写产物','build-elish-uefi.sh']),
      ('elish_common_psci_binding','edk2-porting/edk2-msm','Silicon/Qualcomm/QcomPkg/QcomCommonDsc.inc',
       ['ArmSmcPsciResetSystemLib','FrameBufferSerialPortLib','QcomGeniSerialPortLib']),
      ('elish_upstream_psci_warm_not_board_fix','tianocore/edk2','ArmPkg/Library/ArmSmcPsciResetSystemLib/ArmSmcPsciResetSystemLib.c',
       ['ARM_SMC_ID_PSCI_FEATURES','ARM_SMC_ID_PSCI_SYSTEM_RESET2_AARCH64','ResetCold ();']),
      ('elish_linux_layout_differs','torvalds/linux','arch/arm64/boot/dts/qcom/sm8250-xiaomi-elish-common.dtsi',
       ['ramoops@b0000000','record-size = <0x1000>','console-size = <0x200000>','ecc-size = <16>']),
      ('umi_board_reset_reference','reAAAq/UniXNU-umi','overlay/Platforms/Xiaomi/umiPkg/Library/UmiResetSystemLib/UmiResetSystem.c',
       ['PSCI SYSTEM_RESET hung','SaveAndDisableInterrupts','WriteVerify','BoardReset (1)','0x82000902']),
      ('pipa_reader_early_copy','xVanTuring/UniXNU-pipa','package/linux-log/init.c',
       ['PSTORE','LOG.BIN','read only','qcom,force-warm-reboot']),
      ('pipa_reader_temp_boot_and_board_dtb','xVanTuring/UniXNU-pipa','package/linux-log/build-log-reader.py',
       ['qcom,force-warm-reboot','--cold','header v2'])]
    facts=[]
    for name,repo,path,needles in probes:
        text,url=source(repo,path)
        for needle in needles:
            if needle not in text:raise ValueError('fact changed: '+name+' '+needle)
        facts.append(dict(id=name,url=url,matched_line_numbers={s:text[:text.index(s)].count('\n')+1 for s in needles},
                          evidence_level='source fact / peer claim; not independent enuma execution'))
    report=dict(scope='fixed-source peer comparison; no firmware changes, physical access, boots or module loads',
                repositories=len(references),files_checked=checked,sha256_and_git_blob_match=True,facts=facts,
                enuma_hardware_baseline=dict(last_trial='S-018',hard_stop=True,recovered_android=True,firmware_pin_unchanged=True),
                conclusion='Board PMIC PON/SPMI/PS_HOLD reset + early temporary Linux reader is a concrete alternate chain; peer enuma/elish do not establish a solved enuma PSCI_RESET2 retention case',
                next_priority=['offline audit enuma-native PMIC/SCM/restart DT and match peer board-reset assumptions',
                               'separate minimal fresh write with already-returned cold path from persistence',
                               'qualify an enuma-owned early reader before any new persistent-log experiment'],
                not_authorized_by_reference=['pipa/umi SPMI constants or long-power-button reconfiguration','4MiB mapping/pmsg expansion','flash/slot/verified changes'],
                raw_media_local_only=True)
    (ROOT/'reports/enuma-elish-reset-route-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'PASS: {checked} fixed files across {len(references)} repositories; SHA256/Git blob and {len(facts)} source findings checked; no device actions')
if __name__=='__main__':audit()
