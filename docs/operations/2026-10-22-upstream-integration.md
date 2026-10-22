# UniXNU 主分支接入

2026-10-22 Asia/Shanghai。按用户要求更新上游并保留 enuma patch。设备仓是 `-D` overlay，故更新固定底座，而不把上游整树合并进设备仓历史。

旧底座 `75bc13dd34dc4e403826793739e316a264ce00dd` → 本轮实时查询 main `5fdbd5d08518bc2d5c196264c56a377dd80cf5ca`。独立工作树 `out/sources/UniXNU`，原共享参考及 nuwa 未改。21 个 gitlink 固定于 config/sources.lock.json，递归检出；CI 同样初始化并核对模块，禁止跟随模块浮动 HEAD。

## 保留与迁移

- 四个 firmware/patches 原文件摘要完整保留；EnumaPlatform、NT36523、内存/GOP overlay 和 boot v3 打包实现不变。board.toml 字节不变、example=true、512 MiB，不改任何验证标记。
- ArmCpu、ArmDTPlatform、GENI 核心内容一致；GENI 来源改为独立模块仓及其固定 SHA。上游 NativeUfs/HidInput/Adreno 的新内容不等于 enuma 驱动通过，仍未开启存储/显示/SM8550 专用路径。
- DarwinBoot.c 的新 GPU addon 可选文件/16-byte ADT 槽和错误输出已核对；GetMap/RunEnd/绘字提取逻辑仍适用。真实 AdtNode 多一个 AddonOffset 参数，主机 harness 已同步，并覆盖合法、短值及重复 addon 槽。
- 保留上游真实实现，增加 patches/upstream/0001-guard-optional-legacy-display.patch：未选 legacy 功能时去掉其编译期引用；开启时仍链接真正驱动。不是空 stub。因为它修改上游 XNU patch，本层 diff 同步调整内层 hunk 长度。
- scripts/upstream_source.py 核对底座、21 模块、文件与 patch 摘要；补丁可重复应用；反向移除后必须精确恢复固定树，拒绝同文件中的额外改动。check_workspace 与 macOS CI 共用。
- 新的 archive/bootstrap 编排随主分支保留在固定底座，尚不把未完成的板级静态库配置为已可构建。macOS 通用基线仍所有板级开关关闭，要求最终链接和 Mach-O/4 KiB 审计通过；不把 bootstrap 留下编译记录当成功。

## 复现

```powershell
git -c core.autocrlf=false clone --no-checkout https://github.com/UniXNU/UniXNU.git out/sources/UniXNU
git -C out/sources/UniXNU checkout --detach 5fdbd5d08518bc2d5c196264c56a377dd80cf5ca
git -C out/sources/UniXNU -c core.autocrlf=false submodule update --init --recursive --depth 1
python -B scripts/upstream_source.py out/sources/UniXNU
python -B scripts/check_workspace.py
python -B -m unittest discover -s tests
```

WSL 使用 `/mnt/d/Code/UniXNU-enuma/out/sources/UniXNU` 作为 `--unixnu` / `--source`。执行 check_enuma_drivers.py、check_reused_ufs.py、check_darwin_adt.py、check_optional_display.py 与原完整 build_enuma_firmware.py（--stop-stage 10）、audit_enuma_fd.py、prepare_enuma_boot_payload.py、package_enuma_boot.py。check_firmware_overlay.py 的 --firmware-root 仍为固定旧 uefi-sheng 参考。

## 证据边界

30 项 Python、主机 ASan/UBSan、四个 AArch64 板级对象、真实可选显示 probe 对象符号 0/1 对照、DarwinBoot 解析/分配契约、完整固件构建、81 文件/33 OEM 字节与 boot v3 roundtrip 均通过。新 stage10 FD `10d813fce9a1d503a8b2152aa3c21acaf56885201233b48546db2d1023703e27` 未实机启动，不能继承旧 stage10 的硬件结论。

新候选 `out/boot-candidate/enuma-upstream-stage10-boot-v3.img`；构建日志/报告/FD 快照 `out/upstream-integration/stage10/`。可发布证据见 reports/enuma-upstream-integration.json、enuma-optional-display-check.json 及各回归报告。macOS 新运行结果另记；旧 run39784240390 的最终链接失败记录保留。

## CI 头文件获取修复

迁移提交83f4608已推送。run39789234153的固定源/21模块/补丁/SDK检查通过，但prepare-xnu-source.py请求匿名GitHub API元数据时403，尚未进入XNU编译。证据reports/enuma-macos-upstream-run.json。

新scripts/ci/header_inputs.py从固定Git树列出DriverKit/crypto/TrustCache文件blob，提供同格式缓存元数据，download_url指向固定commit的raw内容。其余下载、blob校验及恢复仍为原始上游实现。补充锁config/ci-header-sources.lock.json固定Apple头文件提交2c2f96dc和aca3beaa，校验其tag与当前feeds匹配；只需浅取树，避免匿名API和整树blob下载。未传入或记录访问令牌。

Windows第一次raw HTTPS读取出现SSL EOF；在WSL使用不变上游恢复器完成26个文件恢复，逐个Git blob SHA-1与SHA256核对通过，reports/enuma-ci-header-check.json。该主机证据不等于macOS最终链接；修复后另跑CI。

## macOS 真实最终链接通过

修复提交d3ce3c4已推送。run39790786938成功，artifact已回读，固定主分支5fdbd5d、21模块与本地patch均吻合。真实通用基线最终链接完成，产物21,041,528 bytes，SHA256 de5ccd244f0b4fd6c0ebe5f6173aa6f7be993e31aa45db583150cd65c2f4c0fd，TG0/TG1均4 KiB，Mach-O/初始TCR审计通过。reports/enuma-macos-upstream-success.json记录完整来源、SDK、头文件与日志摘要；二进制和28MB日志只在out/ci-runs/39790786938/。

这次验证关闭全部本板功能，没有板级archives、donor prelink或enuma XNU启动声明。链接还保留不存在的platform搜索目录和dsymutil --minimize选项警告，最终命令退出0且审计通过；不把警告隐去或升格为设备能力。旧两次失败证据保留。
