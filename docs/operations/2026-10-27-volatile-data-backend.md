# 按依赖推进：易失Data块后端

2026-10-27，继6f2f892之后。按[官网平台/OS服务](https://unixnu.com/porting/platform)与[驱动集成](https://unixnu.com/porting/drivers)核对：Data格式只是输入，下一步必须实现实际块I/O、初始化/释放，再接所选OS的storage ABI。仍仅隔离worktree，无设备、推送、内存字段或verified修改。

## 依赖核对结果

现有30组件prelink的emitter.json确实列有ApplePMGR、IOStorageFamily和IOCryptoAcceleratorFamily，不能把“缺服务”误判成“缺组件名”。umi的`build-umi-platform-power.py`还依赖匹配内核的`IOPlatformExpert.cpo.json`、生成的IOPMGR头、340槽虚表与原始候选绑定；Data配方依赖`storage-abi/include`和`interface-audit.json`。本地现有产物中未找到这些配套输入，没有复制umi的固定地址、构造伪IOKit头或绕过ABI检查。

在此边界内，先完成无需UFS持久化的易失Data块后端；真实UFS controller/stream、PMGR服务、IOKit注册仍是后续集成项，不以默认成功值替代。易失Data不是磁盘持久化实现。

## 已实现

`drivers/EnumaPlatform/EnumaRamDisk.cpp/.h`通过C ABI接入固定NativeRamBlock `d4d22d9819b0162eda49f6402235dddc2279410d`的真实SparseDisk算法，不复制上游源码。接口如下：

| 接口 | 行为及调用约束 |
| --- | --- |
| enuma_ram_start | 检查DBRDISK1和<=2GiB的易失路径范围；分配零化页表和非零页，全部导入成功后才发布内部状态；失败释放所有已分配资源 |
| enuma_ram_io | 512字节扇区、描述符长度和方向检查；读零洞，写时分配页；返回真实已完成字节，短复制/分配失败不会报告完整成功 |
| enuma_ram_info | 返回逻辑容量、resident字节、页表字节及显式resident预算；页表开销单独列出，预算不是设备内存预留 |
| enuma_ram_stop | 同一外部锁等待在途复制结束，撤销状态并释放页、页表及对象；重复stop安全，后续请求返回offline，可重新导入seed |

整个start/read/write/info/stop共用调用方持有的gate。gate、ops及disk句柄须比全部调用活得更久；最终释放句柄前调用方排空调用。transfer不可重入、不可保留页指针；读方向只把页数据复制至描述符，不修改源页。完成通知必须在接口返回、锁释放后执行。部分写会留下已完成前缀，不承诺原子写或持久化。

新对象以`arm64-apple-ios17.0`编译；检查Mach-O CPU/subtype及LC_BUILD_VERSION为iOS17。生成`libEnumaRamDisk.a`，包含start/io/info/stop四个真实入口；未解析符号仅memcmp/memcpy/memset，需要最终XNU链接提供。交叉编译只补标准C内存函数声明，不提供伪造OS类。

## 验证

`out/kernel-userland-20261027-3/ram2/`为最终证据，ram1保留前一版本。ASan/UBSan测试使用上一轮真实APFS seed（8a4483bc…），经块后端读取完整512MiB并逐字节匹配原始APFS文件（b2c589db…）。覆盖：

- 23个实际seed导入分配点逐个失败，全部清理且不发布半初始化磁盘。
- 非零预填分配器仍能正确零化；短写、跨页写回读、非法扇区/长度、重复start、stop后offline、再次导入。
- resident预算耗尽与写页分配失败；失败后读零洞仍正确。
- 并发stop确实尝试获取被读取持有的gate后，才允许复制继续；最终完成读取并清空分配记录。
- 无持久化回调、磁盘写入或目标OS挂载；sanitizer无泄漏/越界报告。

归档SHA256：`f9f357d00513b4318501ae3213c47477a23e94becc605b64a2dcb67c28af8b0c`。复现：在WSL执行`python3 scripts/check_enuma_ram_disk.py --seed-dir <kernel-userland-20261027-2/data1/seed> --output <新的本仓out目录>`。输入、固定生产头和本地源码摘要见result.json及`reports/enuma-volatile-data-backend.json`。

## 下一个依赖节点

1. 准备与当前平台内核/所选donor匹配的XNU生成头、编译记录及storage/PMGR ABI证据；不能拿umi已安装内核的归档直接充作enuma构建。
2. 接入真实IOBlockStorageDevice/provider与初始化调用点，把该后端的内存/锁/描述符操作绑定XNU；匹配Root/Owner/Data UUID及策略。
3. 将归档进入XNU链接并证明调用可达，再验证挂载和用户态。持久化UFS另需本机stream、队列/电源/DMA取证；桌面仍依赖CPU framebuffer/IOSurface、HID及实际进程链。

这轮未重链接内核、未重新打包FAT、未注册IOKit服务，没有APFS mount、launchd或SpringBoard运行结论。OEM候选、R027、原root/Data/FAT保持；继续不上机、不推送。
