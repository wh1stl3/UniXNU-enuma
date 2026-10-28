# v13实测：VBIF翻译异常未消除

本轮临时启动成功发送，用户确认自行返回Android、三页日志，独立身份/root/启动完成/A槽/解锁及原双分区与备份核验通过。trial已消费，不重复启动。原始媒体本地保留，28.277563秒；三页字符清晰，独立转录后与资格session 0x4229413d4b327cfc匹配，无需人工字符复核。

| 字段 | v13 |
|---|---|
| PC | 0x9a6fd140 |
| ESR | 0x96000047 |
| FAR | 0x0aeb0004 |
| 镜像基址 | 0x9a6d2000 |
| RVA | 0x2b140 |
| LR | 0x9a6fd120，RVA 0x2b120 |
| GUID | 4138022f-06c7-4f79-9c94-7e33b511a4e7 |

本轮FD清单唯一匹配DisplayDxe，PE SHA256 6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425。精确PE指令0xb8154128为 `stur w8,[x9,#-172]`，向VBIF+4写32位。ESR EC=0x25、DFSC=7、WnR=1、FnV=0：同EL data abort、三级翻译故障，有效FAR。

与v12相比，镜像加载基址、PC和LR一起下降0x2000，RVA/ESR/FAR/原厂PE保持相同。这是重定位变化，不是执行推进；不能宣称越过VBIF或已到DSI，也没有OEM返回、整轮DXE或生产GOP成功证据。

v13软件资格确实验证了源表、实际SEC与最终FD TE的VBIF/DSI描述符字节，却未验证故障时活动页表。这次现场表明新增静态描述符不足以消除故障，不能继续把“未加入表”当作完整解释。

当前实际MemoryInitPei.c将除HobOnlyNoCacheSetting以外的全部描述符顺序转入MemoryTable，物理/虚拟地址相同后调用ArmConfigureMmu；VBIF属于AddDev，不受该跳过条件影响。优先分析同一2MiB块中MDP/VBIF/DSI/DISP_CC多次映射如何更新页表、最终链接实现及后续DXE属性修改；用实际页表算法离线复现，并在必要时取活动TTBR/TCR及目标叶表项，分清从未建立与后续丢失。当前未证明其中任何一种是根因，不再盲目扩大窗口。

完整寄存器及转录见 `reports/enuma-oem-display-map-v13-live-20261028.json`。本地证据 `out/oem-display-map-live-20261028`。旧镜像和资格保持冻结。
