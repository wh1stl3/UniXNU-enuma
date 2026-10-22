# STATUS

更新：2026-10-22（Asia/Shanghai）。当前唯一真相；历史见 WORKLOG。

## 当前结论

已按用户要求把 UniXNU 固定底座从 75bc13dd 更新到实时 main **5fdbd5d08518bc2d5c196264c56a377dd80cf5ca**，固定并初始化 21 个子模块，保留四个原固件 patch、板级支持和 boot v3。设备仓仍为独立 overlay，上游整树留在忽略的 out/。新增编译期 legacy display 修复，关闭功能不再引用其符号；开启时保留真实驱动引用。

目标仍为 enuma / SM8250、iPadOS17.7.11 /21H461、iPad7,1/j120ap、XNU10063.141.1 /4 KiB。board.toml 未变，example=true，已批准512 MiB请求；未改内存基址/大小和 *_verified 标记。

## 当前验证

- 30 项 Windows Python 通过；GENI/NT36523/UFS 主机 sanitizer、四个 AArch64 对象通过。
- 新 DarwinBoot 的 AddonOffset 契约已迁移，内存窗口/ADT/GPU addon 槽主机检查通过。真实可选显示 probe 在开关0/1时的对象未定义符号对照通过。
- 新底座完整 stage10 UEFI 构建、81文件/33 OEM PE-DEPEX字节审计与boot v3回读通过。FD SHA256 **10d813fce9a1d503a8b2152aa3c21acaf56885201233b48546db2d1023703e27**；候选 out/boot-candidate/enuma-upstream-stage10-boot-v3.img **未启动**。快照 out/upstream-integration/stage10/。
- CI 已迁移到新 pin、固定21模块并应用校验的patch系列；run39789234153在恢复Apple头文件前遇匿名GitHub API HTTP403，尚未编译内核。新增固定Git树元数据适配，26头文件已由不变的上游恢复器在WSL恢复并逐blob核对；下一轮最终链接待运行。旧preflight run39784132935通过，旧bootstrap run39784240390在legacy符号最终链接失败，历史不覆盖。

## 实机边界

上游更新后已临时复测新版stage10，31.357秒确认Android完成、root/分区摘要不变。主线新增调度后门的2秒候选也已返回Android（44.497秒），正在构建7秒对照以区分其他复位源；该后续源码/证据将在固件里程碑单独提交。历史旧版六个门最远CoreDispatcher前。最后实测镜像 SHA fe97cac064925e430e4b2d4c8f058aa1cf8a0a05fb051e1c7c1b484b1eadc43b，FD da56498bcb5f8ce804bc9d1719d9be8cf2c4d7ed35113ec18bce70d654aeaabe。

按官网仍是阶段1 UEFI；没有 GOP、菜单、负载卷或 XNU/触控实机运行证据。1600×2560 Android显示不是GOP base/stride/format证明，缓存FDT的35MiB cont_splash也不是黑屏根因。

## 下一步

1. 先完成新版 macOS 最终链接和4 KiB审计；完整板级archive/prelink另推进，不能以通用基线代替。
2. 主线回到UEFI/GOP，增加CoreDispatcher之后的复位门，必要时逐模块定位。全部候选保留摘要，实测前确认enuma/备份/恢复路径，结束回Android。
3. GOP/map观察后补完整ADT、NVRAM/种子/占位符，再推进XNU基础平台与NT36523 IRQ/HID；SM8550专用PHY/电源/A740不能套用，A650后置。

公开origin https://github.com/wh1stl3/UniXNU-enuma.git；本轮推送/CI状态以随后记录为准。无新增硬停项。详细迁移与复现见 [上游接入报告](operations/2026-10-22-upstream-integration.md)，官网路线/144页清单仍有效，历史版本差异结论不代表当前pin。
