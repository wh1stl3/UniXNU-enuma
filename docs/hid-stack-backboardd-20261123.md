# HID 与 backboardd 离线调查（2026-11-23）

`self-checked`；只读分析，无设备操作、构建或卷修改。不能由已观察的 open=0 推断首个调用必然是 HID，也不能证明线程阻塞于 HID。

## enuma：列表、产物和节点

1. **21 项不是 kext**：`package/BootWatchdogPolicy.c:20-24` 是 `sheng-lite` 禁用的 launchd job：`com.apple.` 前缀下 identityservicesd、locationd、CommCenter、bluetoothd、photoanalysisd、mediaanalysisd、mediastream.mstreamd、icloud.searchpartyd、findmy.findmybeaconingd、familycircled、financed、softwareupdateservicesd、ndoagent、biomesyncd、email.maild、amsengagementd、adid、eyereliefd、fairplayd.A2、passd、mobile.obliteration。见 `docs/enuma-r19-watchdog-lite-host-20261122.md:14-32`。它不是内核加载列表，不应同 kext 集合比较。
2. r40 实际组件列表为 `out/ufs-sm8250-storegeom-20261123-r40/prelink.json:5-39`：30 个有代码组件加一个 codeless `com.apple.iokit.IOHIDEventDriver`；`IOHIDFamily` 在 components 第 24 行。r23 明确根为 `scripts/build-enuma-r23-hid-standin.py:28` 两项 family 与 event driver。无独立 IOHIDSystem 或 AppleHIDTransport bundle 列项。
3. 字节计数（非符号定义数量），在设备仓执行：
   ```sh
   python3 -c 'b=open("out/ufs-sm8250-storegeom-20261123-r40/prelink.macho","rb").read(); [print(s.decode(),b.count(s)) for s in (b"IOHIDFamily",b"IOHIDSystem",b"IOHIDEventSystem",b"AppleHIDTransport")]'
   # IOHIDFamily 28
   # IOHIDSystem 1
   # IOHIDEventSystem 0
   # AppleHIDTransport 3
   ```
   `IOHIDSystem` 唯一命中 `0x5816eac` 是 `IOHIDSystem posted stackshot event 0x%08x` 日志字符串，不是独立实体证据；AppleHIDTransport 命中为字符串。Family 有 prelink 组件元数据和 executable，不只是名称引用；event driver 是 codeless。未完成 personality 全量解析或导出符号扫描。
4. 对 `kernel.macho.adt` 按 Apple ADT 递归解析，搜索节点名和属性名 `hid|digitizer|spi|input`：无命中；解析消费长度为 14128/14128 字节。该检查不是对属性值搜索。r23 的 digitizer **不是 ADT 节点**：`package/EnumaHidStandin.cpp:48-68` 在匹配出的 EventDriver 和 interface 设置 Built-In、DisplayIntegrated、PrimaryUsagePage=0x0d 和 PrimaryUsage=4；`:105-120` 加载 family/event driver 并等待 `IOHIDResource`，以软件 device attach/start。r40 的 `device/board.toml:72` 仍带 `sheng-touch-hid=1`，prelink 中仍有 stand-in 日志字符串；这不独立证明 r40 运行时执行成功。r23 实测 `digitizer properties=1` 见 `docs/enuma-r23-hid-device-20261122.md:15`，不证明物理触摸或用户态消费。
5. **HID 首个依赖能否满足：无法判定**。family 与软件 digitizer 路径存在，不支持直接断言缺该 kext；缺 backboardd 首个实际依赖、目标服务发布/可见性和等待点的证据。family 的完整 personalities/provider 列表尚未提取，不能断言必须另加哪种 ADT 节点。

## backboardd 离线取得

`find out .cache/firmware -type f \\( -iname '*.ipsw' -o -iname '*.dmg' \\)` 找到 `out/userdata-clean-20261112/044-76034-038.dmg` 3303014400 B（SystemOS）及 `044-76040-038.dmg` 5157406069 B（OS）；另有同目录 `OS.raw` 6077580800 B。该搜索未命中 IPSW。OS DMG 为压缩 UDIF，见 `docs/data-seed-macos-vm-procedure.md:19`；已有 raw 避免重复解压。先前“没读取器”只是当时环境状态，不是不可行证明。

最直接路线是 WSL 的 `apfs-fuse` 只读访问现有 raw，需支持对应 APFS 格式及 FUSE、权限和目标卷/快照；可能还需处理文件压缩和 cryptex。nuwa 已记录同工具读取 20H392 的 OS raw 并见到 backboardd：`D:/Code/PortingiOS/nuwa/UniXNU-nuwa/docs/nuwa-display-abi-20261120.md:427-435`，但这是不同供体，不证明 enuma 镜像可读。本轮未实际挂载或提取，工作量主要在准备工具、只读访问及核验文件和完整 extent；成本未知。`libfsapfs` 或新版 7-Zip 是备选，尚未核实本机版本及其对该镜像的具体兼容性。

## 计数钩子

`out/ufs-sm8250-launchd-attempt-20261123-r32-intermediate/source/iokit/Kernel/IOUserClient.cpp:4366,4376` 在 `is_io_service_open_extended` 入口调用 `enuma_att_record(0)`；拒绝分支见 `:4386-4403`。这个位置只能观察 open，不能直接观察匹配请求或所有 Mach 消息。

匹配计数须另在同文件 `is_io_service_get_matching_services*`（`:2735,2745,2773`）及 `is_io_service_add_notification*`（`:2964-3137`）各入口或已确认的公共实现插入 pid 分类计数；须覆盖不同 MIG 变体并避免重复计数。Mach 消息目的端口类别须在 Mach IPC 发送路径另作端口对象和命名空间分析，不可从 open 入口推导；全局高频计数、端口生命周期、锁及并发增加风险，属于需 deep_reviewer 的范围。本轮未实现。

## nuwa / sheng 对照

nuwa 主工作树 `D:/Code/PortingiOS/nuwa/UniXNU-nuwa/board.toml:49-78` 的 iOS 20H392 roots 共 28 项，全部逐行列在该位置；包含 IOHIDFamily、IOHIDEventDriver（`:76-77`），不含独立 IOHIDSystem 或 AppleHIDTransport。`git worktree list` 有多个历史 worktree；本次未逐一检查，不声称覆盖所有版本。

与 enuma r40 **最终 closure** `prelink.json:5-39` 做集合比较（注意不是同层：nuwa 为 roots，enuma 为包含传递依赖的输出）：

- nuwa 有、enuma 无：`com.apple.kec.pthread`（nuwa board `:71`）。
- enuma 有、nuwa 无：`com.apple.filesystems.apfs`、`com.apple.iokit.IOAVFamily`、`com.apple.iokit.IOMobileGraphicsFamily`、`com.apple.kec.Libm`（enuma prelink `:16,18,25,30`）。

nuwa board 属性名未发现 HID/digitizer/input/spi 匹配；未解析其最终 ADT，因此不能断言最终节点不存在。未找到 nuwa IOHIDSystem 发布或 backboardd 打开 IOKit 的实测记录，不能以未找到证明未发生。

sheng 本地参考 `UniXNU-sheng@c8f92b20:board.toml:213-216` 的 iPadOS 27 override roots 包含 IOHIDFamily、IOHIDEventDriver，也包含 USB HID 项；不同系统版本不能直接比较其余驱动。三者均包含前两项，enuma 不缺这两项；USB HID、运行时发布及具体客户端依赖并不因此一致。
