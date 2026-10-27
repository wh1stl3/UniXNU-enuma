# D-172：boot v3 RAM载荷运输与同次13项检查

2026-10-25。本轮完成源码、完整UEFI构建、实际FD/PE资格、AOSP boot-v3打包和独立归档；没有实机动作。用户补充“尽量一次验证多个验证点”已写入AGENTS，并落实为同一候选的顺序报告，前置失败不继续依赖读取。

## 当前产物

| 项目 | 实际值 |
| --- | --- |
| firmware源码 | 698b7c17dbbd80993070a45e2aa5ae15d330b63b，已推送uefi-enuma/main |
| FD SHA256 | 5a031cd8b39c84a23a3ffd847400adbe5c85944f5fde59e307f7c4c9c1e13f68 |
| boot-v3镜像 | out/full-boot/transport/enuma-system-transport-v3.img，103817216字节 |
| 镜像SHA256 | 194fa0f2bf51236ba7d1ed2f741ea1597104c8278197a0485b039b8e100f8b9e |
| 内含generic ramdisk | D-171真实96MiB FAT，49b4d6229e88180c338eb41a347f8ecf9572ba60c7efc476ccf4573936818773 |
| 资格归档 | out/full-boot/transport/qualified-698b7c1/，包含FD/raw/image、实际PE/map/编译命令、源码/生成契约及资格清单 |

这个镜像含真实kernel/ADT/trust/config，是运输实验候选，**不是已具备iPadOS运行资格的完整系统**。prelink的runtime/loadable限制、PMGR/UFS/root/Data/种子和实际错误观察仍未闭合。未启动XNU、未观察Hello。

## 从猜测推进到本机指令依据

