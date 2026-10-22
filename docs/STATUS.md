# STATUS

更新：2026-10-22（Asia/Shanghai）。当前唯一真相；历史见 WORKLOG。

## 当前结论

**官网全站审阅完成：144 个文档页（中英文各 72）全部访问成功，与源码路由清单一致，两个指定入口可到达全部页面。结论是保持 iPadOS 17.7.11 / 4 KiB，继续 UEFI/GOP → XNU 基础平台 → NT36523，先补版本一致的构建归档和交接契约。** 本轮只读网页、源接口和已有缓存，未操作设备、生成镜像或更改固定构建来源。

按官网阶段划分，本板仍在 **阶段 1：UEFI** 内部。已有实机证据是 BootShim/SEC/DXE 的六个定时复位门，最远到 CoreDispatcher 前；`stop-stage 10` 只是固件内部诊断编号。没有 GOP、菜单、负载卷、DarwinBoot 或 XNU 运行证明。

目标保持 iPadOS 17.7.11 / 21H461、iPad7,1 / j120ap、XNU 10063.141.1、4 KiB。owned-memory 请求为已批准的 512 MiB；board.toml example=true，物理内存字段及 *_verified 标记未改。

## 官网核对的有效发现

- 页面、3836 条有向站内链接、144 个源路由完整覆盖；1 个中文跨页锚点失效，未发现缺失页面目标。中文正文逐页审阅，英文结构及关键段交叉核对；223 个站外链接仅编目，不把外站算入已遍历范围。
- 官网源码参考 HEAD d704728a6df9d1eb113873dc1b57e87f6846e361 比构建固定的 75bc13dd 领先 89 个提交，完整树差异 509 个文件/条目，gitlink 从 0 增到 21。已审阅 archive/bootstrap、模块和 macOS workflow 接口，不等于审查全部变更。未更新锁或切换上游工作树。
- 新工具可复用真实 archive builders、编译记录 bootstrap、存储头准备及官方 macOS 工作流；新版文档不能直接套在旧固定接口上。新版仍保留本次导致 legacy probe 链接缺符号的调用，不能假设升级 HEAD 自动修复。
- pipa 同为 SM8250，但官网未记录实机验证且缺存储驱动；sheng 仍是同 donor 的通用链路参考。NT36532E/THP、SM8550 PMGR/A740 以及其他设备内存/分区值不能继承。
- 缓存 enuma Android FDT 已有 /reserved-memory/cont_splash_region@9c000000（label cont_splash_region，35 MiB），没有名称恰为 splash_region 的节点。应核对临时启动最终 FDT 与本机 ABL 查找语义；这不是黑屏根因证明，也不是修改地址的依据。
- 官网建议设备仓与 uefi-enuma 分离。当前 firmware/ 为已构建/测试的隔离增量原型，拆仓可后续整理；本轮未新建第二个远端。

详细结论：[官网路线核对](operations/2026-10-22-official-docs-route-review.md)；[完整网页清单](operations/2026-10-22-official-site-inventory.md)。机器证据：reports/enuma-official-docs-audit.json、enuma-upstream-docs-comparison.json、enuma-docs-splash-crosscheck.json。

## 最后实机与固件证据

- 六次临时复位门：BootShim 入口 2/7 秒、复制/缓存维护后、SEC C 入口、DXE C 入口、CoreDispatcher 前，均回 Android。最后一次 20:57:59 发出，32.018 秒后确认 sys.boot_completed=1、root 和 boot/vendor_boot 摘要不变。未 flash/erase/改槽。本轮未重新查询设备。
- 最后实测为 stage10 镜像 out/boot-candidate/enuma-dxe-dispatch-stage10-boot-v3.img，3153920 bytes，SHA256 fe97cac064925e430e4b2d4c8f058aa1cf8a0a05fb051e1c7c1b484b1eadc43b；内含 FD da56498bcb5f8ce804bc9d1719d9be8cf2c4d7ed35113ec18bce70d654aeaabe。
- 当前构建报告对应后续未启动 FD d6bf6bb203cd71da4b049db7f8a259c9d702be05180060e3b259c2c2d6c05d8c，仍通过完整构建/81 文件/33 OEM PE-DEPEX 字节审计。重建差异含 SEC 的编译时间/常量池与 PcdDxe 的 8-byte RSDS 标识；不把旧实测结论转移给新二进制。
- 历史 Probe 01 r2 黑屏记录与已测各变体保留；不原样盲重试。门镜像到选定点会主动复位，正常路径须 --stop-stage 0，不运行 iPadOS payload。

证据：reports/enuma-entry-device-tests.json、enuma-probe01-device-test.json、enuma-fd-rebuild-comparison.json；构建变体在 out/entry-probe/ 对应子目录。

## 构建与远端的实际状态

公开 origin：https://github.com/wh1stl3/UniXNU-enuma.git，main 已推送；本轮文档提交号见 Git 日志。

- macOS preflight run 39784132935 **通过**：Apple Silicon、macOS15.7.9、Xcode16.4/SDK18.5、固定源及 arm64 对象编译。SDK 不改变 donor 版本。
- 通用 4 KiB bootstrap run 39784240390 **失败**：已推进到最终链接，_bsd_init 引用的 _native_legacy_display_probe 未解析；artifact 和日志已回读。先前“运行中”的记录已由此结论取代。它关闭板级功能，本来就不是完整 enuma 内核；本轮不重新触发 CI。
- 当前 30 项 Python、主机 sanitizer、4 个 AArch64 板级对象、固件/OEM/v3 审计和复位门证据仍分别有效；无完整 IOKit、最终 XNU/预链接或触控运行通过记录。

## 基础适配与下一步

已有本机 XBL 的 45 项内存/MMIO、31 项配置、33 个原厂模块与 K81 资源；GOP base/stride/format、UEFI map、连续 512 MiB 分配和 EBS 显示保持未观察。硬件 ADT 片段缺 chosen/NVRAM/DRAM/GOP/产品/根；NT36523 只有协议解码核心与通用 GENI 接入证据，缺 FWINFO/IRQ/IOKit/HID/固件恢复/笔输入。

1. 继续 DXE 模块与协议门，核对本机 splash/显示依赖和 BDS/Probe，完成实际 GOP、菜单、输入与 FAT 卷观察。
2. 独立修复未选显示功能的链接引用，审查并复用正确版本的 archive/bootstrap；不用空 stub。随后完成真实静态库、最终内核、donor prelink，不能把仅有编译记录的 bootstrap 失败当成功。
3. 补完整 ADT/NVRAM/种子/占位符，先做 QEMU 的 UniXNU→DarwinBoot 契约验证，再测本板基础平台。新内存字段或预算仍需审查。
4. 按 GENI/ID/FWINFO/帧→IRQ/HID 推进 NT36523，审查软件显示；A650 GPU 后置。原生 UFS/PHY/电源、GPT/OS/SystemOS/root UUID/Data/trust cache 随后闭合。

无新增硬停审批或待按键事项。上游与 nuwa 只读，镜像/备份/设备标识和网页全文缓存不进 Git。
