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
    p.add_argument('--clock-calibration',type=Path)
    a=p.parse_args();directory=a.qualification.resolve();q,image=validate(ROOT,directory)
    if not a.execute:
        print('PASS: offline candidate binding; no device commands');return
    if not a.human_ready:raise ValueError('current filming and manual recovery readiness required')
    from oem_exit_clock import SCOPES,require_plan,logic
    clock=q['scope'] in SCOPES
    if q['scope']==SCOPES[0]:
        if not a.clock_calibration:raise ValueError('fresh low/high calibration required before target execution')
        require_plan(q,json.loads(a.clock_calibration.read_text()))
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
    pre_clock=None
    def clock_after():
        if not clock:return
        from boot_origin import capture
        try:
            bound,samples=capture(lambda c:invoke('adb',['shell',c]),state['issued_monotonic'],pre_clock['boot_id_sha256'])
        except (ValueError,subprocess.TimeoutExpired) as exc:
            state['clock_observation_valid']=False;state['clock_observation_error']=str(exc)
            return # Android/partition recovery passed; clock failure is not recovery failure.
        state['clock_observation_valid']=True
        (out/'post-boot-clock.local.json').write_text(json.dumps(samples,indent=2))
        observation=dict(scope=q['scope'],trial_id=q['run_config']['trial_id'],image_sha256=q['image_sha256'],logic_sha256=logic(q),
            observed_unix=time.time(),boot_id_changed=True,post_boot_clock=bound,qualification_sha256=sha(directory/'qualification.json'))
        (out/'clock-observation.json').write_text(json.dumps(observation,indent=2))
    try:
        android_check()
        if clock:
            from boot_origin import capture
            pre_clock,samples=capture(lambda c:invoke('adb',['shell',c]))
            (out/'pre-boot-clock.local.json').write_text(json.dumps(samples,indent=2))
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
        state['issued_monotonic']=time.monotonic()
        r=invoke('fastboot',['boot',windows],30)
        if r.returncode or b'FAILED' in r.stdout+r.stderr:raise ValueError('single boot transport failed; no retry')
        deadline=time.monotonic()+75;disconnected=False;returned=False;android_returned=False
        while time.monotonic()<deadline:
            r=subprocess.run([str(TOOLS/'fastboot.exe'),'devices'],capture_output=True,timeout=3)
            if r.returncode:raise ValueError('USB enumeration failed')
            present=any(line.split()[:1]==[serial] for line in r.stdout.decode().splitlines())
            events.append(dict(event='bound-fastboot-enumeration',present=present,elapsed=time.monotonic()))
            (out/'transport.json').write_text(json.dumps(events,indent=2))
            disconnected,returned=observe_fastboot_return(present,disconnected)
            if returned:break
            if disconnected and time.monotonic()<deadline:
                product=invoke('adb',['shell','getprop','ro.product.device'],2)
                if product.returncode==0 and product.stdout.strip()==b'enuma' and time.monotonic()<deadline:
                    completed=invoke('adb',['shell','getprop','sys.boot_completed'],2)
                    android_returned=completed.returncode==0 and completed.stdout.strip()==b'1'
                    if android_returned:break
            time.sleep(1)
        if android_returned:
            android_check();clock_after();state['observed_return_endpoint']='android';state['manual_recovery']=None;state['return_method']='pending-user-confirmation'
            save('android-recovered-visual-review-pending');return
        if not returned:raise ValueError('no observed disconnect and verified fastboot or Android return')
        if not fastboot_check():raise ValueError('return identity failed')
        save('fastboot-returned')
        if invoke('fastboot',['reboot']).returncode:raise ValueError('Android reboot failed')
        deadline=time.monotonic()+120
        while time.monotonic()<deadline:
            try:
                if adb('getprop sys.boot_completed')=='1':break
            except (ValueError,subprocess.TimeoutExpired):pass
            time.sleep(2)
        android_check();clock_after();save('android-recovered-visual-review-pending')
    except Exception as exc:
        state['error']=str(exc).replace(serial,'<enuma>')
        save('manual-recovery-needed' if mutated else 'preflight-rejected')
        raise

if __name__=='__main__':main()
