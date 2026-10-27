# 已批准的 512 MiB 请求与离线交接检查

2026-10-22，用户批准 R-001 方案 A。配置提交 982dcc0，仅新增 [payload.adt].owned_memory_size="0x20000000"；example=true、其他未设定内存基址和总 DRAM 均保持。生成/启动镜像仍需单独确认。check_workspace.py 已通过源码锁、donor身份、真实 defconfig 和 example 拒绝检查，并精确限制 payload 为获批配置。

## 接通的约定

plan_adt.py 从 board.toml 读取批准值，在 reports/enuma-adt-plan.json 中记录 /chosen/darwinboot-memory-size、LE uint64 字节 0000002000000000，以及 board 文件摘要。这里仍是 JSON 输入计划，不输出 ADT 二进制；enuma 完整 ADT 生成器和实际启动路径未接通。实际物理地址保持未知，不能从此报告推断可用内存。

scripts/check_darwin_adt.py 从 UniXNU 75bc13dd 的 DarwinBoot.c 按固定函数边界提取 AdtNode、RunEnd、AllocateWindow 到本仓 out/，先核对源文件 SHA256。编译时使用真实 WindowSize.h，并运行上游 Test/window-size.c；未复制或修改上游源码树。

主机 harness 仅提供类型、字节读取、内存映射和 EFI 服务替身，合成 ADT 只存在于进程内存。EFI AllocatePages 替身检查请求始终为512 MiB对应页数并注入失败；不调用固件，不触碰物理内存。C 测试中的地址仅为合成例子，不是 enuma 内存图或基址选择。

## 检查结果与限制

- 真实 AdtNode 接受512 MiB请求；144个截断长度、尾随字节、重复属性、重复chosen、根节点错放属性、短属性、越界/未对齐大小被拒绝。最小256 MiB和最大8 GiB边界通过。属性缺省时解析结果仍为0，实际 Boot 调用者会使用256 MiB默认值；本板现在显式请求512 MiB。
- 真实 RunEnd/AllocateWindow 可合并乱序但物理相邻的空闲描述符，支持描述符stride大于结构体大小；不会跨越保留洞或选择保留类型。测试覆盖对齐及内核块偏移、候选窗口分配失败后尝试下一窗口、全部失败、GetMap失败及释放行为。
- 首次夹具把起点0x100001000、长度0x20200000、内核块偏移0x4000误判为可容纳512 MiB。实际候选起点0x100204000，比区域起点多0x203000；剩余空间不足。将该例保留为拒绝测试，另加长度0x20400000的成功例后检查通过。没有修改上游算法来满足错误预期。
- 以上均为 ASan/UBSan 主机检查，不是 QEMU、EDK II 完整链接、真实 UEFI 分配或 XNU 执行。它不验证实际内存图是否正确、GOP交接、reserved区域真实性或设备驱动状态。

## 复现

```powershell
& 'C:/Program Files/WorkBuddy/resources/vendor/python/python.exe' -B scripts/check_workspace.py
& 'C:/Program Files/WorkBuddy/resources/vendor/python/python.exe' -B scripts/plan_adt.py
wsl -d Ubuntu-22.04 -- python3 -B /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/check_darwin_adt.py --unixnu /mnt/d/Code/PortingiOSLegacy/common/sources/UniXNU
```

先重新生成JSON计划，随后检查其board摘要以拒绝过期计划。检查只编译主机测试程序，输出位于 out/darwin-adt-contract；不会生成 ADT、EFI、FD、boot.img 或改动设备。证据 reports/workspace-check.json、reports/enuma-adt-plan.json、reports/darwin-adt-contract.json。

剩余前置条件：实际 UEFI map、完整enuma平台内存/GOP配置、厂商依赖、启动材料实际尺寸，以及已审查的固件/boot打包方案。R-001不代替这些条件，也不授权自动扩大请求。当前不新增其他批准请求。
