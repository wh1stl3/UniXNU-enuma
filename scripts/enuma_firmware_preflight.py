#!/usr/bin/env python3
"""enuma [firmware] preflight：构建前检查 vendor 输入与 FD 一致性，缺什么就明确报错。

官方约定（porting/uefi-firmware）：preflight 脚本在构建树内执行，环境里
UNIXNU_UEFI=固件仓检出，UNIXNU_DEVICE=设备仓。这里只做检查，不写入任何文件。
"""
import os
import pathlib
import re
import sys
import tomllib

PACKAGE = "Platforms/Xiaomi/enumaPkg"
CONFIG = "Resources/Configs/enuma.toml"
DTB = f"{PACKAGE}/FdtBlob/sm8250-xiaomi-enuma.dtb"
VENDOR = "Binaries/enuma"


def fail(problems):
    print("enuma preflight failed:", file=sys.stderr)
    for p in problems:
        print(f"  - {p}", file=sys.stderr)
    print(
        "\n所需输入见 UniXNU-enuma/proprietary-files.txt 与 porting.toml 的 firmware 区域；"
        "vendor 二进制放 .cache/firmware/，由 preflight/导入脚本落到 Binaries/enuma，不入库。",
        file=sys.stderr,
    )
    raise SystemExit(1)


def main():
    uefi = os.environ.get("UNIXNU_UEFI")
    if not uefi:
        fail(["UNIXNU_UEFI 未设置（应由 unixnu build firmware --uefi 注入固件仓路径）"])
    root = pathlib.Path(uefi)
    problems = []

    package = root / PACKAGE
    if not package.is_dir():
        fail([f"固件仓缺少 {PACKAGE}"])
    for required in ("enuma.dsc", "enuma.fdf", "enuma.dec"):
        if not (package / required).is_file():
            problems.append(f"{PACKAGE}/{required} 缺失")

    vendor = root / VENDOR
    if not vendor.is_dir() or not any(vendor.iterdir()):
        problems.append(
            f"{VENDOR}/ 为空：需要 enuma 原厂 UEFI DXE 二进制（UFS/Display/PMIC/GPI 等），"
            "结构与 pipa 包相同但必须是 enuma 自己的文件"
        )

    if not (root / DTB).is_file():
        problems.append(f"{DTB} 缺失：需要 enuma 的板级 DTB（原厂 dtbo/vendor_boot 导出后编译）")

    config = root / CONFIG
    if not config.is_file():
        problems.append(f"{CONFIG} 缺失")
    else:
        fd = tomllib.loads(config.read_text()).get("uefi_fd", {})
        base, size = fd.get("base"), fd.get("size")
        map_c = package / "Library/MemoryMapLib/MemoryMapLib.c"
        if map_c.is_file() and base is not None and size is not None:
            m = re.search(r'\{"UEFI FD",\s*(0x[0-9A-Fa-f]+),\s*(0x[0-9A-Fa-f]+)', map_c.read_text())
            if not m:
                problems.append("MemoryMapLib.c 里没有 'UEFI FD' 行，无法与 config 对齐")
            else:
                fd_base, fd_size = int(m.group(1), 16), int(m.group(2), 16)
                if fd_base != base or fd_size != size:
                    problems.append(
                        f"FD 不一致：{CONFIG} 为 0x{base:X}/0x{size:X}，"
                        f"MemoryMapLib.c 为 0x{fd_base:X}/0x{fd_size:X}"
                    )
        elif base is None or size is None:
            problems.append(f"{CONFIG} 缺少 [uefi_fd] base/size")

    if problems:
        fail(problems)
    print("enuma preflight: vendor 输入与 FD 配置一致")


if __name__ == "__main__":
    main()
