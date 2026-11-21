# enuma r8 单次实机观察（2026-11-21）

状态：`self-checked`，记录主控提供的操作和录像核读；阶段不提升。本文不声称独立复核或重跑。

## 授权和操作

- 18:00 用户当轮授权一次 `fastboot boot`。唯一命中设备的 `getvar product` 为 `enuma`；序列号按项目规则不入库。
- 镜像 `out/ufs-sm8250-launchd-display-20261120-r8/boot.img`，169,951,232 B，SHA-256 `0797330553b8cd1e5c2833dadb70a29ae816a490ae63c172b6fd8cde00339779`。
- claim `.cache/enuma-timebase-r8-20261121.claimed` 于 18:00:44 创建，已消耗，禁止访问、删除或重放。
- 18:00:49 发出一次 `fastboot -s <enuma> boot <上述镜像>`，exit 0：`Sending 165968 KB OKAY 4.044s`、`Booting OKAY 0.260s`。无重试、无刷写、无 erase。
- 现场录像 764.071 s、1920×1080；以 1 fps 抽帧至临时目录，影像不入仓库。

## 时基探针

`key_10s` / `f_0030`：

```text
enuma-tb: enter seq=0 cntvct=2864181823425 abstime_ns=149176136636145 cal=149176.136636
```

`f_0030`：

```text
enuma-tb: exit seq=0 cntvct=2864277864946 abstime_ns=149181138798854 cal=149181.138799
```

未出现 `skip`。cntvct 差 96,041,521 tick，abstime 差 5,002,162,709 ns；96,041,521 / 19,200,000 = 5.00216255 s，与 abstime 差值一致。这一次 `IOSleep(5000)` 已返回，按板内时基经过 5.00216 s。

录像的 10 s 帧可见 enter、30 s 帧可见 exit；30 s 只是上界。三个读数不是独立秒表，真实等待精确时长 **UNKNOWN**。`abstime_ns` 约 41 h 是计数原点未知的绝对值，不影响差分，不追查该绝对值。

## 显示

`key_10s`、`f_0030` 出现 `IOMobileFramebufferLegacy::start(IOService *): provider was not AppleARMIODDevice.`，因此 legacy 接线在实机执行到原版 `start` 的非 IOD 分支。所审画面全程未见 `EnumaLegacyDisplay:`、`refused stage=`、`unqualified backend slot` 或 panic。`EnumaLegacyDisplay:` 是拒绝路径才打印，走了不打印符合设计；这不证明 `stage==4`、backboardd swap 或 GUI 像素。

## launchd 录像核读

- 90 s：`launchd[1]`、`Early boot complete. Continuing ...`、`entering bootstrap mode`。
- 120–150 s：`amfid[26]`、`MobileGestaltHel[73]`、`tccd[77]`，多次 `pending spawn`。
- 480 s：`tccd[206]`、`tccd[222]`；537–542 s 六帧稳定显示 `tccd[222] triggered unnest of range 0x204000000->0x204200000`、`0x204200000->0x209600000 of DYLD shared region in VM map 0x6c9`。
- 600 s：`tccd[272]`，开始出现多行 `Failed to bootstrap path: path = …`；660 s：`tccd[285]`。
- 720/764 s：`tccd[315]`、`tccd[344]`、`tccd[354]`、`exiting bootstrap mode`、`spawn scheduled`、`spawned with pid`。至 764 s 底部仍出新行，未收敛。

未见任何 `exited` 行；缺同一服务前一 PID `exited` 与下一 PID `spawned` 的配对，是否循环重启 **UNKNOWN**。首轮核读的 `tccd[17]` 经 537–542 s 六帧复核为误读，已撤回；已确认序列从 `tccd[77]` 起。

失败路径可见前缀 `/System/Library/Launch…` 与 `/AppleInternal/Library…`，右侧截断。可见前缀与已核对的历史完整路径不同，不得按历史 donor 卷缺失路径结案；目标与影响 **UNKNOWN**。

## 三档结论

- **已确证**：探针配对返回与上述板内差值；legacy `start` 非 IOD 分支执行；launchd 进入并退出 bootstrap mode；多个 `tccd` PID 可见；至末尾仍有新行，所审画面无 panic。
- **强推断**：多个 `tccd` 实例先后参与启动；显示适配走了预期路径。
- **UNKNOWN**：真实等待精确时长、日志迟缓所在层、`tccd` 是否循环重启、失败路径身份、首个 GUI swap、用户态稳定性、持久 Data 与断电后可交互。

阶段不提升；本次记录无需 `decider` 或 `deep_reviewer`。

## 高帧率复扫（2 fps，480–764 s）

### 方法

主控提供的复扫结果：同一录像在 480–764 秒区间按 2 fps 重抽 568 帧至临时目录，不入库；分两段各 12 帧、每 12 秒一帧抽样核读，另对 537–542 秒六帧逐帧核读。本次仅整理转述，未重复抽帧或核读。

### 结果

