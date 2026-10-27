import importlib.util,json,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('driver_inputs',Path(__file__).resolve().parents[1]/'scripts/ci/driver_inputs.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.base=Path(self.tmp.name)
        self.source=self.base/'source';self.source.mkdir();self.sdk=self.base/'SDK';self.sdk.mkdir()
        (self.sdk/'private.h').write_text('do not export SDK')
        (self.source/'generated').mkdir();(self.source/'generated/config.h').write_text('#define REAL_INPUT 1\n')
        (self.source/'driver.cpp').write_text('#include "config.h"\n')
        self.kernel=self.base/'kernel';self.kernel.write_bytes(b'fixture only')
        self.record=dict(directory=str(self.source),file='driver.cpp',arguments=['clang++','-Igenerated','-isysroot',str(self.sdk),'-c','driver.cpp','-o','driver.o'])
        self.save()
    def save(self):
        (self.source/'compile.json').write_text(json.dumps(self.record)+',\n');self.digest=m.sha(self.source/'compile.json')
    def export(self):return m.export_inputs(self.source,self.base/'output',self.kernel,['compile.json'],{'compile.json':self.digest},self.sdk)
    def test_capture(self):
        r=self.export();self.assertEqual(len(r['files']),3);self.assertEqual(r['kernel_sha256'],m.sha(self.kernel))
        self.assertEqual(len(r['external_inputs']),1);self.assertFalse((self.base/'output/tree/private.h').exists())
    def test_record_changed(self):
        (self.source/'compile.json').write_text('{}');self.assertRaises(ValueError,self.export)
    def test_external_include(self):
        self.record['arguments']+=['-I',str(self.base)];self.save();self.assertRaises(ValueError,self.export)
    def test_response_file(self):
        self.record['arguments']+=['@hidden.rsp'];self.save();self.assertRaises(ValueError,self.export)
    def test_missing_generated(self):
        self.record['arguments']+=['-include','absent.h'];self.save();self.assertRaises(FileNotFoundError,self.export)
    def test_escape_symlink(self):
        (self.source/'generated/escape.h').symlink_to(self.sdk/'private.h');self.assertRaises(ValueError,self.export)
    def test_output_in_source(self):
        self.assertRaises(ValueError,m.export_inputs,self.source,self.source/'out',self.kernel,['compile.json'],{'compile.json':self.digest},self.sdk)
    def test_existing_output(self):
        self.export();self.assertRaises(FileExistsError,self.export)
    def test_normalized_include(self):
        (self.source/'scratch').mkdir();self.record['arguments']+=['-I',str(self.source/'scratch/../generated')];self.save()
        self.assertEqual(len(self.export()['files']),3)
    def test_indirect_module(self):
        self.record['arguments']+=['-fmodule-map-file=hidden.modulemap'];self.save();self.assertRaises(ValueError,self.export)
    def test_joined_include(self):
        self.record['arguments']+=['-includegenerated/config.h'];self.save();self.assertEqual(len(self.export()['files']),3)
    def test_nested_directory_link(self):
        (self.source/'generated/link').symlink_to(self.sdk,target_is_directory=True);self.assertRaises(ValueError,self.export)
    def test_internal_directory_link(self):
        (self.source/'other').mkdir();(self.source/'other/valid.h').write_text('header')
        (self.source/'generated/link').symlink_to(self.source/'other',target_is_directory=True)
        self.assertIn('generated/link/valid.h',self.export()['files'])
    def test_directory_cycle(self):
        (self.source/'generated/self').symlink_to(self.source/'generated',target_is_directory=True);self.assertRaises(ValueError,self.export)
if __name__=='__main__':unittest.main()
