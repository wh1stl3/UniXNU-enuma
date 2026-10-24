# 当前进度：step14 两次读即挂死，硬停待人工恢复

2026-10-24 Asia/Shanghai。**硬停中**：17:31:23 临时 boot `exit14-minimal`（step14，仅两次只读 `0x0ae6b800`/`0x0ae6c000`，无等待无写），75 秒无 ADB/fastboot 返回，17:32:38 停止追加。相机快照 `out/camera-capture/20261024T173305/` 全黑。

## 待用户执行

长按电源回 Android 或 fastboot，然后由主机独立核验：enuma 身份、`sys.boot_completed=1`、root、原槽、解锁、匹配备份、`boot_a`/`vendor_boot_a` 原摘要。

## 本轮对照（同一台设备、同一小时）

| 候选 | 探针深度 | 笔数 | 挂死 |
| --- | --- | --- | --- |
| exit10-early（stage10 派发前复位） | 0 次 MMIO 读 | 5 | 0 |
| exit14-minimal（step14） | 2 次 MMIO 读 | 1 | 1 |
| step20 完整只读（今日） | 250 次读 | 4 | 1（最后成功 16:38:36） |

exit10-early 五笔 adb 15.918–17.007，delay7 正对照 21.277 证明 checkpoint 执行且复位生效。

## 判断

主判断（高置信）：挂死点在第一次触碰显示窗口 `0x0ae00000..0x0ae84207`，与读多少寄存器无关。exit14-minimal 带 7 秒 completion fallback，PASS 或 FAIL 都会回 Android，只有真挂住才 75 秒无返回。

状态假设（中高）：窗口可访问性随启动序列变化。16:38 同窗口读 250 次成功，之后五笔 stage10 在显示驱动前复位，17:31 同窗口读 2 次即挂。机制可能是早期复位让 XBL/ABL 认为显示已初始化，下次启动跳过，UEFI 读落在未上电域上挂住总线。可解释 S-001/250849f/S-002/S-003 反复出现。

## 恢复后第一步

**完全断电冷启动**（不是复位），再跑同一份 `exit14-minimal` 一次：

- 干净返回 → 启动序列假设成立，转查 XBL/ABL 显示初始化与 UEFI 早期复位的交互；
- 同点位挂死 → 假设回落，问题回到镜像侧需重新分解。

## 边界

R-005 consumed；禁像素/MMIO 写、新映射、内存字段、verified、分区写；51MiB heap、512MiB owned、example=true、Boot v3 保持。TWRP/UART 未验证；无可见日志；未进 XNU。冻结镜像不重试。

证据 `reports/enuma-exit14-device.json`、`reports/enuma-exit-early-device.json`、`out/device-tests/20261024T173123-dxe-driver-return/`。

接手顺序 AGENTS/STATUS/DECISIONS/NEED-REVIEW。
