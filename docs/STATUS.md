# STATUS

更新：2026-10-23（Asia/Shanghai）。当前唯一真相，历史见WORKLOG。

## 当前状态

**离线推进FAT发现与源内核平台链接；实机仍留到晚上。** 本轮零设备查询/启动/写入。最新设备查询仍是15:18 UART只读enuma/root/Android完成1/槽_a；原boot/vendor_boot摘要核验仍为12:11人工恢复记录，不是本轮重读。233a9d8首次黑屏未自动返回的历史失败保留。

## 本轮结果

- 生成64MiB配置专用FAT32，唯一ENUMA FAT DISCOVERY 01标签，仅reset动作，无kernel/EFI/ADT/Data。固定官方write_volume后校验双FAT、清空空闲簇，解决实际尾簇非确定字节；两次产物逐字节一致，mdir清单和mcopy回读通过。SHA567431ade5af6d74cd963ded01d74d568babcd0995cfb5a92036e0b76fde9fb7。未打包boot或接入publisher，10秒菜单倒计时遇输入会取消，不是复位保护。
- 固定六份归档配方，复用sheng通用builder。首轮CI39926725474/head a801314通用bootstrap及crypto plain/namespace、pthread通过；第4步ArmDTPlatform因Apple Clang不支持的warning在-Werror下失败，未平台链接。精确补丁仅移除该开关，保留其余warning/Werror，原参考源不变；隔离apply/输出hash通过。
- 第二轮CI39927966148/head250cdf9成功，四个真实归档与按既有defconfig的源内核链接通过。下载内核21417672B，SHAb940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d；本地锁定NativePrelink解析器复核普通ARM64/可执行入口/双4K TCR/iOS17.0及真实平台、CPU、pthread三符号通过。配方补丁、run/head与功能开关一致；首轮失败证据负向测试拒绝。仅源平台链接，未预链接donor或启动。[实际CI与本地复核](../reports/enuma-platform-kernel-ci.json)。
- 原boot/vendor_boot备份与保存的Android FDT离线摘要重核通过：历史initrd50124652B=generic50122422+vendor2230，mod512=364；整段块发布要求不成立。临时候选实际chosen/FAT偏移/可读保留范围仍未知，不裁剪或取整猜测。

见[本轮实施与证据](operations/2026-10-23-discovery-volume-platform-link.md)、[FAT报告](../reports/enuma-discovery-volume.json)、[首次CI失败](../reports/enuma-platform-kernel-first-failure.json)、[历史运输证据](../reports/enuma-initrd-transport.json)。53项Python、固定配方/源锁、串行workspace与晚间bundle检查通过。

## 现有固件与晚间计划

固件82ce8a5/50源锁不变，已有三候选：早期加载前2秒、完整SimpleFb GUID调用前2/7秒；晚上早期→2/7/2四次，末次严格复用同镜像。实际AArch64/官方core还原/30OEM/FD/192B BootShim/raw/v3及源/宏/摘要检查通过，全部未实测。正常Dispatcher完成7秒兜底不是异步看门狗，目标7秒与兜底单次不可区分。

SimpleFb已有配置重试/描述符跨度修复，真实Mu Configure/完整驱动/BootVideo host sanitizer与目标构建通过，未证明首次黑屏根因。默认原生33、无UFS32、SimpleFb30选择保持；metadata Blt禁绘制、Probe早退，现有三候选不会到菜单。EnumaScreen受控GOP Blt文本后端host sanitizer/AArch64对象通过，但无INF/FDF/调用者集成或全链接，memset运行时待核，尚未上屏。见[屏幕后端](operations/2026-10-23-bounded-screen-renderer.md)、[晚间计划](operations/2026-10-23-evening-validation-plan.md)。

UART软件线索ttyMSM0/115200n8、serial0=988000/GPIO117/118，但console disabled、无活动ttyMSM，998000是另一绑定。实物接点/电平/UEFI输出未知，USB/ADB不等于UART；依用户选择保留屏幕路线。

## 系统与内核边界

目标enuma/SM8250、iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB、UniXNU5fdbd5d/21模块。旧通用bootstrap功能全关；新源平台内核已实际链接四服务，仍缺donor预链接、完整ADT、实际UEFI窗口/EBS与硬件基础平台证明，尚非可启动候选。kernel.archives/opt-in/prelink/ADT工具尚未接回正式board构建，不以限定CI替代完整设备构建；运行初始化/密码自检未验证。

FAT载荷、OS/SystemOS只读根镜像、Data分开；NativeUfs含SM8550硬件参数且当前禁用，根卷载荷还要求未接入的PMGR契约。GPT/UUID/Data seed未定，未下载大DMG/生成系统卷/写userdata。固定userdata dry-run不比较展开后容量。详见[系统预研](operations/2026-10-23-system-kernel-userland-roadmap.md)。

51MiB DXE Heap、512MiB owned、内存/example/verified均不变。R-002跨Bootloader不保留，持久日志仍停，不换地址/扩大/借DFPS或SMEM。build/workspace qualification保持串行。尚未验证SimpleFb入口/返回、GOP可见、真实scanout、BDS、XNU、存储根卷或NT36523；UART/TWRP未验证。

## 下一步

下一轮离线审查donor解压Mach-O与预链接roots/依赖/AMFI入口/slide，并把已成功配方接回正式板级构建；不复制外板常量。实机开始时重新核对身份/备份/原摘要/在场恢复条件，按既有四次顺序逐次检查Android/root/分区摘要；任次无返回停追加先恢复。入口门命中不当作驱动/协议成功。候选实际x0/FDT/UEFI map取得前不接initrd发布；新内存/verified或破坏性分区操作仍按编号审查，无新待批准项。

设备已推送250cdf9，固件82ce8a5；本轮补充发布见Git/WORKLOG。参考仓只读，产物/原始设备数据仅out。
