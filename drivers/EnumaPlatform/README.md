# Enuma platform support core

可编译的板级支持代码，尚未接到 IOKit service 或固件，未在设备执行。

- `EnumaGeniSpi` 直接调用固定 UniXNU `NativeGeniSpi/GeniSpi.c`。不复制、不替代其传输实现。enuma 历史 FDT：SE4=0x990000、wrapper=0x9c0000、CS0、mode0、上限19.2MHz。只开放 FIFO/PIO；FIFO 被固件禁用时返回 NOTSUP，不偷偷切 DMA 或改 SMMU。caller 负责时钟/pinmux/供电和独占状态；本模块不具备这些硬件初始化能力。协议身份、忙碌状态、无效参数在写寄存器前拒绝；超时后撤销 ready。
- `EnumaUfsClock` 使用 Kona 的九项时钟寄存器，提供完整快照或失败；没有写接口。尚未推断时钟值意味着 HC 可安全访问，也没有启动 PHY、SMMU 或存储链路。
- `EnumaNvt` 按固定 MiCode NT36523 包格式实现有界解码：67/81 字节 SPI 响应去 dummy，66/80 字节规范包的触控前缀校验、十点 ID/坐标/压力、ESD/WDT 分类、闭区间坐标归一化。错误不交付部分帧；不包含 SPI 发起、FWINFO 读取、固件上传、恢复、手写笔解析或 HID 发布。测试仅从固定厂商文件提取原 checksum 函数到 out/ 作主机对照，不链接 Linux 代码。
- sheng 的触控为 NT36532E/THP；enuma 候选为 NT36523 普通触点包。不能复用 sheng 的触控解码/下载固件，仅复用通用 GENI SPI 层。
- 固定 `NativeHidInput.cpp` 的坐标映射仍写死 sheng 的 30480×20320，不能直接喂本板坐标；后续需单独接 enuma digitizer 与 ID 消失/抬手事件。实际 FWINFO 最大值、轴向及笔输入仍待设备证据。

编译与测试入口：`scripts/check_enuma_drivers.py`（WSL）。来源事实、SHA256 与许可证见本目录 `sources.json` 和 `LICENSE`。常量来源需按源码结构提取核对，不能仅因测试断言相等就称硬件验证。

2026-10-27新增：EnumaUfsSmmu按固定umi双stream接管算法实现显式输入、完整路由重查、失败停止及单次状态；本机FDT未声明UFS iommus，测试中的0xe0/0x4e0仅是umi夹具，不能当enuma硬件值。EnumaUfsRead解析实际READ CAPACITY(10)并生成受LUN/根窗口/DMA缓冲约束的READ(10)，不借用umi容量，不含磁盘写接口。两模块尚未接入IOKit或真实MMIO；调用方还必须实现队列静止和独占、实际DMA分配及时钟/供电路径。验证入口scripts/check_enuma_storage.py。
