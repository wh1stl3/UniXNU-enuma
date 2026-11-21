# enuma r17 trust cache 覆盖调查

状态：self-checked；离线只读，无设备操作、构建或卷修改。

## 输入与格式

对 `out/ufs-sm8250-launchd-keystore-20261122-r17/payload.img` 用 `mtype` 读出 `::/EFI/UniXNU/Payloads/kernel.macho.trustcache`，长 61356 字节，SHA-256 `7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7`；与 r17 `candidate-manifest.json` 的输入及打包哈希相同。输入是 `out/production-os-trust-20261113/original-static-system.bundle`，由 2026-11-13 `prepare.py` 从 iPad7,1 iPadOS 17.7.11 21H461 Erase identity 制成，来源详见同目录 `provenance.json`：

| donor 组件 | bundle 偏移 | 模块 SHA-256 | 格式版本 | 记录数 |
| --- | ---: | --- | ---: | ---: |
| StaticTrustCache (`Firmware/044-76040-038.dmg.trustcache`) | 12 | `da88460e6e513438d5307e5c526f76497a74754476a24da29f239f0c90120fc2` | 2 | 2478 |
| Cryptex1,SystemTrustCache (`Firmware/044-76034-038.dmg.trustcache`) | 59508 | `d121ba89167e03aafd00fa687c30cd8ebc4ccafd10c1408adb2ba3de12403651` | 2 | 76 |

两个模块合计 2554 条记录，未按相同 hash 去重；每项 24 字节，前 20 字节为 cdhash，末四字节为属性。两个模块均含 cdhash 类型记录；第一属性字节分布为 type 2 共 2552 条、type 1 共 2 条。属性第三字节非零的记录共 2344 条（静态模块 2331、cryptex 模块 13）；这些字节的 constraint 语义未独立核定，不把它们当作已确认的独立 constraint 模块或规则。打包内容存在不证明运行时已被 AMFI 装载或接受。

## 覆盖与判断

任务给定的 SpringBoard、xpcproxy、backboardd、tccd、assistantd、runningboardd、mediaserverd、studentd、peopled、remoted、biomed、checkerboardd、threadradiod、CommCenter 均未从 OS/SystemOS 卷中取得其 Mach-O，也未计算 CDHash 或进行集合查找。`out/userdata-clean-20261112/` 中有 `OS.raw` 和两个 donor DMG，但仅有镜像不等于已读取到卷内文件；本次不修改或挂载卷。可在只读 APFS 解析环境读取实际对应卷中的文件，对每个架构的 Mach-O CodeDirectory 计算签名指定算法的 CDHash，并与两模块逐项比较；同时确认日志服务名和实际可执行路径的对应关系。不能用服务名或文件存在性代替签名核验。

因此判定 **无法判定（缺卷内可执行体 CDHash、实际运行时 trust cache 装载证据）**；没有发现未经覆盖的可执行体不等于证明全部覆盖。r17 `sig=9` 不是 AMFI 原因的直接证据；sirius 的缺 bundle 观察也不能直接迁移为本板归因。即使命中所选文件的 hash，也不能单凭命中排除所有 AMFI 策略或动态装载问题。

## 最终 payload ADT

从同一 payload 以 `mtype` 读回 `kernel.macho.adt`，14048 字节，SHA-256 `099dda97e8c01592cf9542b806b868ce098415ef9bab8ed7a01c8d03edd95059`。遍历全部节点，解析结束偏移等于文件长度：`/device-tree/defaults:vmm-present = 1`（`01000000`）、`kern.maxvnodes = 66560`（`00040100`）；整个树中没有 `sleep-disabled` 属性，不能将其写成 0。

固定 UniXNU 文档 `docs/zh/devices/evb10.md:52,240` 要求 `sleep-disabled=1`、`vmm-present=1`，并记载 `kern.maxvnodes=66560`；r17 前两项分别不一致、一致，maxvnodes 一致。`docs/zh/devices/sirius-dddqmmx.md:48,510` 记载 board 设置 `sleep-disabled=1`，与 r17 不一致；不据此推断 sirius 另两项值。

复核方法：`mtype -i <r17 payload.img> ::/EFI/UniXNU/Payloads/kernel.macho.{trustcache,adt}` 分别读取二进制；按 bundle 小端 count/offset、v2 模块 24 字节头与 24 字节记录统计，ADT 按节点头及 4 字节对齐属性递归遍历。所用临时只读脚本位于主机临时目录，非发布资产。
