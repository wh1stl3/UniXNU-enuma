# D-171：完整结构ADT与真实FAT系统输入

2026-10-25 02:45（Asia/Shanghai）。本轮仅离线工作，无设备动作、固件改动、分区写入或新硬停。

## 具体产物与复用

通过固定UniXNU 5fdbd5d的真实payload.build生成96 MiB FAT，路径out/full-boot/payload/payload.img，SHA256 **49b4d6229e88180c338eb41a347f8ecf9572ba60c7efc476ccf4573936818773**。这是系统输入包，不是Android boot镜像，也未具备完整系统启动条件。

- kernel.macho：54,231,040字节，be83a7ec0c11132c13b9581d8784a1775584bb97ff5c66484bcbb2e7bef0879e，复用D-170预链接，未重编平台内核。
- kernel.macho.adt：11,024字节，f8b5e0bc127967f785b464486f1a0ec0fac798592824206fd1ef91e7b0fb7cd2。
- kernel.macho.trustcache：7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7，原始Static和System两个v2模块，不增加自签代码条目、不改模块、不宣称Apple个性化完成。
- unixnu.toml：96066b835a28a685113f8858ca0a6d56f8d494aa7a92249f94e8e2caa92c4f3e；默认xnu、autoload=false、参数-v，无虚假native-ufs-root或PMGR开关。

scripts/make_enuma_adt.py直接调用固定umi 3eb7257的umi_adt.py编码器和build_tree，校验现有源锁中的文件摘要；不调用umi硬件profile或其builder。包含chosen、8192字节NVRAM proxy、manifest/memory-map、CPU0、GIC/timer和同donor iPad7,1产品/安全兼容属性。保留enuma物理产品model，不复制umi的显示、触控、GPT或种子。CPU0优先，不提前启用SMP。

本机历史FDT 643aa3ec…34c62的三段memory/reg经2+2 cell解码、排序及非重叠检查，总量0x1fbb00000、最低地址0x80000000；只写入ADT信息属性，不解释为可用/连续RAM。不修改board.toml或bringup-plan，不固定新的物理分配基址；darwinboot-memory-size仍为R-001的0x20000000，实际UEFI分配尚未观察。没有新增*_verified=true。

scripts/prepare_full_payload.py核对上游Git blob，用上游DER函数解出两份有固定SHA256的原始IM4P trust module，复用上游bundle布局和payload.build/mtools。构建上下文仅在进程内，不写board；生成ADT含新鲜随机熵，重新构建不会承诺相同摘要，已有包默认拒绝覆盖。平台身份种子、root UUID和Data均未伪造。私有环境种子意外继承会被拒绝。

## 离线执行与资格

构建（WSL Ubuntu-22.04，firmware-tools虚拟环境含tomli；不运行参考仓默认builder）：

```text
env PATH=/mnt/d/Code/UniXNU-enuma/out/firmware-tools/bin:/usr/bin:/bin python -B /mnt/d/Code/UniXNU-enuma/scripts/prepare_full_payload.py
```

实际FAT由mtype回读四个输入，内核和trust摘要匹配原输入，ADT和配置归档至out/full-boot/payload-readback.*。机器证据reports/enuma-full-payload.json、enuma-full-adt.json。

扩展已有check_darwin_adt.py和C主机适配器，提取当前固定DarwinBoot的实际AdtNode与ValidTrustCaches函数，消费FAT回读ADT及trust bundle。ASan/UBSan下正例通过、两份输入的每个截断位置拒绝、trust尾随字节/非法offset/hash类型/重复无序hash拒绝；原有窗口分配/合并/空洞/失败测试仍通过。reports/darwin-adt-contract.json记录命令、函数/适配器摘要及退出码。此为主机执行，非UEFI实机分配或XNU执行。初次检查发现旧ADT plan的board摘要已过期，重新由同一FDT与当前board生成plan；512MiB数值和physical_base=null不变。

```text
python scripts/check_darwin_adt.py --unixnu out/sources/UniXNU --adt out/full-boot/payload-readback.adt --trust out/full-boot/original-static-system.bundle
python scripts/audit_payload_transport.py
python scripts/audit_system_roadmap.py
```

WSL Python3.10运行check_darwin_adt时须先将tomli别名为tomllib（原脚本工具链要求）；实际完整调用已在机器报告记录。额外负例：--owned-memory-size 0x40000000被新ADT适配器拒绝，未生成rejected.adt。

## v3运输的具体判断

保存stock vendor_boot_a SHA256 3da202d0…641daba为v3，page4096/header2112，vendor ramdisk长度**2230字节**。固定umi模板从FDT读取initrd，并要求完整范围为sector对齐、精确BPB长度的FAT，还依赖其独有保留/映射窗口。enuma不能直接套用。

audit_payload_transport.py核对源锁和原始备份摘要：纯96MiB FAT满足BPB检查；原长2230前缀+FAT和页补齐4096前缀+FAT这两个**假设组合**均不满足完整initrd的FAT检查。原长前缀还导致FAT相对起点不对齐512。这里只证明直接搬whole-initrd契约不兼容这些组合；**未观察本机实际入口布局，也未选择其中一种偏移**，不能把离线组合当成ABL实测。

主判断：应先适配v3运输契约，再让现有FAT进入loader；当前直接换成umi RAM驱动很可能在BPB/范围门禁前被拒绝（中等置信，取决于真实组合规则）。能推翻该判断的观测：本机临时启动的实际FDT表明initrd本身已是精确FAT，且整个范围在已审查映射/生命周期内。

下一步按固定本机ABL和公开boot-v3实现核对组合规则，取得实际入口FDT/start/end与映射依据；在已界定范围内派生唯一FAT子区间，严格检查溢出、重叠、对齐和长度，复用只读BlockIO，确认SFS绑定和文件身份。不扫描任意RAM、不猜2230/4096偏移、不搬umi的0xa0000000窗口；若必须修改board/plan内存字段，按原规则先提具体审查。

## 仍缺的完整系统条件

v3运输/SFS、GOP或其他真实错误通道、原生PMGR/UFS/root/Data/UUID和私有平台种子仍未闭合。ADT是完整结构的早期启动输入，不是完备用户态硬件描述。实验prelink仍保留上游runtime/loadable限制；未进入XNU/Hello/桌面。下一轮优先运输和可观察错误，再闭合存储，不重复已有54MiB预链接或内核CI。A历史恢复/R-016 consumed、B离线备用、R-002失败/R-015暂停及其他门禁维持。
