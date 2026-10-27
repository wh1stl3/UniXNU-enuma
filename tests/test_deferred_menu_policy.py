import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from firmware_audit_policy import omitted_oem_modules
from deferred_menu_scope import SCOPE
class FullMenuPolicy(unittest.TestCase):
 def setUp(self):
  recipe=json.loads((ROOT/'out/inherited-gop/qualified-dxe-log-8s-8680ea7/firmware-build.json').read_text())
  d=recipe['firmware_configuration']['defines'].copy()
  d.update(ENUMA_DEFERRED_MENU='1',ENUMA_FULL_MENU='1',ENUMA_BOUNDED_MENU='1',ENUMA_BOOT_LOG_REPLAY='0',ENUMA_NATIVE_ROUTE_CPU_TEXT='0',ENUMA_PROBE_JOURNAL_REPLAY='0')
  self.b=dict(deferred_menu=True,complete=True,fd_sha256='a'*64,profile='deferred-menu',deferred_menu_scope=copy.deepcopy(SCOPE),hardware_review_required='R-027',firmware_configuration={'defines':d},diagnostic_omitted_oem_modules=['CPRDxe','DisplayDxe','UFSDxe'])
 def test_exact(self):self.assertEqual(len(omitted_oem_modules(self.b,'a'*64)),3)
 def test_scope(self):
  for field,value in [('deferred_menu',False),('profile','menu-window'),('hardware_review_required','R-025'),('fd_sha256','b'*64),('deferred_menu_scope',{}),('diagnostic_omitted_oem_modules',['UFSDxe'])]:
   b=copy.deepcopy(self.b);b[field]=value
   with self.subTest(field=field),self.assertRaises(ValueError):omitted_oem_modules(b,'a'*64)
 def test_macro(self):
  for k in ['ENUMA_DEFERRED_MENU','ENUMA_FULL_MENU','ENUMA_BOUNDED_MENU','ENUMA_DIAG_STAGE','ENUMA_DIAG_DETAIL_POINT','ENUMA_DIAG_GUID_ONLY','ENUMA_DIAG_DISPATCH_FALLBACK','ENUMA_BOOT_LOG_REPLAY','ENUMA_PROBE_JOURNAL_REPLAY','ENUMA_NATIVE_ROUTE_CPU_PATTERN','ENUMA_NATIVE_ROUTE_CPU_POLICY']:
   b=copy.deepcopy(self.b);b['firmware_configuration']['defines'][k]='99'
   with self.subTest(macro=k),self.assertRaises(ValueError):omitted_oem_modules(b,'a'*64)
if __name__=='__main__':unittest.main()
