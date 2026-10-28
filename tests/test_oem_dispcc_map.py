import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_oem_dispcc_map import LINE,BASE,SIZE,FAULT,source_check,RECORD
from oem_runtime_candidate import limits_for
from oem_exit_clock import SCOPES

class DispCc(unittest.TestCase):
    def test_real_arm64_descriptor_abi(self):
        import subprocess,tempfile
        root=Path(__file__).resolve().parents[1]
        inc=root/'firmware/Mu_Basecore/MdePkg/Include'
        with tempfile.TemporaryDirectory() as td:
            td=Path(td);c=td/'abi.c'
            c.write_text('''#include <Library/MemoryMapLib.h>
_Static_assert(sizeof(EFI_MEMORY_REGION_DESCRIPTOR)==72,"descriptor size");
_Static_assert(__builtin_offsetof(EFI_MEMORY_REGION_DESCRIPTOR,Address)==32,"address");
_Static_assert(__builtin_offsetof(EFI_MEMORY_REGION_DESCRIPTOR,Length)==40,"length");
_Static_assert(__builtin_offsetof(EFI_MEMORY_REGION_DESCRIPTOR,HobOption)==48,"HOB");
_Static_assert(__builtin_offsetof(EFI_MEMORY_REGION_DESCRIPTOR,ResourceType)==52,"resource");
_Static_assert(__builtin_offsetof(EFI_MEMORY_REGION_DESCRIPTOR,ResourceAttribute)==56,"cache");
_Static_assert(__builtin_offsetof(EFI_MEMORY_REGION_DESCRIPTOR,MemoryType)==60,"type");
_Static_assert(__builtin_offsetof(EFI_MEMORY_REGION_DESCRIPTOR,ArmAttributes)==64,"ARM");
_Static_assert(AddDev==2 && MMAP_IO==1 && UNCACHEABLE==0x400 && MmIO==11 && NS_DEVICE==6,"attributes");
''')
            subprocess.run(['/usr/bin/clang','-target','aarch64-unknown-windows-msvc','-ffreestanding','-Wall','-Wextra','-Werror','-I'+str(inc),'-I'+str(inc/'AArch64'),'-I'+str(root/'firmware/Silicon/Silicium/SiliciumPkg/Include'),'-c',str(c),'-o',str(td/'abi.obj')],check=True)

    def test_scope_keeps_exception_budget_and_no_timing_classification(self):
        self.assertEqual(limits_for('oem-exception-v11'),limits_for('oem-exception-dispcc-v12'))
        self.assertNotIn('oem-exception-dispcc-v12',SCOPES)

    def test_fixed_range_covers_fault_and_excludes_neighbors(self):
        self.assertEqual((BASE,SIZE),(0xaf00000,0x20000))
        self.assertTrue(BASE<=FAULT<BASE+SIZE)
        self.assertEqual(len(RECORD),72)

    def test_original_generated_map_rejects_and_patch_is_single_addition(self):
        # Reconstruct the fixed generated source from current baseline and
        # its existing map patches, without requiring historical build outputs.
        import subprocess,tempfile
        root=Path(__file__).resolve().parents[1]
        rel='Platforms/Xiaomi/enumaPkg/Library/MemoryMapLib/MemoryMapLib.c'
        with tempfile.TemporaryDirectory() as td:
            td=Path(td);p=td/rel;p.parent.mkdir(parents=True)
            p.write_bytes((root/'firmware'/rel).read_bytes().replace(b'\r\n',b'\n'))
            subprocess.run(['git','init','-q',str(td)],check=True)
            for patch in ['display-mdp-map.patch','ramoops-console-map.patch']:
                subprocess.run(['git','apply',str(root/'firmware/patches'/patch)],cwd=td,check=True)
            before=p.read_text();self.assertRaises(ValueError,source_check,before)
            subprocess.run(['git','apply',str(root/'firmware/patches/display-dispcc-map.patch')],cwd=td,check=True)
            after=p.read_text();source_check(after)
            self.assertEqual(after.replace(LINE,''),before)
            for bad in [after.replace(LINE,''),after+LINE,after.replace('0x20000ULL, AddDev','0x1000ULL, AddDev'),after.replace('"DISP_CC", 0xaf00000','"DISP_CC", 0xae00000'),after.replace('"DISP_CC", 0xaf00000ULL, 0x20000ULL, AddDev','"DISP_CC", 0xaf00000ULL, 0x20000ULL, AddMem')]:
                self.assertRaises(ValueError,source_check,bad)

if __name__=='__main__':unittest.main()
