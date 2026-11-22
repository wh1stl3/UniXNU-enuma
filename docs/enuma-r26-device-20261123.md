# enuma r26 framebuffer 计数实机观察（2026-11-22）

`self-checked`：用户单张实机照片，主控目视转录；无录像、无 `vision` 核读。本次仅记录转述，未重新上机或核读；阶段不提升。

## 操作和审查

- 2026-11-22 17:08:28 +08:00 刷入 `boot_b`：`Sending 'boot_b' OKAY [4.066s]` / `Writing 'boot_b' OKAY [0.378s]`，exit 0；随后 `reboot` exit 0。claim `.cache/enuma-r26-fbcount-20261123.claimed` 已消耗，禁止访问、删除、重放。
- 镜像 `out/ufs-sm8250-launchd-fbcount-20261122-r26/boot.img`，169,951,232 B，SHA-256 `a60d634bb92e9be03af29df71d09634a543f924c9b27281a299d33a2b139bd92`。
- 主控提供的审查留痕：`deep_reviewer` 曾因归档的失败构建判 FAIL；正式候选随后经机械复核：链接日志无错误、`__GLOBAL__sub_I_NativeLegacyDisplay.cpp` 在 native/prelink 均定义为 `S`、零 undefined 含 weak、`boot.img` 大小和哈希吻合、文档三处判读限定齐备。本次刷写前最终审查**仅为机械核对，未经 `deep_reviewer` 对正式候选重新判定**（方案 B，未经正式候选 deep 重审）；本记录未独立复核上述检查。

## 屏上结果

屏上三组、间隔约 30 秒，主控转录读数完全一致：

```text
enuma-fb: begin
enuma-fb: start=1 userclient=2 swap=0 last_comm=IOMFB_FDR_Loader
enuma-fb: end
```

另见 `corecaptured[120]` 以 `st=0` 退出及 `process exited in a dirty state`；与显示主线的关系未见证据。

## 判读边界

依 [r26 主机记录](enuma-r26-fbcount-host-20261122.md) 的计数点定义：

- **已观察（该次启动、三次快照）**：板级 `startDisplay` 入口调用计数为 1，板级 `newUserClient` 打开尝试计数为 2；至快照时无呈现请求到达板级 `validateSwap`（`swap=0`）。`start` 计调用而非成功，`userclient` 包括被拒绝的请求。
- **待证解释**：路径已收到打开尝试但未见呈现到达板级校验，与显示链路停在打开之后、SpringBoard 拿不到可用渲染目标的假设相容；打开结果和 SpringBoard 因果未测，不能断定。
- **UNKNOWN**：两次 `userclient` 的调用者及打开是否成功；打开后是否卡在显示模式设置、首帧提交或其他位置。`last_comm` 为三探针共用的末次上下文，计数与名字不是事务快照，不能将 `IOMFB_FDR_Loader` 归属给两次打开。

阶段不提升。
