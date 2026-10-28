# v12 接续交接：软件完成，未消费

2026-10-28当前：v12（oem-exception-dispcc-v12）已完成build2/qualification1与新来源绑定，新增DISP_CC 0x0af00000/0x20000 NS_DEVICE映射，保留真实OEM/Core/GOP与v11三页异常取证。66项Python、8组宿主验证及最终链接/FD映射检查通过；软件就绪，尚未上机，trial未消费，不能复用v11拍摄就绪。旧镜像/资格冻结，旧源码准入失效。

用户已批准制作该范围的v12；不改board.toml/bringup-plan RAM字段、verified、分区。本轮无设备命令，共享主线只读、R027冻结。v11已消费且自动回Android，独立恢复核验通过；当前在线状态未重新查询。

## 精确候选

- 镜像：`out/oem-dispcc-20261028/qualification1/image.img`，3153920字节。
- 镜像SHA256：`a14b999f39c590b1c0a43ea3f4cdb560396d713c03b5641d41c4f40fa6797e5c`。
- FD SHA256：`d927b6f738b355c630bcfd76ce707a0298b1a589ebe4235a7f6545aadbed7ecd`。
- 资格SHA256：`91cdb1afbb9779e69e0ac8a1113f6080f3fc4563d57f1058001a8f4b2ba0a761`。
- trial：`9da1688c-96a7-4adf-9774-f4661f5a5d13`；session：`0x509d1d695c7e0fdc`；未claim/未启动。
- 固件提交：`9d7b56d49faeb3bc2f5236e10b3a9970c08a9edf`。build2使用工作树快照并由source-manifest逐文件绑定，不称提交后重编。
- 2492项来源绑定，72个FD PE镜像，另独立验证SEC TE；22份旧镜像/资格摘要保持。

## 证据和下一步

v11明确故障：ClockDxe+0x11d58读取0x0af022c0，ESR0x96000007；v12修复对应平台映射缺口。生成内存表除该条外与v11相同；实际链接描述符、最终FD中SEC TE及地址/长度/属性删除变异检查通过。宿主验证包括真实异常sink的ASan/UBSan、严格ARM64、真实Core表同步、事件竞态及GOP失败清理。

详见 [v12操作记录](operations/2026-10-28-oem-dispcc-v12.md)、[结构化报告](../reports/enuma-oem-dispcc-v12-20261028.json)、[v11故障分析](operations/2026-10-28-oem-clock-fault-analysis.md)。本地证据在out/oem-dispcc-20261028，源码/文档最后统一发布，网络不阻塞本地工作；发布receipt另记out及最终答复。

下一次仅在当轮拍摄/在场恢复、即时enuma身份/原备份/分区及精确资格门禁满足后，单次临时boot此新镜像。默认离线准入入口：

```text
wsl --cd /mnt/d/Code/PortingiOS/enuma/worktrees/enuma-oem-display /usr/bin/python3 -B scripts/run_oem_runtime_trial.py --qualification out/oem-dispcc-20261028/qualification1
```

保留75秒主机观察期限，非固件自动返回保证；没有异常页不能视为成功。若有新PC/FAR，先归属镜像和指令；若同地址仍异常，检查实际页表及运行中修改；后续电源、权限、时钟握手、HAL IOMMU仍可能成为下一卡点。未证明OEM返回、全DXE或真实GOP成功。无时钟校准，不按返回时长分类。原始媒体本地，只有辨认困难且影响结论的字符才请用户核对。
