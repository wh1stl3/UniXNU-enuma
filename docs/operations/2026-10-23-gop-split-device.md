# GOP 拆分 step0/step1 实机结果

2026-10-23，Asia/Shanghai。用户明确授权重新核验设备与恢复条件，先step0，受控返回后继续step1；并在场可进行电源/音量下恢复。两次均确认全程未按键。

## 结果

| 候选 | 临时启动时间 | ADB返回 | Android完成及摘要核验完成 |
| --- | --- | --- | --- |
| step0 安装后返回 | 21:10:18 | 16.906秒 | 30.438秒 |
| step1 枚举、校验与释放 | 21:11:37 | 15.844秒 | 30.547秒 |

两次runner返回0，Android完成/root/boot_a及vendor_boot_a原摘要通过。每次启动前重新核对唯一enuma、原槽A、解锁、备份文件摘要与当前分区摘要；fastboot product/current-slot/unlocked全部通过且无重试。第二次恢复后另行核对enuma、完成1、槽_a、locked=0。恢复终点均为Android，未依赖人工按键，无flash/erase/改槽。

固件e286834，core-warning-v2，selector1、stage13/detail16/delay2、完整SimpleFb GUID与七秒正常完成兜底。重跑scripts/check_gop_split_bundle.py通过，镜像摘要与既有报告一致。仅运行scripts/run_enuma_entry_probe.py的两份新候选，未运行旧相机编排器或旧失败/互补镜像。历史blocked标志依据新拆分审计和本轮明确授权人工复核，不把runner未消费标志视为自动许可。

执行命令：Windows Python以-X utf8 -u -B运行scripts/run_enuma_entry_probe.py，--label dxe-driver-return，--image分别为config/gop-split-probes.json两variant在out/boot-candidate下的-boot-v3.img。命令输出、身份响应和result.json保存在报告对应私有目录。

## 证据解释

两次无按键自动返回且短时序接近既有短门，支持新阶段标记/Core返回路径可用及step1枚举/释放整体返回。没有同版本延时对照或数值EFI日志，不能仅凭时序唯一证明目标门命中，也不独立证明每项校验成功。旧250849f超时根因仍未知。

step1不执行HandleProtocol、Mode检查或QueryMode；没有数值GOP快照、真实scanout、像素、菜单或XNU通过。禁绘制/Probe早退保持，同步兜底仍不能救服务卡死。

## 采集与后续

遵循无绘制不持续录像偏好，仅保留启动前与两次返回后的USB相机截图、主机日志/时序及用户无按键确认。相机第一次因旧cp313 numpy与当前cp312运行时不匹配失败，改为先导入已安装numpy再运行既有截图脚本后正常；设备启动之前已取得有效截图，未修改参考工具或安装依赖。

私有截图目录：out/camera-capture/20261023T210938、20261023T211042、20261023T211155。前后画面为Android桌面/锁屏，截图不覆盖中间过程，不用于证明中间黑屏或无按键。结构化脱敏证据：reports/enuma-gop-split-device.json。

本轮止于step1。下一步离线准备step2（HandleProtocol）完整链接/打包/审计；如需增强门命中证据，先做同版本step0延时对照或同step selector2分类，不混入旧250849f。后续实机仍逐笔重新核验恢复条件。原内存、example、verified、R-002边界保持。
