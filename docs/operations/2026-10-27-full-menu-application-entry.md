# D-315：完整UniXNU应用入口离线接通

S053独立画面判读已由用户“对的”确认，增量报告reports/enuma-menu-window-S-053-confirmed.json；旧独立判读/待核对报告原字节保留。R025已消费，Android完成/root/A槽/解锁及原分区摘要独立通过，本轮无设备动作或新的实机批准。

## 实现与验证

新增firmware/diagnostics/EnumaMenuApplication.h：实际LoadImage/StartImage，通过子镜像LoadedImage.SystemTable传递私有GOP控制台表并重算CRC。仅改变调用者gST不会跨独立EFI镜像；固定DXE Core Image.c的CoreStartImage使用Image->Info.SystemTable，QEMU实际子应用验证该路径成立。子表ConOut/ConIn为空，ConsoleOutHandle指向已发布GOP，不改全局控制台。应用返回后确认卸载，卸载失败保持Active及存储所有权，拒绝复入；LoadImage安全失败但返回句柄也清理，拒绝非EfiLoaderCode镜像。此helper目前未启用到板级profile。

新增config/menu-entry-validation.toml，只有真实exit动作，无驱动/切片/ACPI/内核条目。scale1使800×600下完整底部提示可见，已查看生成PNG。它是新离线配置，不更改S053被冻结的scale2镜像。

新增tests/uefi_application_chain.c与scripts/check_unixnu_application_qemu.py，运行build3原字节UniXNU.efi独立应用：磁盘文件系统加载TOML→UniXNURun→真实图形菜单→UniXNUBootEntry exit。普通应用返回EFI_SUCCESS，unixnu:firmware标记入口返回EFI_ABORTED，均符合真实应用契约；两帧CRC15EA20DF。gST不被污染，VM缓冲区边界/行padding未变。不是只调用Ui/Menu的旧fixture，也不是enuma BDS实测。

最终out/menu-application-20261027/qemu6/result.json共22条命令通过，含9种ASan/UBSan生命周期/失败场景、ARM编译链接及两种真实应用入口。qemu1缺FileDevicePath链接符号，qemu2完整DevicePathLib依赖不足，改为真实DevicePathUtilities协议后qemu3通过；qemu4测试头NULL重定义失败，修复后qemu5/6通过。失败输出保留，不写成通过。

## 剩余板级阻塞与下一步

1. 当前板级SimpleFb阶段仍在诊断返回点，原临时GOP会撤销。需把提供器生命周期交给独立应用调用者，或保持到BDS消费结束；不能简单撤掉终止而留下已失效的GOP/栈上下文。
2. 完整应用的firmware host在配置加载前无条件UniXNUConnectAll；TOML connect_all=false仅控制注入驱动后的连接。QEMU已执行这个路径，但真实enuma不能将其当作已验证。应先明确需要连接的RAM FAT/图形/输入句柄，避免未经定位地连接所有OEM控制器；决定正常BDS路径或显式应用加载路径后再做新板级候选。
3. 实体输入仍须单独核对本机协议/驱动和按键，不将通用KeypadDxe源码存在等同于enuma已接入。QR后置。

当前没有新板级完整FD/启动镜像；本轮产物是已编译运行的ARM EFI验证器及可复用子应用绑定代码。R025原qualification2全部文件哈希重新核验一致，旧R022/23/24产物未触碰，requirements22/verified/内存参数不变，无提交推送。所有新证据位于新目录。

入口报告reports/enuma-menu-application-development.json。下一步离线把经过本轮验证的跨镜像绑定与有界提供器的所有权/恢复接到一起，再做完整新固件构建与独立资格；不得用QEMU成功代替实机BDS/输入验收。
