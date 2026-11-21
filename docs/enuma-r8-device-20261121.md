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
