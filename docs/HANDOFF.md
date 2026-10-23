# 当前停点：失败对照已人工恢复，继续离线隔离与新软件

2026-10-23，Asia/Shanghai。838b38f的linear-control step3在23:16:54临时启动后75秒未返回，已当轮停止追加启动并落实全部交接文档。用户随后确认回Android，主机于2026-10-23 23:20:44核验enuma/boot_completed/root/原槽/解锁/原分区摘要全部通过。当前设备已恢复Android，不再等待人工按键。

失败候选SHA a8061b8510935bbe8991ec0d8723a1bcc3b1a9460422ecc9ac30ffe13813016a，不能原样重试；step10镜像已完成离线构建/审计但没有实测，不得绕过对照停点启动它。R-004映射不变，未发生像素/寄存器写入或分区操作。

离线进度：与17aa47a成功对照解包比较，DxeCore/OEM叶载荷一致，SimpleFb和Pcd差异仅RSDS调试标识八字节；SEC存在编译时间字符串及引用布局变化，压缩级联改变整包。故障PC/根因未知，不声称新增格式代码导致失败，亦不声称SEC布局就是根因。64主机用例/对象和两份838b38f完整构建/bundle四负例/workspace均通过，证明离线构建而非实机通过。

接下来按用户要求持续离线：稳定SEC编译时间造成的构建布局变化，重放相同输入检查产物一致性，再准备新的安装后返回基线（step0）而非重复失败step3。该软件尚在准备，不声称修复或新镜像通过。新的设备动作仍须身份/备份/恢复和故障隔离门禁，超时停追加并优先恢复，真实硬停当轮写交接。

源码与发布：固件838b38f已推送，设备源锁/gitlink在工作树与之匹配；设备已推送最新文档3161bf4，本组实现/恢复记录待本次提交发布。参考仓只读，内存/verified/分区边界不变。无待批准项、无按键待办。证据reports/enuma-linear-control-timeout.json、enuma-linear-control-offline-diff.json、operations/2026-10-23-linear-control-timeout.md；恢复录像out/camera-capture/20261023T231903，601帧完整解码。

接手先读AGENTS/STATUS/DECISIONS/NEED-REVIEW。此前step9地址存在性实测成功见operations/2026-10-23-scanout-address-layer.md，历史事实留WORKLOG；当前不要误把已恢复当成可直接追加step10。
