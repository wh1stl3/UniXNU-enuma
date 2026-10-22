import copy
import sys
from pathlib import Path
import tomllib
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_firmware_source import check_board_contract

class R002BoardTests(unittest.TestCase):
    def setUp(self):
        self.board=tomllib.loads((Path(__file__).resolve().parents[1]/'board.toml').read_text())
        self.old={k:v for k,v in self.board.items() if k not in ('firmware','diagnostics')}

    def test_exact_configuration(self):
        check_board_contract(self.board,self.old)

    def test_no_extra_address_size_enable_or_unknown_field(self):
        for key,value in [('physical_base','0x9fff6000'),('size','0x10000'),
                          ('enabled',True),('other',False)]:
            with self.subTest(key=key):
                board=copy.deepcopy(self.board)
                board['diagnostics']['persistent_log'][key]=value
                with self.assertRaises(AssertionError):check_board_contract(board,self.old)

    def test_legacy_memory_still_checked(self):
        board=copy.deepcopy(self.board)
        board['extra']={'physical_base':'0x12340000'}
        with self.assertRaises(AssertionError):check_board_contract(board,self.old)
