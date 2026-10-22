# Enuma platform support core

可编译的板级支持代码，尚未接到 IOKit service 或固件，未在设备执行。

- `EnumaGeniSpi` 直接调用固定 UniXNU `NativeGeniSpi/GeniSpi.c`。不复制、不替代其传输实现。enuma 历史 FDT：SE4=0x990000、wrapper=0x9c0000、CS0、mode0、上限19.2MHz。只开放 FIFO/PIO；FIFO 被固件禁用时返回 NOTSUP，不偷偷切 DMA 或改 SMMU。caller 负责时钟/pinmux/供电和独占状态；本模块不具备这些硬件初始化能力。协议身份、忙碌状态、无效参数在写寄存器前拒绝；超时后撤销 ready。
- `EnumaUfsClock` 使用 Kona 的九项时钟寄存器，提供完整快照或失败；没有写接口。尚未推断时钟值意味着 HC 可安全访问，也没有启动 PHY、SMMU 或存储链路。
- sheng 的触控为 NT36532E/THP；enuma 候选为 NT36523 普通触点包。不能复用 sheng 的触控解码/下载固件，仅复用通用 GENI SPI 层。

编译与测试入口：`scripts/check_enuma_drivers.py`（WSL）。来源事实、SHA256 与许可证见本目录 `sources.json` 和 `LICENSE`。常量来源需按源码结构提取核对，不能仅因测试断言相等就称硬件验证。
