import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from analyze_video_topology_pair import analyze


class TopologyPairTests(unittest.TestCase):
    def pair(self):
        p=dict(topology_status_query=1,consumed=True,automatic_android_return=True,boot_returncode=0,firmware_commit='a'*40,image_sha256='b'*64,
               timing=dict(adb_return_seconds=21,boot_complete_seconds=35),recovery=dict(
               checks=dict(device='enuma',boot_completed='1',slot='_a',flash_locked='0',root_available=True),
               partitions=[dict(partition=n,device_and_backup_match=True) for n in ['boot_a','vendor_boot_a']]))
        n=copy.deepcopy(p);n.update(topology_status_query=2,image_sha256='c'*64);n['timing']=dict(adb_return_seconds=26,boot_complete_seconds=40)
        return p,n

    def test_both_consistent_directions_and_no_direct_claim(self):
        p,n=self.pair();r=analyze(p,n);self.assertEqual(r['conclusion'],'topology-status-supported');self.assertFalse(r['exact_status_observed'])
        p['timing'],n['timing']=n['timing'],p['timing'];r=analyze(p,n)
        self.assertEqual(r['conclusion'],'non-topology-status-supported');self.assertIn(0,r['supported_status_set']);self.assertTrue(r['successful_sample_not_excluded'])

    def test_equal_noisy_or_conflicting_signals_are_ambiguous(self):
        for a,b in [(21,35),(29,43),(26,30),(23,40)]:
            p,n=self.pair();n['timing']=dict(adb_return_seconds=a,boot_complete_seconds=b)
            self.assertEqual(analyze(p,n)['conclusion'],'ambiguous')

    def test_no_return_invalid_time_and_missing_recovery_reject(self):
        for key,bad in [('automatic_android_return',False),('consumed',False),('topology_status_query',1),('firmware_commit','d'*40),('image_sha256','b'*64)]:
            p,n=self.pair();n[key]=bad
            with self.subTest(key=key),self.assertRaises(ValueError):analyze(p,n)
        for bad in [None,float('nan'),float('inf'),76,-1,True]:
            p,n=self.pair();n['timing']['adb_return_seconds']=bad
            with self.subTest(bad=bad),self.assertRaises(ValueError):analyze(p,n)
        p,n=self.pair();n['recovery']['checks']['root_available']=False
        with self.assertRaises(ValueError):analyze(p,n)
        p,n=self.pair();n['recovery']['partitions']=[]
        with self.assertRaises(ValueError):analyze(p,n)
        p,n=self.pair();n['timing']['fastboot_return_seconds']=10
        with self.assertRaises(ValueError):analyze(p,n)
