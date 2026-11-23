# r55 dk=0 host candidate — 2026-11-23

Self-checked host build only; no device operation or independent verification.
r54's framebuffer diagnostic requires its own deep concurrency review before
deployment; r55 inherits it unchanged.

## Origin and override

The r54 snapshot `out/ufs-sm8250-fbfill3-20261123-r54/device/board.toml:72`
contains the baseline `kernel_args`, including `offline-legacy-cpu-present=1`
and `sheng-touch-hid=1`. `scripts/build-enuma-r48-fxdiagbp.py:29` appends
` enuma-fx-diag=1 enuma-bp=1` to the payload configuration;
`scripts/build-enuma-r52-fbfill.py:97` appends ` enuma-fb-fill=1`.
Later r53/r54 preserve that payload argument string.

`scripts/build-enuma-r55-dk0.py` copies r54's payload and replaces only its
`EFI/UniXNU/unixnu.toml` entry, appending ` dk=0` to the xnu args; it does
not edit board configuration. It uses the existing r48 packaging recipe.
The resulting payload member was read back and TOML-parsed; the script
asserts `r55_args == r54_args + " dk=0"` exactly.

```text
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 sheng-vsync=60 sheng-aks=1 amfi_get_out_of_my_way=1 sheng-disable-watchdogd=1 sheng-lite=1 sheng-touch-hid=1 enuma-fx-diag=1 enuma-bp=1 enuma-fb-fill=1 dk=0
```

Character diff: append exactly ` dk=0`; no removals or other changes.

## Mechanical evidence

All FAT member SHA-256 values, r54 → r55:

| Member | r54 | r55 |
| --- | --- | --- |
| `unixnu.toml` | `2903ab597ffd918ca329ae3baab08668e4f4852c98eeee887dfbd5ae92102df0` | `c6ba35f7ebd5e547ec8d6b7e914b4bc20ecfaf8cf1dc13f091ef0e624ce8f55a` |
| `Payloads/kernel.macho.trustcache` | `7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7` | same |
| `Payloads/scratch-data.img` | `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470` | same |
| `Payloads/kernel.macho` | `f0b63b593d9eb60d296a6510c7d362f3b3a07ea899970cde003417d7127756e7` | same |
| `Payloads/kernel.macho.adt` | `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457` | same |

`boot.img`: 169951232 bytes, SHA-256
`e288d0f1759769b945c6fa347e52a546cbd0010e0979a95a76f35b9e1f863b01`;
size delta versus r54 is zero. r54 boot SHA-256 is
`c4069bfa4e40fd3f20a497b0e4d15f6126897e9455ee8e1d5a7560d57c7e7504`.
All five r54 artifacts were rehashed unchanged after packaging. ADT bytes
match the r54 file and the payload member. `llvm-nm -u` reported no undefined
symbols, including weak, for both native and prelink Mach-O.

| Observation | Interpretation |
| --- | --- |
| Exactly ` dk=0` appended | Single payload argument change; no hardware outcome established. |
| Other payload members unchanged | Kernel, trust cache, scratch image and ADT remain r54's bytes. |
| Same boot size | Does not establish equivalent runtime behavior. |

Risk: `dk=0` runtime effect is not established; inherited r54 framebuffer
locking, timing and display behavior remain unverified. No deployment,
device execution, GUI, persistence or stage advancement is claimed.

Build, root with Python 3.11.18:

```sh
wsl -u root -- bash -lc 'cd /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma && test ! -e out/ufs-sm8250-dk0-20261123-r55 && /home/wh1stl3/.local/bin/python3 scripts/build-enuma-r55-dk0.py --r55'
```

The previous incomplete attempt was retained as
`out/ufs-sm8250-dk0-20261123-r55.incomplete`.
