# 当前：far-clock-v9三份镜像与软件资格完成，未上机（2026-10-28）

2026-10-28当前：far-clock-v9目标及2/22秒校准镜像已完成完整build4、qualification1和离线来源校验，三trial均未claim/上机。移除诊断晚期GOP/像素出口，保留真实OEM/Core和整轮DXE路径；52项Python与最终机器码删除负测通过。实际时钟校准未完成，目标execute需新low/high报告与精确计划；v8已consumed且恢复通过，不复用旧拍摄就绪。现行STATUS/HANDOFF及operations/2026-10-28-oem-far-clock-v9.md；以下旧当前/准备文字按历史阅读。

### target — oem-far-clock-v9

- 镜像：`out/oem-far-clock-20261028/target/qualification1/image.img`，3153920字节。
- image SHA256：`3691d5989d9f50ead22f995b240644e58b579693d7f3db4f6b9d4329215f8e96`
- qualification1 SHA256：`dfea3b0f95e34702129485b6ba95fbd9599c2226101410dab6e67a7769a46858`
- FD SHA256：`577dde36ceba29e78393ef6d1a1d34a457686592f72d4d19c4ef0ba64146018b`
- trial：`96b78e34-892b-4ac1-b84d-8d3cc74a1f82`；session：`10889924087055404375`；未claim。

### low — oem-far-clock-low-v9

- 镜像：`out/oem-far-clock-20261028/low/qualification1/image.img`，3153920字节。
- image SHA256：`422139ef5b0d26bd4887c21b67e004331d3ca220c74077799cb3c77c848f6ab4`
- qualification1 SHA256：`cf07716a197bc08d70dad9c5144cc5424b971686f82e8baf6c4ef13dcb56ea44`
- FD SHA256：`76b1659f70e1cb13f0806bc6b27ed0afc1411b768df85b76a8cf21258fc5bcb7`
- trial：`d07aaceb-e633-42c3-9746-7c2304740a8b`；session：`72241299989157236`；未claim。

### high — oem-far-clock-high-v9

- 镜像：`out/oem-far-clock-20261028/high/qualification1/image.img`，3153920字节。
- image SHA256：`b8980a2d309b42b8b9207ac63fe8e0ab7ba68d545bfa97777071ed721277ce97`
- qualification1 SHA256：`3a8d1876bf807e1d4ca8845006e86809b5daf40c42ee7a380af4b65a18cc52c4`
- FD SHA256：`38e3113afdf34d8cc86cb3113c274039371a0d93c9966d8ca6692c6195e23889`
- trial：`0e8e88d1-faea-4829-8b8c-93ebbece2544`；session：`360695613987928583`；未claim。

## 当前改变与证据边界

v8在修复可复现通知竞态后仍由用户报告无页并自行返回，不能继续把该竞态当唯一原因。最大可操作方向是区分末端显示拒绝、提前终止和真实DXE返回。v9保留精确原厂DisplayDxe PE、私有SystemTable同步、v8 RAM事件临界区和真实CoreStartImage状态，OEM中途不绘制/等待；整轮CoreDispatcher返回后选计时终点，BDS前复位。诊断出口不再查询晚期GOP/Mode或读取MDP/像素。

目标类1/2/3/4/5分别等待2/7/12/17/22秒：受控异常、诊断terminal、DXE返回而缺少匹配Core返回、DXE返回且真实Core状态非零、DXE返回且真实Core EFI_SUCCESS。low/high强制2/22秒，只作时间对照，不能证明Core返回。不是独立看门狗；可变执行前缀和未包装复位仍会别名，时间码只能作间接推断，不能替代生产GOP/ConOut/BDS/输入/XNU验收。

三份最终FD/原厂PE及panel RAW/编译flags/Boot v3封包和解包回读通过；每份2470来源绑定，同一源码指纹。实际helper和真实Core配置表/绑定/ARM64编译及ASan/UBSan、v7竞态复现/v8修复/删hook负测通过，52项Python通过。实际链接目标/low/high逐条删除负测99/82/90处，覆盖真实返回身份/状态门、表发布同步、RestoreTPL前事件交付、Recorded回调地址、计时与CPU默认异常出口，限选定序列，不是完整控制流证明。

最终隔离build4基于49affe7工作树快照；固件现提交edc579d9e02beb7e395f4bad680329adf07b70bb，不称提交后重编。build1 unused-helper、build2定向中止、build3旧捕获头依赖失败原样保留；以独立无预包含/无unused抑制的真实Core绑定ARM编译补足夹具，再构建build4。新FD审计逐项核对当前firmware与实际原始快照，阻止新源码给旧编译背书。patch UTF8 LF与隔离staging git apply --check均通过。

最后设备证据仍是v8：00:51用户确认自行回Android且无页，独立身份/完成/root/A槽/解锁和原分区/备份核验通过；没有本轮独立视频判读。本轮零设备命令，当前在线状态未刷新，无恢复欠项。R027/v6/v7/v8镜像及资格冻结摘要核验保持，唯一写入根为本worktree，D:/Code/PortingiOS/enuma/UniXNU-enuma共享主线只读。

