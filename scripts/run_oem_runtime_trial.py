"""One temporary OEM boot. No flash, erase, slot changes or boot retries."""
import argparse,json,shlex,subprocess,time
from pathlib import Path
from oem_runtime_candidate import validate,claim,sha
from run_enuma_entry_probe import fastboot_value_matches,observe_fastboot_return

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT.parents[1]/'UniXNU-enuma'
TOOLS=Path('/mnt/d/Code/PortingiOSLegacy/common/tools/platform-tools')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--qualification',type=Path,required=True)
    p.add_argument('--execute',action='store_true')
    p.add_argument('--human-ready',action='store_true')
    a=p.parse_args();directory=a.qualification.resolve();q,image=validate(ROOT,directory)
    if not a.execute:
        print('PASS: offline candidate binding; no device commands');return
    if not a.human_ready:raise ValueError('current filming and manual recovery readiness required')
    local_state=ROOT/'out/device-tests/current.local.json'
    if local_state.exists() and json.loads(local_state.read_text()).get('phase') in (
        'manual-recovery-needed','entering-bootloader','boot-issued','fastboot-returned'):
        raise ValueError('local trial recovery unresolved')
    from enuma_paths import evidence_path
    previous=json.loads((ORIGINAL/'out/device-tests/current.local.json').read_text())
    if previous.get('phase')=='manual-recovery-needed':raise ValueError('previous recovery unresolved')
    backup=evidence_path(previous.get('recovery_backup_directory',previous['directory']),ORIGINAL)
    serial=json.loads((evidence_path(previous['directory'],ORIGINAL)/'target.local.json').read_text())['serial']
    if previous['slot']!='_a' or {b['partition'] for b in previous['backups']}!={'boot_a','vendor_boot_a'}:
        raise ValueError('unexpected recovery scope')
    for b in previous['backups']:
        if sha(backup/(b['partition']+'.bin'))!=b['sha256']:raise ValueError('backup changed')
    out=ROOT/'out/device-tests'/('oem-'+q['run_config']['trial_id']);out.mkdir(parents=True,exist_ok=False)
    (out/'target.local.json').write_text(json.dumps({'serial':serial}))
    events=[]
    def invoke(tool,args,timeout=10):
        start=time.monotonic()
        try:
            r=subprocess.run([str(TOOLS/(tool+'.exe')),'-s',serial,*args],capture_output=True,timeout=timeout)
        except subprocess.TimeoutExpired:
            r=subprocess.CompletedProcess(args,124,b'',b'bounded transport timeout')
        events.append(dict(tool=tool,args=[str(x) for x in args],elapsed=time.monotonic()-start,
                           returncode=r.returncode,output=(r.stdout+r.stderr).decode(errors='replace').replace(serial,'<enuma>')))
        (out/'transport.json').write_text(json.dumps(events,indent=2))
        return r
    def adb(command,root=False,timeout=10):
        r=invoke('adb',['shell',('su -c '+shlex.quote(command)) if root else command],timeout)
        if r.returncode:raise ValueError('ADB command failed')
        return r.stdout.decode().strip()
    def android_check():
        for prop,wanted in [('ro.product.device','enuma'),('sys.boot_completed','1'),
                            ('ro.boot.slot_suffix','_a'),('ro.boot.flash.locked','0')]:
            if adb('getprop '+prop)!=wanted:raise ValueError('Android predicate failed: '+prop)
        if 'uid=0(root)' not in adb('id',True):raise ValueError('root unavailable')
        for b in previous['backups']:
            if adb('sha256sum /dev/block/bootdevice/by-name/'+b['partition'],True,30).split()[0]!=b['sha256']:
                raise ValueError('partition differs from backup')
    def fastboot_check():
        return all(fastboot_value_matches(invoke('fastboot',['getvar',key]),key,val)
                   for key,val in [('product','enuma'),('current-slot','a'),('unlocked','yes')])
    state=dict(directory=str(out),recovery_backup_directory=str(backup),backups=previous['backups'],slot='_a',
               candidate=str(image),candidate_sha256=q['image_sha256'],partition_writes=False,boot_count=0)
    def save(phase):
        state['phase']=phase
        (out/'state.json').write_text(json.dumps(state,indent=2))
        (ROOT/'out/device-tests/current.local.json').write_text(json.dumps(state,indent=2))
        print(phase,flush=True)
    mutated=False
    try:
        android_check()
        q,image=claim(ROOT,directory,a.human_ready)
        save('preflight-complete')
        mutated=True;save('entering-bootloader')
        if invoke('adb',['reboot','bootloader']).returncode:raise ValueError('reboot transport failed')
        ready=False
        for _ in range(5):
            time.sleep(3)
            if fastboot_check():ready=True;break
        if not ready:raise ValueError('fastboot identity not confirmed')
        validate(ROOT,directory)
        state['boot_count']=1;save('boot-issued')
        # Windows fastboot requires a Windows image path even under WSL.
        windows=subprocess.check_output(['wslpath','-w',str(image)],text=True).strip()
        r=invoke('fastboot',['boot',windows],30)
        if r.returncode or b'FAILED' in r.stdout+r.stderr:raise ValueError('single boot transport failed; no retry')
        deadline=time.monotonic()+75;disconnected=False;returned=False
        while time.monotonic()<deadline:
            r=subprocess.run([str(TOOLS/'fastboot.exe'),'devices'],capture_output=True,timeout=3)
            if r.returncode:raise ValueError('USB enumeration failed')
            present=any(line.split()[:1]==[serial] for line in r.stdout.decode().splitlines())
            events.append(dict(event='bound-fastboot-enumeration',present=present,elapsed=time.monotonic()))
            (out/'transport.json').write_text(json.dumps(events,indent=2))
            disconnected,returned=observe_fastboot_return(present,disconnected)
            if returned:break
            time.sleep(1)
        if not returned:raise ValueError('no observed disconnect and verified fastboot return')
        if not fastboot_check():raise ValueError('return identity failed')
        save('fastboot-returned')
        if invoke('fastboot',['reboot']).returncode:raise ValueError('Android reboot failed')
        deadline=time.monotonic()+120
        while time.monotonic()<deadline:
            try:
                if adb('getprop sys.boot_completed')=='1':break
            except (ValueError,subprocess.TimeoutExpired):pass
            time.sleep(2)
        android_check();save('android-recovered-visual-review-pending')
    except Exception as exc:
        state['error']=str(exc).replace(serial,'<enuma>')
        save('manual-recovery-needed' if mutated else 'preflight-rejected')
        raise

if __name__=='__main__':main()
