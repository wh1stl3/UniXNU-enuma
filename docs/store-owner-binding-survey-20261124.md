# 持久 Data store 的 owner placement 绑定调查

状态：self-checked，纯源码/文档调查，未构建、未访问设备；结论限以下固定版本及所查路径，不能证明其他分支不存在实现。这里的「有保障」特指 owner 签名覆盖写窗口位置且运行时开写前验证，不表示数据完整性、反回滚或硬件所有权已解决。

## 1. 官方定义

官方基座 `UniXNU@693f5d9cae8a408dd18b39f3f9fdc4228c934241`：

* `docs/zh/concepts/userdata.md:68` 原文：「持久 store 从 userdata 分区末尾的窗口提供磁盘。写入使用 forced unit access，命令完成时页已写入介质。store 与根镜像和日志保留区保持距离。`sheng-log-reserve=<MiB>` 设置该保留区，默认 1024 MiB。`sheng-data-persist=1` 只验证窗口，`sheng-data-persist=2` 打开写窗口。」`:70` 原文：「store 窗口不适合真实分区时，内核拒绝该种子。」
* `docs/zh/concepts/security.md:57` 原文：「`kits/VerifiedRoot` 提供签名的策略包。verified block 驱动按策略校验每次读取。策略可以按容量用 `--verified-root-bundle` 选择。」
* `patches/xnu/offline-owner-root-binding-audit.patch:11-19` 对只读根设备调用 `native_verified_block_root_authorized(device)`；这是根设备授权，并非持久 Data 写窗口位置授权。
* 具体签名字段可由本板兼容官方格式的 `scripts/enuma-owner-policy.py:45-51,76-100` 核实：输入 `offset` 用于读取源镜像，签名 header 直接包含 size、块数、UUID、内容和散列表 hash、anchor hash、generation；**offset 不在 header**，更没有 store LBA。它证明此格式下本板签署的内容而不是任何后续 store 声明。

以上官方文字定义根镜像签名/逐块验证及 store 几何门控，未找到 owner 签名 store placement 格式或运行时验证规范；不能把本板额外安全门槛冒充官方已有要求。官方文档的 FUA 描述亦非位置授权。

## 2. 设备仓逐项比较

* **sheng**：设备 `UniXNU/UniXNU-sheng@c8f92b208068eeaa4cd2b0f592671f04ee70076e` 使用 `UniXNU/ShengUfs@9d527ae1a8d36a7ff210f9f4c9b429549c34c991`；`NativeUfs.cpp:2949-2966` 根据 root layout/manifest 设置几何，`:1515-1553` 检查 mode、host、大小、root 末尾 guard 后 mode 2 调 `hostStoreOpen`；`RootCommands.h` 再限制边界和 log 重叠。设备 `board.toml:184-185` 为 iPadOS 17 配置 mode 2。未见 store 起止签名验证；**仅几何**。详见 `docs/nuwa-persistent-store-20261123.md:14-22`，其中实测 macOS 不能冒充 iPadOS 17 跨重启验证。
* **pipa**：`xVanTuring/UniXNU-pipa@cdb3d62771e31d48d832853ee0c90964346d78da` 的 `board.toml:49-50,192` 选择 PipaUfs 和 mode 2；`.gitmodules:2-3` 指向 `xVanTuring/PipaUfs@5c64c0125e0d1855729a2d0095c03514b9cc7030`。其 `NativeUfs.cpp:1321-1332,1360-1387,2478` 设置 root 几何，检查 mode、大小及 root guard 后打开窗口；未见 placement 签名验证；**仅几何**。
* **sirius**：`HuajiFruit/UniXNU-sirius@ac0c900485f3c0cd18de9707579a1cdcd3365503` 的 `package/NativeEmmc.cpp:1061-1104` 需要 `sirius-data-write=1`、root image 大小、NXSB、块大小/数量及 userdata/设备边界，再设置写窗口；`:1322-1339,1441-1442` 的 `sirius-allow-unverified=1` 是显式无验证路径，不是签名。未见位置签名验证；**仅几何**。
* **orangepi5**：`Ken-u/UniXNU-orangepi5@729ba25f4d67225ff3853ba1e435b95af97e59e3` 的 `package/Rk3588Nvme/NativeNvme.cpp:1784` 条件为 mode 4 和 `nvme-data-persist`；`:1195-1240,1245-1267` 检查 rootReady、DMA、APFS seed 格式、容量、尾窗和 root 64 MiB 间距，再启写；seed CRC 非签名，且不同时强制 seed CRC 一致。未见位置签名验证；**仅几何**。
* **nuwa**：`nuwa/UniXNU-nuwa/package/nuwa-ramblock/NativeRamBlock.cpp:85-105` 检查 mode/provider 并调用 GPT check 和 open；`nuwa/UniXNU-nuwa/porting.toml:85` 区分双 root policy 与拒绝所有 store/log 写窗口。`docs/nuwa-persistent-store-20261123.md:7-11` 记录主控转述的某次最终链接 open 无条件拒绝，原始反汇编未随文档提供。未发现位置签名；**拒绝开启，不是无门控或有保障的可用 store**，不能外推所有构建。

## 3. enuma

`porting.toml:159,161` 记录主控提供的独立验证：真实 OS/SystemOS policy、anchor、块验证和隔离最终链接；不是默认生产集成或设备持久 store 验收。`scripts/enuma-owner-policy.py:94-101` 显示签名 header 不含输入 offset，更不含 store 起止；因此缺的不是「完全无签名」，而是**已有 root 签名不授权 store 窗口**。

`docs/persistent-data-plan-20261124.md:7-9,14-16` 引用 r40 审计源：root window 验证后 `storeBound` 仍 false；owner placement 签名与核对仅是提案。默认 `package/EnumaRamBlockStore.cpp:5-13` 是拒绝的 RAM-only provider；最终候选六符号归属需另核。mode 1/2 未放行，已有根挂载不等于持久 Data 通过。

## 4. 最小定义（方案，不是现有 API）

由设备 owner 的既有私钥签署版本化、域隔离声明，以受信 anchor 验签，至少覆盖：

1. 设备/安装身份与 LUN、分区唯一身份和分区边界；
2. root manifest / owner policy 身份及 imageBytes；
3. 块大小、store 起始 LBA 和长度，以及 reserve；
4. seed 内容身份、逻辑大小及 Data UUID。

在 root 和 GPT 的同一可信快照建立后、任何 store 发布/初始化/`hostStoreOpen` 或写入之前验签并逐项比较实际介质和计算窗口，检查容量、溢出、root guard 与其他区域不重叠；不符、过期或无法保证快照与写入生命周期一致则拒绝。保留每次写边界/epoch 检查。防重放、可信启动链、密钥轮换、DMA/并发和设备身份可信性仍需具体设计及 deep_reviewer；placement 签名本身不认证可变 Data 内容。
