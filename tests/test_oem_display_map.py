import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_oem_display_map import REGIONS,NEGATIVES,MAP,line,source_check,require_evidence
from oem_runtime_candidate import limits_for
from oem_exit_clock import SCOPES

class DisplayMap(unittest.TestCase):
    def test_real_patch_chain_and_unrelated_change_rejection(self):
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as td:
            td=Path(td);p=td/MAP;p.parent.mkdir(parents=True)
            p.write_bytes((root/'firmware'/MAP).read_bytes().replace(b'\r\n',b'\n'))
            subprocess.run(['git','init','-q',str(td)],check=True)
            for name in ('display-mdp-map.patch','ramoops-console-map.patch','display-dispcc-map.patch','display-resource-map.patch'):
                patch=str(root/'firmware/patches'/name)
                subprocess.run(['git','apply','--check',patch],cwd=td,check=True)
                subprocess.run(['git','apply',patch],cwd=td,check=True)
            text=p.read_text();source_check(text)
            for region in REGIONS:
                for bad in (text.replace(line(region),''),text+line(region),text.replace(line(region),line(region).replace('NS_DEVICE','WRITE_BACK')),text.replace(line(region),line(region).replace(hex(region[2]),'0x100000'))):
                    self.assertRaises(ValueError,source_check,bad)
            self.assertRaises(ValueError,source_check,text.replace('"DXE Heap"','"changed"'))
    def test_admission_rejects_missing_wrong_or_unbound_evidence(self):
        bindings={n:'bound' for n in ('scripts/check_oem_display_map.py','scripts/check_oem_dispcc_map.py','tests/test_oem_display_map.py')}
        m=dict(passed=True,fd_sec_exact_match=True,regions=[dict(name=n,base=hex(b),size=hex(z),negative_checks=NEGATIVES) for n,b,z in REGIONS+(('DISP_CC',0xaf00000,0x20000),)])
        require_evidence(m,bindings)
        for i in range(4):
            bad=copy.deepcopy(m);bad['regions'][i]['base']='0x0';self.assertRaises(ValueError,require_evidence,bad,bindings)
            bad=copy.deepcopy(m);bad['regions'][i]['negative_checks']=[];self.assertRaises(ValueError,require_evidence,bad,bindings)
        self.assertRaises(ValueError,require_evidence,None,bindings)
        self.assertRaises(ValueError,require_evidence,m,{})
    def test_exception_budget_no_timing_inference(self):
        scope='oem-exception-display-map-v13'
        self.assertEqual(limits_for(scope),limits_for('oem-exception-v11'))
        self.assertNotIn(scope,SCOPES)

if __name__=='__main__':unittest.main()