## 下一步

1. 不重试已consumed的v7/v8，不从旧录像状态推断本轮就绪。新low/high/target每份均独立单次trial，无自动轮测。
2. 沿既有临时boot授权准备本次现场，重新核对当次拍摄/人在场可恢复、即时enuma身份/原备份/原双分区/恢复路径及文档发布。先low，独立核验恢复和人工确认自动返回；再high同样处理。
3. 只有low/high启动原点区间<=0.25秒、新boot_id、同源码、各自自动返回及独立恢复通过，扣除2/22秒后基线包络<=1秒，才生成绑定精确目标、有效一小时的计划。target execute缺计划或过期/错源/错图时在claim和任何设备命令前拒绝；不能以Android总就绪耗时直接解码。
4. 两份完整控制报告包含automatic_android_return=true、independent_recovery_passed=true与原clock_observation。用scripts/oem_exit_clock.py --low <report> --high <report> --qualification <target/qualification1/qualification.json> --output <out/plan.json>生成计划，再按即时门禁单独执行目标。target完成后报告须同样确认自动返回与独立恢复，decode只给间接类别；漂移/歧义/人工恢复不作正向分类。
5. 每次75秒未回合格终点先停止追加并恢复，原样保留状态；恢复后离线分析。无flash/erase/改槽、内存base/size或verified变化。原始媒体/out/二进制/备份/设备标识不得入Git或云端。

默认离线入口（不带execute，无设备命令）：

```
wsl --cd /mnt/d/Code/PortingiOS/enuma/worktrees/enuma-oem-display /usr/bin/python3 -B scripts/run_oem_runtime_trial.py --qualification out/oem-far-clock-20261028/target/qualification1
```

详见operations/2026-10-28-oem-far-clock-v9.md及reports/enuma-oem-far-clock-v9-candidates-20261028.json；原始证据out/oem-far-clock-20261028。源码/脱敏文档按固件→设备仓顺序发布到显式GitHub URL/oem-progress-20261027；不向固件origin（共享主线）推送，不force、不改main。实际发布以git log和out/oem-far-clock-20261028/publication.json为准。


## 2026-10-28公开源码与其他设备仓核对补充

本轮只检索/静态对照，无固件修改、重编、设备命令或v9资格/镜像回写。报告reports/enuma-oem-public-research-20261028.json记录17份固定提交公开文本的URL/SHA256，原文仅留out/public-research-20261028-v9；本机原厂PE仍6c6351c3...，14处新增选定指令核对通过。

新增可操作定位：公开ChipInfoTypes把family93定义为SDA865/SM8250。本机0x3620确实比较93，后续0x3640查询Clock GUID 241afae6...，0x3668/0x3694分别调用+8 GetClockID/+16 EnableClock，字符串为gcc_disp_ahb_clk、disp_cc_mdss_rscc_ahb_clk、disp_cc_mdss_rscc_vsync_clk。此为v6最后入口页到后续HAL查询前的一段未包装方法区间，实际执行/返回未知；EnableClock返回后未检查状态，不能把前面的Locate成功当三路时钟已启用。

历史SID简称的54b6d3b4...由公开QcomPkg.dec对应为HAL IOMMU/SMMU。精确本机查询位于0x1bcdc（返回0x1bce0），随后调用协议+8获取函数表，再调表+0/+64/+16，带客户端\_SB_.MDP；旧公开表对应create/configure-bypass/attach，精确本机HAL提供者ABI/返回/资源仍须独立核对。当前Kona源码早期MDP detach不证明OEM后段不重新attach，不复制外机stream IDs或改MMU/内存字段。旧公开HAL样例先发布协议再执行可能失败的dummy初始化，说明Locate成功本身不足证明提供者完全就绪；不推断本机必同实现。

其他仓证据边界：Mu-Silicium nabu=SM8150-AC/custom-display1，pipa=SM8250-AC/custom-display0；早期LonelyFool SM8250使用PCD SimpleFb，不能当enuma原厂DisplayDxe成功样例。公开旧版高通DisplayDxe可能发布GOP但Mode=-1，后续SetMode才填framebuffer；EDK2 GraphicsConsole在DriverBinding Start中QueryMode/SetMode，不能把DXE dispatch完成等同控制台已连接。Aloha DisplayCaller/Silicium ReEnabler有真实显示电源off/stall/on路径，是协议/模式确认后的条件方案，不是当前入口故障的现成修复。ChipInfo头宏61224fbe与DEC b0760469的差异在其他实现也有记录，当前本机原厂查询/追踪已用正确b0760469，不改GUID。

判断更新：尚无唯一根因或可直接套用的enuma修复；下一重点已具体到SM8250显示前置时钟和HAL IOMMU方法链，同时保留“已走远但诊断出口拒绝”的解释。v9三图/校准门禁保持；未来新实测先当次low/high，再target，不沿用旧拍摄就绪。若取得真实Core/DXE完成的合格间接码，再独立推进GOP发布→QueryMode/SetMode→显示电源/ConOut，不把返回成功作为生产GOP验收。
