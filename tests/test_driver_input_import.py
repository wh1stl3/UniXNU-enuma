"""Synthetic exporter/importer round trips; no XNU ABI or build claim."""
import importlib.util
import json
import unittest
import test_driver_inputs as fixtures
from pathlib import Path

spec=importlib.util.spec_from_file_location('importer',Path(__file__).resolve().parents[1]/'scripts/import_enuma_driver_inputs.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
exporter=fixtures.m

class ImportTests(unittest.TestCase):
    setUp=fixtures.ExportTests.setUp
    save=fixtures.ExportTests.save
    export=fixtures.ExportTests.export

    def bundle(self):
        self.manifest=self.export();self.package=self.base/'output'
        self.report=dict(status='passed',platform_build_and_link_passed=True,
            platform_kernel_sha256=exporter.sha(self.kernel),driver_compile_records={'compile.json':self.digest})
        self.bind()

    def bind(self):
        (self.package/'manifest.json').write_text(json.dumps(self.manifest))
        self.report['driver_input_manifest_sha256']=exporter.sha(self.package/'manifest.json')
        self.report_path=self.base/'report.json';self.report_path.write_text(json.dumps(self.report))

    def run_import(self):
        return m.import_bundle(self.package,self.report_path,self.kernel,self.base/'imported')

    def test_roundtrip(self):
        self.bundle();r=self.run_import()
        self.assertTrue(r['passed']);self.assertFalse(r['commands_executed'])
        self.assertFalse(r['private_abi_qualified']);self.assertFalse(r['kernel_linked'])
        args=r['templates'][0]['arguments']
        self.assertIn('-I${INPUTS}/generated',args);self.assertIn('${SDK}/.',args)
        self.assertEqual(args[-2:],['-o','${OUTPUT}'])
        self.assertEqual((self.base/'imported/tree/generated/config.h').read_bytes(),(self.source/'generated/config.h').read_bytes())

    def test_kernel_changed(self):
        self.bundle();self.kernel.write_bytes(b'other');self.assertRaisesRegex(ValueError,'identity mismatch',self.run_import)

    def test_manifest_changed(self):
        self.bundle();(self.package/'manifest.json').write_text('{}');self.assertRaisesRegex(ValueError,'manifest not bound',self.run_import)

    def test_header_changed(self):
        self.bundle();(self.package/'tree/generated/config.h').write_text('other');self.assertRaisesRegex(ValueError,'checksum',self.run_import)

    def test_extra_file(self):
        self.bundle();(self.package/'tree/extra.h').write_text('extra');self.assertRaisesRegex(ValueError,'unlisted',self.run_import)

    def test_wrong_final_record(self):
        self.bundle();self.report['driver_compile_records']['compile.json']='0'*64;self.bind()
        self.assertRaisesRegex(ValueError,'final kernel',self.run_import)

    def test_false_qualification(self):
        self.bundle();self.manifest['private_storage_abi_qualified']=True;self.bind()
        self.assertRaisesRegex(ValueError,'overstates',self.run_import)

    def test_tree_symlink(self):
        self.bundle();(self.package/'tree').rename(self.base/'redirect')
        (self.package/'tree').symlink_to(self.base/'redirect',target_is_directory=True)
        self.assertRaisesRegex(ValueError,'regular directory',self.run_import)

    def test_traversal(self):
        self.bundle();self.manifest['files']['../escape']='0'*64;self.bind()
        self.assertRaisesRegex(ValueError,'canonical',self.run_import)

    def test_duplicate_record(self):
        self.bundle();self.manifest['compile_records']*=2;self.bind()
        self.assertRaisesRegex(ValueError,'duplicate',self.run_import)

    def test_metadata_changed(self):
        self.bundle();self.manifest['compile_records'][0]['source_file']='other.cpp';self.bind()
        self.assertRaisesRegex(ValueError,'source identity',self.run_import)

    def test_existing_output(self):
        self.bundle();self.run_import();self.assertRaises(FileExistsError,self.run_import)

    def test_plugin_rejected(self):
        self.record['arguments']+=['-fplugin=hidden'];self.save();self.bundle()
        self.assertRaisesRegex(ValueError,'indirect',self.run_import)

    def test_target_preserved(self):
        self.record['arguments']+=['-target','arm64-apple-ios17.0','-x','c++'];self.save();self.bundle()
        self.assertEqual(self.run_import()['templates'][0]['arguments'][-4:],['-target','arm64-apple-ios17.0','-x','c++'])

if __name__=='__main__':unittest.main()