[AOSP固定bootimg.h](https://android.googlesource.com/platform/system/tools/mkbootimg/+/808d42e197506319ee65eb078d3defd9602e2ac2/include/bootimg/bootimg.h)规定v3 generic ramdisk紧接vendor ramdisk。此前Android历史FDT长度50124652恰好等于50122422+2230，仅能支持历史组合，不能独自证明临时UEFI入口。

本轮audit_abl_v3_concat.py从本机ABL ff00cd26…cc802a提取实际LinuxLoader PE 0460da8e…cee612，逐条核对：

- 0x16470..0x1648c从vendor header+0x18解出原始size，存入[x24-0x28]；generic size路径取boot header+0xc、存入[x24-0x38]。
- 0x173a4..0x173d0针对版本>=3执行vendor复制，间接槽0x160与UEFI CopyMem布局一致。
- 0x173d4读取原始vendor size，**0x173d8 add x21,x21,x8**直接推进目的地址，没有对齐计算。
- 0x173e4..0x173f8用generic size执行下一次复制。

报告enuma-abl-v3-concat.json保留RVA、指令字节、反汇编及NOP破坏推进指令被拒绝的负例。这是实际PE切片/数据流依据，不是运行跟踪，也不证明全部分配路径或所选DTB。主判断现为高置信：按原长2230字节拼接适用于这个固定ABL的普通v3路径；实际候选仍必须在运行时核对完整范围和内容，不能凭静态结论越过检查。

## 实现与边界

新增可选EnumaRamPayloadDxe，复用固定umi 3eb7257的真实只读BlockIO、设备路径和FDT交接模式，保留版权/BSD-2-Clause-Patent说明。它不带umi物理地址，不访问UFS或分区。

运行时从本仓MemoryMapLib查唯一Kernel条目，要求AddMem/Reserved/write-back且范围不溢出。当前已有0xa0000000/0x10000000条目保持不变；MemoryInitPei为该SYSTEM_MEMORY条目构建Reserved allocation HOB，RamManager的ParseMemoryRange跳过既有descriptor，提供源码层生命周期依据。本轮未新增映射或修改任何board/bringup-plan内存字段，实际UEFI map仍待观察。

x0 HOB必须给出位于上述现有映射内的8字节对齐FDT；先约束40字节头，再限制完整TreeSize，才遍历chosen。initrd必须整个在该范围内、与FDT不重叠、长度精确等于本地vendor prefix+FAT。通过前缀CRC后才派生FAT起点，随后检查精确BPB和完整FAT CRC。没有RAM扫描、第二偏移、页补齐、sector向上取整或范围外解引用。

FAT起点可能不按512对齐，这是有效的字节复制输入；mRamBase保持原始地址，RamRead以LBA/长度作扇区检查，再CopyMem，IoAlign=1。不能为满足旧umi的物理起点对齐而跳过字节或扩大映射。

生成的PayloadContract.h只在out/构建staging中，来自锁定vendor_boot与已审计FAT，不提交OEM原文。host SHA256锁输入；runtime CRC32用于传输损坏检测，**不作密码学认证或Apple信任链声明**。四个文件以大小与首64字节CRC核对；其完整数据此前已纳入整个FAT CRC，不分配54MiB临时内核缓冲。

发布同次报告后，失败的DXE入口保留映像驻留，避免报告和函数指针悬空；此处EFI_SUCCESS仅表示驱动留驻，payload结果必须读逐项状态。报告只在本次Boot Services生命周期有效，不承诺跨复位保存；未复活R-002。

## 同一候选的13项结果

| 索引 | 项目 | 位置/判据 |
| --- | --- | --- |
| 0 | MAP | 现有命名区域、类型和范围 |
| 1 | FDT | x0 HOB、头、完整大小和映射边界 |
| 2 | INITRD | chosen起止、精确长度、无溢出/重叠 |
| 3 | PREFIX | 实际vendor前缀CRC |
| 4 | BPB | FAT签名/512字节sector/精确声明长度 |
| 5 | FAT CRC | 完整96MiB内容损坏检查 |
| 6 | BLOCKIO | 只读协议与device path发布 |
| 7 | CONNECT | BDS时ConnectController实际返回，单独记录 |
| 8 | SFS | 同一个RAM handle上的文件系统绑定 |
| 9–12 | KERNEL/ADT/TRUST/CONFIG | 依次只读打开、大小和header检查 |

0–6在DXE执行，7–12由已有EnumaProbe在BDS调用，避免在体系结构/文件系统驱动未就绪时过早ConnectController。四个文件检查任一失败即停止后续打开，未执行保持EFI_NOT_READY；新模式移除原60秒诊断暂停，成功后交给原UniXNURun。

CONNECT可能因已绑定设备返回非成功；只要SFS与文件成功即可判断载荷可用，不能把CONNECT warning当后续读取失败。应用要求0–6和8–12的成功位，单独打印全部13项。失败时在进入UniXNU前返回错误。

输出仍复用原有Print/DiagDraw；这仅是源码上的同次错误通道，**enuma可见文本尚未实证**，不能把协议存在/FD打包成功当作人能读到报告。当前不安排新设备动作；下一步先闭合观察与恢复条件，再在同一启动中读取这批结果。

## 执行与资格

1. check_ram_payload.py在ASan/UBSan下执行生产TransportBounds、RamRead/Write/Reset/Flush及CRC wrapper：非对齐首尾块、范围/溢出/重叠、错误MediaId、NULL/非整sector/越界LBA、写保护和prefix/FAT损坏负例通过。用主机服务适配器，不执行FDT/SFS或模拟实机。
2. 可选完整构建：build_enuma_firmware.py --stop-stage 0 --diagnostic-without-ufs --ram-payload out/full-boot/payload/payload.img，实际WSL路径/命令保留在构建记录。第一次preflight因修改了旧补丁匹配行拒绝；698b7c1把新宏并入现有options补丁后完整构建通过，未绕过检查。
3. audit_enuma_fd.py确认32个保留OEM PE/DEPEX原字节不变，仅省略UFSDxe；实际EnumaRamPayloadDxe/EnumaProbe进入FD。A/B旧候选保持自身归档，不将本轮新源码归给旧实测。
4. prepare_enuma_boot_payload.py复用原BootShim编译器，192字节shim+3MiB FD；package_enuma_boot.py用固定AOSP mkbootimg/unpack_bootimg往返真实96MiB ramdisk，stock vendor_boot不变。
5. qualify_ram_payload.py核对两个实际GNUmakefile的RAM_PAYLOAD=1和禁早停/像素/value宏，实际PE机器类型/FD内相等、map指向的Sizes/Crcs数组、RamWrite机器码精确返回EFI_WRITE_PROTECTED，以及旧60秒文本已消失。归档默认拒绝覆盖，清单绑定所有文件。

机器证据：enuma-ram-payload-host.json、enuma-ram-payload-contract.json、enuma-ram-payload-qualification.json、enuma-abl-v3-concat.json、enuma-firmware-build.json、enuma-fd-audit.json及源迁移报告。source/host/build/packaging通过均不等于实机运输/SFS通过。

设备仓以firmware/子模块为权威，本轮pin升级到698b7c1，UniXNU仍5fdbd5d；standalone D:/Code/PortingiOS/enuma/uefi-enuma旧74598df及其已有Mu脏状态未动，不要误用其旧检出构建本候选。board仍example=true、R-001仍512MiB、没有新增verified/分区写入/像素试验。A/R-016 consumed、B备用、R-015暂停和R-002失败限制保持。
