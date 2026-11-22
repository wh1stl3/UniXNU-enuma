# AppleKeyStore 软件身份调查（2026-11-23）

状态：self-checked，纯源码和公开记录；没有构建或设备操作。基座 UniXNU `693f5d9cae8a408dd18b39f3f9fdc4228c934241`，其 AppleKeyStoreState gitlink `8c70daf814aafdf4a3d35e40dde0322655fd0a83`。enuma 工作基线 `c34aed27f57c3633fcac3feeb23a79d0f3be61d3`。本调查不改变既有 fail-closed 配置。

## 1. 契约与调用

`UniXNU/drivers/AppleKeyStoreState/NativeKeyStoreEvents.cpp:28`：`extern "C" size_t native_aks_device_id(uint8_t *out, size_t capacity);`。`:103-115`：

```cpp
uint8_t id[32];
size_t n = native_aks_device_id(id, sizeof id);
if (!n) return false;
static const char domain[] = "UniXNU AppleKeyStore v1";
hash.update(domain, sizeof domain - 1);
hash.update(id, n);
hash.final(cached);
```

调用方给 32 字节空间，板级应写入实际字节并返回 1–32，或返回 0 表示不可用；通用实现只检查返回长度非零，不检查其是否超过 capacity，不能返回超界长度。没有规定必须恰好 32 字节，也没有检查字节内容是否非零。身份必须跨启动一致（`:103`），派生为 32 字节 SHA-256 软件密钥。`:151-184,264-266` 的 externalMethod selector 10/11/23 经 `wrapKey`/`unwrapKey`/`bagUuid` 间接调用；有效参数下身份缺失返回 `0xe00002bc`，bag UUID 是另一次哈希前 16 字节。封装/解封还受参数、输出空间和旧 blob 验证约束；非零身份并不保证所有调用成功。状态 selector 不依赖该身份。

`package/EnumaKeyStoreProbe.cpp:30-32`：`extern "C" size_t native_aks_device_id(uint8_t *, size_t) { return 0; }`；`:65-75` 的 probe 自己也调用并打印长度，故 `aksid 0` 是该探针的直接结果，不证明用户态已调用 selector 10/11。用户提供的注册/匹配观察是上下文转述，非本轮复核。

## 2. 官方来源

`UniXNU/docs/zh/drivers/apple-key-store-state.md:11` 原文：“密钥封装由软件完成：设备密钥来自板级通过 `native_aks_device_id` 返回的标识，keychain 用它存取条目。这不是硬件数据保护。不支持引用密钥操作和设备锁定。”该页未规定板级从常量、ADT、SEP 或 ECID 取值。

`UniXNU/docs/zh/porting/packaging.md:56-58`：“把它的 secret `UNIXNU_UNIQUE_CHIP_ID` 设为设备的平台种子（8 位十六进制）。种子不在任何仓库中，镜像会把它编入，只对这台设备有效。”`:40` 还列出 `--unique-chip-id HEX`。`UniXNU/scripts/unixnu/devicetree.py:311-316` 将提供的非零种子作为小端 u64 `unique-chip-id`，另将配置 chip ID 作为小端 u32 `chip-id` 写入 chosen；这证明生成规则，不证明现有 enuma 运行时 ADT 的值、硬件来源或该 seed 是保密的。

## 3. 其他设备

* [UniXNU/UniXNU-sheng `c8f92b208068eeaa4cd2b0f592671f04ee70076e`, `package/KeyStoreProbe.cpp:67-79`](https://github.com/UniXNU/UniXNU-sheng/blob/c8f92b208068eeaa4cd2b0f592671f04ee70076e/package/KeyStoreProbe.cpp#L67-L79)：取 `/chosen/unique-chip-id` 的原始 OSData，长度至少 8、不超过 capacity 且至少一字节非零；否则返回 0。其值由 payload 平台种子提供，不是这里读取 SEP。
* [Ken-u/UniXNU-orangepi5 `729ba25f4d67225ff3853ba1e435b95af97e59e3`, `package/KeyStoreProbe.cpp:147-181`](https://github.com/Ken-u/UniXNU-orangepi5/blob/729ba25f4d67225ff3853ba1e435b95af97e59e3/package/KeyStoreProbe.cpp#L147-L181)：顺序拼接可用的 `/chosen/unique-chip-id` 和 `chip-id`，缓存并返回，均不存在则 0；代码允许只有其中一个。注释指明 payload 生成的 u64/u32，通常合计 12 字节。
* [rootstockos/UniXNU-asteroids `6370e66cc460202756058ae53f73afdb69abd364`, `package/KeyStoreProbe.cpp:29-35,96-99`](https://github.com/rootstockos/UniXNU-asteroids/blob/6370e66cc460202756058ae53f73afdb69abd364/package/KeyStoreProbe.cpp#L96-L99)：此文件注册 stand-in 并记载 T28/T29，但未定义此回调；尚未定位该 revision 的其他定义，不能声称其身份来源。`UniXNU/docs/zh/devices/asteroids.md:695,715-716` 记录 T20–T28 无 stand-in 未完成启动、T29 有 stand-in 出首图；不是单独改变身份长度的对照。
* [57UU/UniXNU-sirius `f269452c36eceb7f91446fccc4c3bed175aaa98e`](https://github.com/57UU/UniXNU-sirius/tree/f269452c36eceb7f91446fccc4c3bed175aaa98e)：`UniXNU/docs/zh/devices/sirius.md:3,9` 标识仓库和版本；本轮未定位回调实现，值及来源未知，不据此断定不存在。

## 4. enuma 来源可行性

| 来源 | 判断 | 原因 |
|---|---|---|
| donor APFS UUID | 需额外输入 | 可当稳定字节串，但要证明运行时早期取得及跨启动一致；公开镜像可共享，非设备唯一或秘密，换卷会改变密钥。不能解开原 Apple SEP 保护的内容。 |
| donor `/var/db` 密钥材料 | 不可行（现有证据） | 未发现可用于本回调且可在此调用时安全取得的材料；不能假设可迁移原 SEP 密钥。 |
| ADT `unique-chip-id` | 需额外输入 | 官方生成器能从配置种子注入；当前 enuma 实际 payload 是否有、稳定性及值的来源未核。不能从 `chip-id`/`board-id` 推导逐设备唯一性，也不能假设 Android 板有 Apple ECID。不得把设备标识写入仓库。 |
| 所有设备相同的固定字节 | 可行（仅诊断算法） | 任意固定的 1–32 字节（包括内容全零，长度非零）可越过本组件身份缺失分支；相同身份产生相同软件密钥，可被镜像使用者推导，不提供设备绑定/保密。后续改身份会使旧 blob 校验失败；不是安全存储或用户态端到端通过的证明。 |
| 固件生成并持久化随机身份 | 需额外输入 | 需要真实可用、授权的持久存储、早期读取及跨启动稳定性；丢失/改变身份会丢失旧封装数据访问，且仅软件保存不是硬件保护。本轮没有固件或存储操作。 |

## 5. 卡点判断

身份缺失是该 stand-in 的 wrap/unwrap/bag UUID 的确定性前置缺失（源码强证据）；它**可能**影响 SpringBoard/backboardd（跨设备先例及 keychain 机制，弱至中等证据）。缺 enuma 用户态相关 selector 的实际调用、返回与等待链，不能断言这是当前 GUI 卡点，更不能断言补身份即可出图。最小诊断输入是一段跨启动稳定的固定非空字节串；只足以排除 `deviceKey()` 的零长度分支，其他参数、已有 blob、服务和显示链仍未验证。
