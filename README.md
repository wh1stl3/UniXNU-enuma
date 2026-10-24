# UniXNU-enuma

小米平板5 Pro 5G / SM8250-AC的iPadOS17.7.11移植。尚未验收可见GOP、XNU入口或用户态。

当前D-166：已完成本机ABL/原厂DisplayDxe/保存DTB的[交接契约](docs/operations/2026-10-25-handoff-contract.md)与[ABI审计](docs/operations/2026-10-25-native-display-abi.md)，A/detail15正确GUID候选离线构建和资格通过，未上机。接手读[AGENTS](AGENTS.md)、[STATUS](docs/STATUS.md)、[HANDOFF](docs/HANDOFF.md)、[交接词](docs/2026-10-25-handoff-prompt.md)及[审核状态](docs/NEED-REVIEW.md)。

路线维持先审显示交接契约、原厂DisplayDxe有界验证、最小真实初始化为条件后备；不补未知协议stub，不复制其他机型参数。工具与机器报告记录实际输入摘要、编译宏和Core代码。固件固定aa9ec66，源码实现仅在firmware子模块，参考仓只读，所有二进制在out/。

下一次实机仍需文档提交推送、即时身份/匹配备份/恢复和观测门禁。没有从此次离线审计新增像素、内存、verified或分区批准。

远端：[设备仓](https://github.com/wh1stl3/UniXNU-enuma)、[固件仓](https://github.com/wh1stl3/uefi-enuma)。
