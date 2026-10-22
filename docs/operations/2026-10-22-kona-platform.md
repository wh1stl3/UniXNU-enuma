# Kona 固件与 SM8250 支持核心离线里程碑

日期：2026-10-22。用户要求继续离线，优先复用已有实现。本轮未运行 ADB/fastboot，未生成诊断/固件镜像，未修改内存配置或验证标记。参考仓全部只读；产物在本仓 out/。

## 固件源码接入

选用既有 UniXNU/uefi-sheng 329b473df1e53a3bfa64b2b39b79670c4c02279b 的 Kona 路径。初看本地目录不全是 sparse checkout；Git tree 包含完整平台和 Mu 子模块。Mu_Basecore gitlink cfb93724 与 UniXNU feeds 相同。Mu-Silicium 42fe5637 的 core 为 3c9c7b2e，但本次用到的 .gitmodules、Kona DSC/PlatformSec、alioth DSC/FDF 与选定版本相同。比较见 reports/firmware-base-comparison.json。

firmware/Platforms/Xiaomi/enumaPkg 仅包含设备增量：DSC 引用 KonaPkg 和 UniXNULib/FdtLib，FvMain 明确包含 UniXNU app、UniXNUDxe、DarwinBoot 三个 INF。真实模块接口摘要锁在 config/porting-sources.lock.json。未接入 alioth 的内存图、ACPI/DTB 和厂商二进制。

ENUMA_PLATFORM_CONFIG、ENUMA_VENDOR_APRIORI、ENUMA_VENDOR_DXE 没有默认值且带 !error；FD/boot header 的 Resource config 未创建。当前源码检查只展开本地 include，外部依赖作为未闭合边记录，不能声称完整 EDK II 解析/链接成功。厂商依赖也包含供电/clock/DDR/display/storage 等真实协议，空 include 无法代替。

Kona PlatformSec 原本 detach 六个 MDP streams。补丁在 ENUMA_PRESERVE_DISPLAY=1 时跳过它，保留 watchdog；用真正 C 预处理器检查未定义/0/1 三种分支。首次 git apply --check 失败是补丁 CRLF 与上游 LF 不匹配，已固定 .patch 使用 LF，随后精确应用通过。此检查不是 EDK II 编译，更不证明 ExitBootServices 后仍可显示。

## 板级支持

- EnumaGeniSpi 使用固定 UniXNU NativeGeniSpi 的真实实现和原寄存器模型。提供 mode0、CS0、最高19.2 MHz 的 FIFO/PIO 接口，最大单次4096 bytes；拒绝活动 engine/FIFO-disabled/错误 protocol，错误后撤销 ready。显式强制 mode/CS 寄存器编程，修正本板适配可能继承的非零硬件状态。调用者仍须负责映射、顺序保证、供电、时钟、pinmux、独占交接。
- EnumaUfsClock 只暴露 GCC 读取回调，九个寄存器读取成功才发布完整样本。脚本从厂商 gcc-kona.c 的九个 clk_branch 独立提取 enable_reg，避免测试和实现同抄一个错误表。没有写寄存器、MMIO backend 或 UFS 链路初始化。
- SPI 的 SE=0x990000、wrapper=0x9c0000、IRQ GPIO39、SID0x5a3 等来源是 enuma 历史 FDT。GENI wrapper generic 可复用；sheng 的 NT36532E/THP 包解码不可用于 NT36523。历史固件名含 _k81_，与候选厂商 DTS 不同，尚待当前设备绑定核对。
- 未编写空 IOKit service；这些是可编译支持核心，尚未注册到 XNU。NativeUfs 的 SM8550 分支仍关闭，QMPv4 PHY/供电/SMMU 不由九项时钟读取解决。

## 复现

Windows 的 Python 指向 C:/Program Files/WorkBuddy/resources/vendor/python/python.exe；WSL 为 Ubuntu-22.04，Clang14。新引用只取锁定文件，不操作参考树的子模块。

```powershell
& 'C:/Program Files/WorkBuddy/resources/vendor/python/python.exe' -B scripts/fetch_porting_references.py --fetch
& 'C:/Program Files/WorkBuddy/resources/vendor/python/python.exe' -B -m unittest discover -s tests -p test_firmware_overlay.py -v
wsl -d Ubuntu-22.04 -- python3 -B /mnt/d/Code/UniXNU-enuma/scripts/check_enuma_drivers.py --unixnu /mnt/d/Code/PortingiOS/common/sources/UniXNU
wsl -d Ubuntu-22.04 -- python3 -B /mnt/d/Code/UniXNU-enuma/scripts/check_firmware_overlay.py --unixnu /mnt/d/Code/PortingiOS/common/sources/UniXNU --firmware-root /mnt/d/Code/PortingiOS/common/sources/uefi-sheng
```

首次缓存缺失才需要 --fetch；默认只核验。固件检查末尾加 --require-image-ready 应返回2并列出缺少的输入。该程序从不调用实际 build，因此即便检查规则未来发生错误，也不会产生固件镜像。完整构建必须在新的可写工作区进行，因为 UniXNU firmware.py 会更新子模块并 apply/revert 补丁。

结果：上游 GENI 全套模型（包含20种PIO长度）及本板补充测试、九种 UFS 读取失败位置的原子交付检查通过 ASan/UBSan；EnumaGeniSpi、EnumaUfsClock、上游 GeniSpi 三个 AArch64 freestanding 对象编译通过。七项 Python 测试覆盖 FDF 漏项、错误 FV、外国板引用、缺失输入保护、include 环/路径逃逸。完整镜像前置检查如预期拒绝。证据 reports/enuma-driver-check.json、reports/firmware-overlay-check.json。

## 下一个配置关口

R-001 将首阶段 owned-memory 预算明确为候选512 MiB或1 GiB。DarwinBoot 的请求大小不是固定地址；实际分配仍由 UEFI map 决定，不能用 Android 历史 RAM 图代替。默认256 MiB也不是 enuma 的验证结果。推荐512 MiB仅为了首先定位内核入口/诊断问题，不承诺完整 iPadOS 用户态。具体最小批准范围见 NEED-REVIEW；当前 board.toml 保持原状。