- 24 个抽样帧与 537–542 秒六帧均未读到 `exited` 行；`exits` 出现在其它进程的 DYLD shared-region 行，不是服务退出。
- `tccd[17]` 系误读，已撤回：537–542 秒六帧稳定显示两条 `tccd[222] triggered unnest of range 0x204000000->0x204200000`、`0x204200000->0x209600000 of DYLD shared region in VM map 0x6c9`，位置六帧不变，属静止旧内容。已确认序列从 `tccd[77]` 起，依次可见 206 → 222 → 272 → 285 → 315 → 344。
- 672 秒，`(user/501/com.apple.SpringBoard)` 有 `service state: spawn scheduled` → `service state: spawning` → `Launching: system support`；同帧 `(user/501/com.apple.assistantd)` 同样有三段。用户域服务启动流程已推进。
- 684 秒，`(user/501/com.apple.assistantd [41]) xpcproxy spawned with pid 4…`，表明实际 fork；行尾截断，完整 pid 不清。
- 708 秒 `runningboardd [61] xpcproxy spawned with pid …`，720 秒 `mediaserverd [77] xpcproxy spawned with pid …`；两行行尾均截断。
- SpringBoard 仅读到 `spawning` 与 `Launching: system support`，未见其 `spawned with pid`，也未见退出行；右边缘截断与屏幕快速滚动使「卡在启动中」与「已起来但 pid 未入画」无法区分。

### 判读边界更新

- **已确证**：launchd 已推进到 `user/501` 域用户态服务启动；SpringBoard、assistantd、runningboardd、mediaserverd 均有 spawn 记录，后两者为系统服务；assistantd 实际 fork 出子进程。
- **强推断**：同一启动中 `tccd` 至少出现 7 个不同 pid（77/206/222/272/285/315/344），存在重复启动；未捕获 `exited`，不能写成 respawn 环。
- **UNKNOWN**：SpringBoard 是否成功运行；`tccd` 是否循环崩溃；`Failed to bootstrap path` 目标路径（右侧截断）；首个 GUI swap。阶段不提升。

## 第二次上机（完整取景，1504 s）

以下是主控提供的第二次上机、录像核读及同轮离线核对结果，`self-checked` 记录；本次未重复设备操作、录像核读或卷扫描。

### 操作

- 2026-11-21 18:39:16 +08:00 发出一次 `fastboot -s <enuma> boot`，exit 0（`Sending 165968 KB OKAY 4.184s` / `Booting OKAY 0.259s`）；claim `.cache/enuma-timebase-r8-20261121-r2.claimed` 已消耗，禁止访问、删除、重放。
- 同前述镜像和 SHA-256。录像 1504.340 s、1920×1080 HEVC 20 Mbps；约 40 s 起机位改为面板下三分之一特写。

### 时基（可重复性）

```text
enter cntvct=2302305033 abstime_ns=119911720000 cal=119.911720
exit  cntvct=2398344371 abstime_ns=124913760906 cal=124.913769
```

Δcntvct = 96,039,338，除以 19,200,000 为约 5.00205 s；Δabstime = 5,002,040,906 ns。两次独立启动、不同计数器基点均给出约 5.002 s，**板内差值可重复**。这些读数并非独立真实时间参考，不能据此确证时基相对真实时间正常；精确真实等待时长仍 UNKNOWN。

### 显示

出现 `virtual bool IOMobileFramebufferLegacy::start(IOService *)` 与 `…: provider was not AppleARMIODDevice.`。所审画面无 panic、无 `unqualified backend slot`；不证明 GUI swap。

### launchd

- 1019–1439 s 间可见 `xpcproxy spawned with pid` 从 4 增至 21，持续有新服务启动。
- 1019 s 起可见 `(user/501/com.apple.SpringBoard) service state: spawn scheduled` → `service state: spawning`；至 1439 s 仍未见其 `spawned with pid`，也未见退出行。不能据此确定一直停在 spawning。
- `tccd` pid：119 s 见 17，599 s 见 237、284，899 s 见 301；可见序列单调递增，仍无 `exited`。这里的 17 属第二次启动，不恢复第一次上机中已撤回的误读。
- 所审画面仍未读到任何 `exited` 行；`the target exits.` 是另一条消息，不是服务退出。
- 完整失败路径包括 `/AppleInternal/Library/LaunchDaemons`、`/AppleInternal/Library/LaunchAngels`：按出货卷不含 AppleInternal 路径的背景作为预期噪声处理；另有正常系统路径 `/System/Library/LaunchDaemons/com.apple.CommCenter.plist`，性质不同。

### 卷内核对（同轮离线）

- OS 卷 `out/userdata-clean-20261112/OS.raw` 按目录记录键判据，`com.apple.CommCenter.plist` 命中 3 处；同父 ID 下另有一整簇 `com.apple.C*` plist，包括 `CloudSettingsSyncAgent`、`CoreAuthentication.daemon`、`CommCenterRootHelper`、`ClipServices.clipserviced`。该父目录**强推断**为 `LaunchDaemons`，但文件树遍历未完成，oid 链未对到 `/System/Library/LaunchDaemons`。
- SystemOS 卷的 `LaunchDaemons`、`NanoLaunchDaemons` 均 0 命中，与 `/` 由 OS 卷提供、SystemOS 作 union 叠加一致。
- 该 plist 大概率存在于 OS 卷内（强推断）；`Failed to bootstrap path` 原因仍 UNKNOWN，可能涉及 plist 本身或其引用的可执行体。

### 判读边界

- **已确证**：两次启动探针的约 5.002 s 板内差值；legacy `start` 非 IOD 分支；持续出现新服务 spawn、可见 pid 4→21；SpringBoard 可见 `spawning`、至 1439 s 未见其 PID 或退出行；多个 `tccd` PID 可见，所审画面无退出行。
- **强推断**：launchd 处于持续推进而非 respawn 环；`com.apple.CommCenter.plist` 存在于 OS 卷。
- **UNKNOWN**：SpringBoard 是否停在 `spawning` 及其原因；`tccd` 多实例成因；`Failed to bootstrap path` 的失败原因；首个 GUI swap；相对真实时间的时基准确性。

阶段不提升。
