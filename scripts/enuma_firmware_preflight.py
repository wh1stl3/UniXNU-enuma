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
DTB = ".cache/firmware/dtb/sm8250-xiaomi-enuma.dtb"
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

    # Matching copied FD values do not constitute board evidence.
    for source in [root / CONFIG, *package.rglob("*.c"), *package.glob("*.dsc"), *package.glob("*.fdf")]:
        if source.is_file():
            for number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
                if "TODO REQUIRED" in line or "REQUIRED_ENUMA_" in line:
                    problems.append(f"{source.relative_to(root)}:{number}: 未解决的板级占位项")

    vendor = root / VENDOR
    if not vendor.is_dir() or not any(vendor.iterdir()):
        problems.append(
            f"{VENDOR}/ 为空：需要 enuma 原厂 UEFI DXE 二进制（UFS/Display/PMIC/GPI 等），"
            "结构与 pipa 包相同但必须是 enuma 自己的文件"
        )

    # DTB 走 bootimg 的 append_dtb（pipa/alioth/sheng 的 FDF FdtBlob 均为注释），这里只检查设备仓里的候选输入存在。
    device = os.environ.get("UNIXNU_DEVICE")
    if not device or not (pathlib.Path(device) / DTB).is_file():
        problems.append(f"{DTB} 缺失：bootimg 需要 enuma 的板级 DTB（原厂 dtbo/vendor_boot 叠加导出）")

    config = root / CONFIG
    if not config.is_file():
        problems.append(f"{CONFIG} 缺失")
    else:
        fd = tomllib.loads(config.read_text(encoding="utf-8")).get("uefi_fd", {})
        base, size = fd.get("base"), fd.get("size")
        map_c = package / "Library/MemoryMapLib/MemoryMapLib.c"
        if not map_c.is_file():
            problems.append("MemoryMapLib.c 缺失，无法核对 FD")
        if type(base) is not int or type(size) is not int or base <= 0 or size <= 0:
            problems.append(f"{CONFIG} [uefi_fd] base/size 必须为正整数")
        elif base % 0x1000 or size % 0x1000:
            problems.append("FD base/size 必须按 FDF 的 0x1000 块大小对齐")
        elif map_c.is_file():
            m = re.search(r'\{"UEFI FD",\s*(0x[0-9A-Fa-f]+),\s*(0x[0-9A-Fa-f]+)', map_c.read_text(encoding="utf-8"))
            if not m:
                problems.append("MemoryMapLib.c 里没有 'UEFI FD' 行，无法与 config 对齐")
            else:
                fd_base, fd_size = int(m.group(1), 16), int(m.group(2), 16)
                if fd_base != base or fd_size != size:
                    problems.append(
                        f"FD 不一致：{CONFIG} 为 0x{base:X}/0x{size:X}，"
                        f"MemoryMapLib.c 为 0x{fd_base:X}/0x{fd_size:X}"
                    )

    if problems:
        fail(problems)
    print("enuma preflight: vendor 输入与 FD 配置一致")


if __name__ == "__main__":
    main()
