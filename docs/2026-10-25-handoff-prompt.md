# 当前状态：D-193，S-007已恢复，最新上游复审后调整路线

2026-10-25（Asia/Shanghai）S-007 point22于16:03:54发出，命令2.640秒返回/5.109秒断开，75秒无Android/fastboot返回；镜像dedd87a68a005817d8ee2d95c60d7949b244bdc31c974e1bd4c760d817c25361已consumed，不重试。用户反馈Android，16:06:22独立完成/root/A槽/解锁/原boot_a与vendor_boot_a及备份摘要通过，453/453主录像、739/739恢复录像可解码。当前Android恢复完成，无人工或审批待办。原始影音仅本地，不上传Git/Release/CI。

按用户“下一步决策前看最新官网、其他设备及仓库”完成复审。官网已是schema2/SoC+OS profiles/组件目录及porting.toml路线；最新框架16e592abee8a550dec8154ed1f38b5ebc4f16213与本仓pin为diverged，不作整体快进或换底座。最新审查源另放out/sources，固定config/upstream-route-review-20261025.lock.json；8仓40文件资格和cas纯显示解码/Blt16项主机测试通过。没有修改构建依赖锁/board/plan。

新主线建议：先离线评估同SM8250且有UEFI菜单/EFI返回记录的cas继承扫描输出GOP，取得可见错误通道；OEM构造器真实服务取证降为备用，不再默认追加同类更深早停。cas当前casPkg与实测893f5025目录无差异，但其固定内存/1080x2340面板/像素和CTL_START写入不适用于直接复制，也未获新写入资格。仅复用纯快照解码和边界方法，先对enuma本机FDT/固定SDE定义/几何、分块、格式、secure/UBWC和刷新条件做离线适配审计；若条件不满足则拒绝或回备用，不放宽判据。新GOP尚未实现、构建或上机。

共享UniXNURamDiskDxe已在最新上游实现，应优先复用通用代码；但它要求整个initrd是512倍数，本机2230字节vendor前缀+96MiB FAT的预测范围余182字节，不能无适配替换当前精确前缀/范围/CRC保护。运行时FDT仍未知。AdvancedLogger/QR可复用但依赖可用GOP/菜单、输入与日志生产者，不能直接修复当前菜单前黑屏；恢复可见菜单后再接。主机debug_terminal没有匹配设备端CDC后端也不会新增enuma早期日志，不复活R-002。

umi仍是同SM8250/同donor系统、UFS/root/Data的首要参考，审查HEAD未变化，手机地址不复用。elish和Tlrenhb另一enuma仍是骨架而非新实机基线；官网wh1stl3段落转述本仓旧记录，不作独立证据。fajita SDM845的特殊槽/分区命令不继承。sheng最新源码可选OEM或继承SimpleFb，但SM8550驱动/内存不复制。

详见operations/2026-10-25-latest-porting-route-review.md（固定版本、源码行为、网站链接、适用边界及新推进顺序），机器证据reports/enuma-latest-porting-review.json。审查器audit_latest_porting_review.py不访问设备。S-007后无新boot、固件功能实现、像素/MMIO写入。后续先完成可审查离线适配，再满足源码/产物资格/文档推送/即时恢复门禁；有具体新增像素/MMIO范围时按AGENTS精确规则处理，当前不请求批准。

构建仍锁firmwarecb9e568/UniXNU5fdbd5d，完整96MiB系统FAT保持。所有已执行镜像consumed；没有flash/erase/改槽、内存字段或verified变化，R-002/R-015/旧像素硬边界不变。仍无13项RAM运输、GOP/XNU/iPadOS运行通过证据，PMGR/UFS/root/Data契约未闭合。
