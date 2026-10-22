# 固件来源与许可

底座固定为 UniXNU/uefi-sheng `329b473df1e53a3bfa64b2b39b79670c4c02279b`，源于 Mu-Silicium。上游根 `LICENSE` 为 BSD-2-Clause；本目录所衍生 DSC/FDF/PlatformSec 文件明确标注 BSD-2-Clause-Patent，保留各文件原有版权与 SPDX 标头，许可证全文在本目录 LICENSE。APRIORI/DXE 的包引用不包含所引用模块的源码或二进制，其许可仍由各组件决定。

来源文件和摘要固定于 `config/porting-sources.lock.json`；只下载选定文件到忽略目录 out/references。引用 UniXNU/UniXNUPkg、DarwinBootPkg 的实现，不复制其源码。未分发厂商 Device-Binaries，不能由开源包的许可推断厂商二进制的再分发权限。
