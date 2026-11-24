# pipa HID 参数与 enuma 对照

状态：self-checked，离线静态核查；未构建、未访问设备、未独立验证运行时。
参考 pipa `xVanTuring/UniXNU-pipa@cdb3d62771e31d48d832853ee0c90964346d78da`
（本地 `.cache/ref-pipa`）；enuma 比较对象是
`out/ufs-sm8250-smpobs-20261124-r62/prelink.macho`，不是所有历史或未来内核。

## 消费者和行为

对 r62 124760064 字节 prelink 二进制直接做字节串计数：
`offline-hid-input`、`offline-hid-home`、`offline-key-events` 均为 0，
`sheng-touch-hid` 为 1。结合本板 publisher 和 keystore 源码，当前 r62
没有这三个参数的可见消费者；单纯添加它们无效。字节串检查不能排除
不以完整明文保存参数名的未知消费者；未逐个追溯所有链接输入。

* pipa `package/HidInputProbe.cpp:145-153`：
  `if(!PE_parse_boot_argn("offline-hid-input",&enabled,sizeof(enabled)) || enabled!=1)return;`
  之后加载 IOHIDFamily 和 IOHIDEventDriver。`:163-178` 等待 IOHIDResource。
  这是 pipa probe 总门控；enuma 对应功能由
  `package/EnumaHidStandin.cpp:105-120` 的 `sheng-touch-hid=1` 开启，
  加载同两组件，Data 后、launchd exec 前尝试发布。
* pipa `package/HidInputProbe.cpp:166-178`：
  `PE_parse_boot_argn("offline-hid-home",&sendHome,sizeof(sendHome));`
  `if(resource && sendHome==1 && native_hid_class_sizes[4]==208)` 才
  分配、初始化、attach/start `native_hid_input_allocate()` 组合设备。
  名字不是直接证明独立 home 按钮已发布或能发真实按键：设备的按钮报告
  需要其具体描述符、事件来源和实际运行进一步证明。`:184-191` 的独立
  digitizer 另需 `sheng-touch-split=1`，不是默认必然创建。
  enuma `EnumaHidStandin.cpp:72-103` 同样尝试创建组合设备，但无需该门控。
* pipa `package/KeyStoreProbe.cpp:76-107,125-126`：
  `if (!PE_parse_boot_argn("offline-key-events", &enabled, sizeof(enabled)) || enabled != 1 || native_keyevents_stage) return;`
  随后要求 `/chosen` 的 `ephemeral-storage=1` 且 `offline-keystore` 未开启，
  注册并启动 `AppleKeyStore` 软件服务；它是 keystore state/event 服务
  的门控，不是 HID 物理按键开关。`offline-keystore=1` 为另一个原厂
  AppleSEPKeyStore 加载路径（`:125-133`）。
  enuma `package/EnumaKeyStoreProbe.cpp:18-23,54-71` 用
  `sheng-aks=1` 且 `offline-keystore!=1` 门控软件 AppleKeyStore，
  没有 pipa 的 ephemeral-storage 条件；因此作用相近但门控不等效，
  不能把两种实现认作完全等同或推定服务已成功启动。

## enuma HID 覆盖

`package/EnumaHidStandin.cpp:18-24` 的触点变量为零、touch/button sink
为空；`:48-68` 为匹配的 event driver 及 interface 设置 digitizer 属性。
上游 `out/r23-upstream/ShengHidInput/NativeHidInput.cpp:395-415` 在
`sheng-touch-hid=1` 时将触摸 collection 加入 keyboard/consumer 组合
描述符。r23 曾记录 `digitizer properties=1`
（`docs/enuma-r23-hid-device-20261122.md`），仅证明该轮匹配与属性设置，
不证明 r62 的实际运行、真实触摸、Home 按键或用户态消费。
这覆盖 pipa input/home 门控所触发的组合设备发布的主要软件路径，
不覆盖真实触摸和按键事件；不证明 pipa 的设备和属性逐项相同。
`sheng-aks=1` 已提供功能相近的独立 keystore 路径，但不是 HID key events。

## FDR loader 与判断

pipa `board.toml:193-198` 以 boot-arg `sheng-disable-jobs=...` 列出
`com.apple.iomfb_fdr_loader`，其 `package/BootWatchdogPolicy.c:43-49,60-75,81-83,103-111`
写 launchd `disabled.plist`。enuma 不支持该通用参数；若另行授权修改，
位置是 `package/BootWatchdogPolicy.c:19-24` 的 `lite_jobs`，
由 `:56-71` 的 `sheng-lite=1` 路径应用，`:76-89` 写入 Data 上的
`/private/var/db/com.apple.xpc.launchd/disabled.plist`。本次不改。
现有 plist、挂载、写入与 launchd 消费是否成功需验证；loader 涉及 FDR
校准和显示电源请求，停用不能假定无影响，见
`docs/missing-bootargs-and-fdrloader-20261123.md:13-24`。

对 backboardd 打开 IOKit 或 SpringBoard 推进：pipa 软件 HID 和 keystore
服务作为用户态依赖有间接影响的可能，强度低、无本板单变量因果证据；
pipa 的启动配置包含许多同时变化项。对 r62 直接追加这三个参数的影响
预计为零，不值得作为下一个纯配置候选。功能本身与参数名不同，若实际
服务未发布应先查同轮日志及链接，而不是以加无消费者的参数代替。
