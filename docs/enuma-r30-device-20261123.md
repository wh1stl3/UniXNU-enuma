# enuma r30 user-client 对照实机观察（2026-11-22）

`self-checked`：用户单张实机照片、主控目视转录；无录像、无 `vision` 核读。本次仅记录转述，未重新访问设备或核读；阶段不提升。

## 操作与审查

- 2026-11-22 18:33:38 +08:00 刷入 `boot_b`：`Sending 'boot_b' OKAY [4.079s]` / `Writing 'boot_b' OKAY [0.326s]`，exit 0；随后 `reboot` exit 0。claim `.cache/enuma-r30-control-20261123.claimed` 已消耗，禁止访问、删除、重放。
- 镜像 `out/ufs-sm8250-launchd-control-20261123-r30/boot.img`，169,951,232 B，SHA-256 `ac7ca17e9af1b133633d4c17ccea9e50b9713fadaf9d971adad4788140c63675`。
- 主控提供刷写前 `deep_reviewer` **PASS WITH CONDITIONS**：comm 表是截断键不是身份；已知名字计数 >0 要与同轮 `enuma-fb: open[i]` 交叉核对；`bb=0` 是累计采样，不是最近 30 秒。这是 deep 审查，非「方案 B、未经 deep_reviewer」；本次未独立复核。

## 同屏结果

```text
enuma-fb: start=1 comm=-
enuma-fb: open=2 comm=MobileGestaltHel
enuma-fb: refresh=0 kick=0 scanout=0 swap=0
enuma-fb: open[0]=IOMFB_FDR_Loader pid=57 type=0 ret=0
enuma-fb: open[1]=MobileGestaltHel pid=66 type=0 ret=0
enuma-fb: open[2..7]=-
enuma-fb: end

enuma-bb: begin calls=0 overflow=0
enuma-bb: end

enuma-ctl: begin all=70 bb=0 overflow=55
enuma-ctl: [com] keybagd=1
enuma-ctl: [com] logd=1
enuma-ctl: [com] containermanager=2
enuma-ctl: [com] powerd=6
enuma-ctl: [com] PerfPowerService=1
enuma-ctl: [com] audiomxd=2
enuma-ctl: [com] IOMFB_FDR_Loader=1
enuma-ctl: [com] MobileGestaltHel=1
enuma-ctl: end
```

## 判读边界

- **阳性对照**：`all=70` 显示有调用到达该分派点；两条已知截断 comm 键与同轮 framebuffer `open` 表项一致，支持该钩子在本次记录中捕获到相关调用。同名不等于独立身份认证，`ret=0` 为 framebuffer override 返回码。
- **已观察**：`bb=0`、表内无 `backboardd`；在该累计采样窗口，没有 comm 精确匹配 `backboardd` 的调用到达该插桩分派点。`all=70` 反映其他调用同期到达；不覆盖窗口之后、其他路径或不匹配的进程名。
- `overflow=55` 是未能入槽的**调用次数**，不能解释为 55 个不同 comm；独立 `bb` 计数不依赖 comm 表是否满。各字段非事务快照；见 [r30 主机记录](enuma-r30-control-host-20261123.md)。
- framebuffer `refresh/kick/scanout/swap` 均为 0：这些板级探针未记录对应入口或调用，不证明没有其他显示路径使用，也不能区分请求未提交与到达前被拒。
- **待证解释**：backboardd 可能在用户态等待 Mach/XPC 或 dyld 初始化，具体状态未观测；仅凭 `bb=0` 不能证明进程此时存在、卡住或尚未进入任何 IOKit 使用阶段。

阶段不提升。
