# Session handoff — 2026-11-14

当前任务停在交接；新会话不要自动恢复实现或设备操作。以下状态由主控提供，历史候选叙述不覆盖本交接。

## 主线与观察

- 最终目标不变：真实 UFS 的 userdata 持久 iPadOS 根与设备内载荷，界面可交互且断电重启后仍可交互；GPU 等外设后置。
- 用户接受 vendor 异常返回后旧 DMA backing 已释放或复用而退役未完整证明的残余风险，按官方 ShengUfs warm/alioth 整链继续；不再作为当前主机实现前置阻塞，具体故障时回查。这不是 DMA 安全或持续所有权证明；默认 NoAccessPolicy/NoContract、设备授权和正式阶段不变。
- 六读 r2 单次实机 101/101、context 6/6，模式 Observed：SID e0→CB3、4e0→CB2；CBAR 1f000、CBA2R 1、SCTLR e0；之后 rootwait，非 abort。该 claim 已消耗，禁止访问、删除或重放；不证明 root 或持续所有权。
- 最近一次授权普通 reboot 后观察到 Android 13 root ADB 成功；这不是新会话的实时设备状态。当前存储 GPT 证据 `.cache/android-ufs-identity-gpt-20261114-201917/`：4096B、LUN0 total 61880320，userdata [2686976,61880315)，主备 CRC 已核。serial、GUID、视频不入 Git。

## 下一实际候选：warm capacity r2

- 阅读 `out/ufs-native-warm-capacity-20261114-r2/DELIVERY.md` 和同目录 `execution-binding.json`。boot `package-lu0-r1/boot.img` SHA-256 `3b094db25cf727fda0ab34372fe5eaf28f85f4ff3fc24b29efadadfa6a9b6c80`；manifest `final-audit-r2/candidate-manifest.json` SHA-256 `735e8588d47d1cacd9c010470083f4c7ffd6265ad87888c34e09174418fd65c1`，均相对该候选目录。
- 91 executor + 2 issuer 与最终构建仅 self-checked；普通 review `ses_e25fa5684ffe4Zhiu2Qdr1ZplD` 静态 PASS，High deep `ses_e25f7b4a2ffeewMQtSDZycgJbo` CLOSED。旧 r1 冻结，不得执行。
- 范围仅 NOP + LU0 RC10，涉及 HC 写与 DMA；不读 GPT/数据块，不进入 store/root。末屏十行 `WARM-CAP2` → `NO ROOT/NO BLOCK READ/NO STORE`；成功判据 `COMPLETE GEO MATCH`、op25 LU0、OCS/SCSI/PROTO/res/err 均 0、last `03b037ff`、bytes 4096、poison 0。
- 此 boot 尚未获用户授权，完成交接不是授权。新会话须当轮授权、按型号唯一识别 enuma 并走原子新 claim 流程，不能复用六读 claim。

## 生产整包

`out/production-complete-20261114-r1/` 为 self-checked、静态限定 PASS：实际 OS/SystemOS/owner/trust、3GiB Data seed 和安装布局已备；192MiB payload，boot 203505664B，95% 余 65408417B、window 余 392495104B。root 9382658048B，Data store 3221327872B，布局见该目录 `INSTALL-LAYOUT`；不得凭历史参数刷写。尚未安装 userdata、未部署，NoAccessPolicy/NoContract 不变。

## GOP 暂停交接

用户明确暂停，后续由新会话接续；专项交接为 `out/enuma-gop-production-20261114-r5/HANDOFF.md`，固定输入、许可和恢复入口以该文件为准。已写本板 Legacy consumer、ABI 模板及构建和测试脚本，生成显示 archive、native/prelink 与完整生产包；host 自检和最终 audit 为 self-checked，未部署、未实机验证，`release_allowed=false`。

`seal.py` 尚未运行，sourcepin/device patch 生成及精确重放、独立 patch 重放和最终 `audit.py --verify` 均未完成；当前 manifest 为最后成功 audit 的快照，尚未覆盖其后新增的 DELIVERY、seal 和 HANDOFF。此前一次超时命令的子进程状态未调查；新会话恢复前先确认旧 WSL audit/llvm-objdump 子进程状态，避免重复任务，不主动杀进程或删除产物。显示实际运行、触摸及持久 GUI 均未完成。

## 工作纪律

批次 self-check 复用未变结果；额外独立 verifier 须用户同意，仅刷 userdata 前适用最终独立复跑一次；不因每个候选默认全重建。保留全部未提交改动，不自行提交、推送或删除分支/产物。
