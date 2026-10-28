> 当前v13实测已完成：三页独立判读匹配本轮session，DisplayDxe+0x2b140、ESR0x96000047、FAR0x0aeb0004与v12一致，VBIF三级翻译异常未消除。自行返回且恢复核验通过，trial已消费。下一步查实际页表建立/后续变更，不把静态描述符存在当运行期映射生效。见 operations/2026-10-28-oem-v13-live-fault.md。

> 2026-10-28T20:28:23.239076+08:00 v13已单次消费，Sending/Booting OKAY；用户确认自行返回Android、三页日志。独立身份/启动完成/root/A槽/解锁及原双分区和本地备份摘要核验通过。媒体目录已创建，待文件落地独立判读；不重试，不预写OEM/DXE/GOP成功。此前未消费文字仅历史。

# v13接续：三窗口映射候选已就绪

2026-10-28：v13已完成build1/qualification1，新增VBIF、DSI0、DSI1三独立NS_DEVICE映射，保留原厂调用和异常取证。69项Python、8组宿主、277处链接指令删除及36项映射变异检查通过；2495项来源绑定、72个FD PE镜像和SEC TE核对通过。软件就绪，新trial未消费，未上机。

## 精确候选

- 镜像：`out/oem-display-map-20261028/qualification1/image.img`，3153920字节。
- SHA256：`9331e0a3f1db230326c5ae49f2ed77ed443a90f89232684e43b929f8c5a854bb`。
- 资格SHA256：`5d01765a1c216e902f1c503add81bfb638d0e72d651448b21ebc2a4f88dec32b`。
- FD SHA256：`3129d850cd63d96cb495dce7556494be50354adf757e37bfb9d3416a072ab1e7`。
- trial：`e4fd7a07-b112-433b-8008-c8dee5ed1392`；session：`0x4229413d4b327cfc`；未claim/未启动。
- 固件提交：`f523e160ad7d87d00d241e840d94179c1c0b8459`；构建使用逐文件绑定工作树快照，不称提交后重编。

## 改动与证据

v12已实测并恢复，异常在DisplayDxe+0x2b140写0x0aeb0004，是VBIF映射缺口的强证据。本轮增加VBIF 0x0aeb0000/0x3000、DSI0 0x0ae94000/0x1000、DSI1 0x0ae96000/0x1000，后两项由原PE双控制器真实读写路径与本机FDT共同支持。REGDMA/SID/SWFUSE仍待进一步归因，不直接加入。

映射源除三条外与v12一致；实际SEC与最终FD TE四条描述符（含保留DISP_CC）逐字节和属性核对，50条活动描述符。24份旧镜像/资格摘要保持，R027冻结，共享主线只读。没有改RAM字段、保留区、verified、原厂PE、寄存器值或分区。

详见[v13操作记录](operations/2026-10-28-oem-display-map-v13.md)、[结构化报告](../reports/enuma-oem-display-map-v13-20261028.json)、[公开研究](operations/2026-10-28-oem-vbif-public-research.md)。本地证据`out/oem-display-map-20261028`。

## 当前状态与下一步

本轮无设备动作。设备最近一次已知状态是v12 retry1自行返回Android且独立身份/原双分区/备份检查通过；本轮未刷新在线状态。旧v12原尝试和用户明确授权retry1都已结束，不能默认重用。

用户当轮“可以上机”即确认正在录像并在场可恢复，不重复询问；届时仍核对精确新资格、未消费账本、当前设备/备份及恢复状态，再仅一次临时boot。75秒是主机观察期限，不是固件自动返回保证。v12曾传输超时，后续原生Windows成功，但不能断定WSL根因；未来执行入口应保留超时部分输出且独立绑定，不能直接复用v12 retry脚本或账本。

无页不证明成功；同FAR翻译故障需查实时页表，外部异常需查电源/时钟/权限，新FAR按精确PE继续归因。HAL IOMMU/DMA、VBIF握手、面板DSI仍是后续风险。OEM真实返回、全DXE、原厂GOP、ConOut、BDS仍未获实机成功证据。原媒体本地，只询问确有歧义字符。源码/文档统一发布，网络不阻塞本地工作。
