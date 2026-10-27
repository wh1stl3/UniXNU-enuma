import copy,json,sys,tempfile,unittest
from pathlib import Path
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from oem_runtime_candidate import LIMITS,SCOPE,PROGRESS_SCOPE,limits_for,validate,claim,sha

class Admission(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.out=self.root/'out/q';self.out.mkdir(parents=True)
        names=['scripts/run_oem_runtime_trial.py','scripts/oem_runtime_candidate.py','scripts/qualify_oem_runtime.py',
               'scripts/audit_oem_development_fd.py','firmware/source.c']
        for n in names:
            p=self.root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'source')
        (self.out/'image.img').write_bytes(b'qualified image fixture')
        c=dict(trial_id=str(uuid4()),session=7,selected_call=0,profile='oem-control',experiment=SCOPE)
        self.q=dict(passed=True,software_ready=True,scope=SCOPE,run_config=c,identity=dict(runtime=c),
                    runtime_limits=copy.deepcopy(LIMITS),source_bindings={n:sha(self.root/n) for n in names},
                    image_sha256=sha(self.out/'image.img'),image_bytes=(self.out/'image.img').stat().st_size)
        self.save()
    def tearDown(self):self.tmp.cleanup()
    def save(self):(self.out/'qualification.json').write_text(json.dumps(self.q))
    def test_valid_and_single_use(self):
        validate(self.root,self.out);claim(self.root,self.out,True)
        with self.assertRaises(FileExistsError):claim(self.root,self.out,True)
    def test_no_human(self):
        with self.assertRaises(ValueError):claim(self.root,self.out,False)
        self.assertFalse((self.root/'out/oem-runtime-attempts').exists())
    def test_image_changed(self):
        (self.out/'image.img').write_bytes(b'other')
        with self.assertRaises(ValueError):validate(self.root,self.out)
    def test_source_changed(self):
        (self.root/'firmware/source.c').write_bytes(b'other')
        with self.assertRaises(ValueError):validate(self.root,self.out)
    def test_scope_rejections(self):
        original=copy.deepcopy(self.q)
        for mutate in [lambda q:q.update(scope='stage10'),lambda q:q['run_config'].update(profile='oem-mmu-only'),
                       lambda q:q['run_config'].update(session=0),lambda q:q['runtime_limits'].update(max_boots=2),
                       lambda q:q['run_config'].update(selected_call=True),lambda q:q['source_bindings'].pop('firmware/source.c')]:
            self.q=copy.deepcopy(original);mutate(self.q);self.save()
            with self.assertRaises(ValueError):validate(self.root,self.out)
    def test_outside_output(self):
        with self.assertRaises(ValueError):validate(self.root,self.root)
    def test_progress_scope_and_budget(self):
        self.q['scope']=PROGRESS_SCOPE;self.q['run_config']['experiment']=PROGRESS_SCOPE
        self.q['runtime_limits']=limits_for(PROGRESS_SCOPE);self.save();validate(self.root,self.out)
        for key,value in [('max_windows',6),('max_total_hold_us',48000000)]:
            self.q['runtime_limits']=limits_for(PROGRESS_SCOPE);self.q['runtime_limits'][key]=value;self.save()
            self.assertRaises(ValueError,validate,self.root,self.out)

if __name__=='__main__':unittest.main()
