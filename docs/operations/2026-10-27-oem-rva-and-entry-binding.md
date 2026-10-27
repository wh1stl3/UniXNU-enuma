# OEM 返回地址归因与入口接线检查

本轮共享工作区检查：设备仓起点 e71a86e，实际 firmware 起点 7a5c920；两者 status 为空。另一 enuma 对话当时 idle。本轮仅新增独立分析工具、测试和文档，不启动其他写入者，不修改依赖、Core 补丁或冻结候选。

## 可落实的入口与尚缺的绑定

Mu_Basecore/MdeModulePkg/Core/Dxe/Dispatcher/Dispatcher.c:520 使用 DriverEntry->ImageHandle 调用 CoreStartImage。Image/Image.c:945 的 CoreLoadedImageInfo 对同一句柄调用 CoreHandleProtocol，使用 LoadedImage 私有结构反推；1660 处取得该结构，1745 处实际传入 Image->Info.SystemTable。firmware/patches/dxe-dispatch-details.patch 保留这条入口调用，并在调度期间绑定 EnumaStartingImage/File，之后清空。这是当前源码及补丁检查，未生成新 patched Core 或机器码资格。

因此未来接线必须在同一 Core 私有 Image 的入口前完成，核对桥接句柄、完整 GUID、LoadedImage 指针身份、BootServicesCode、有效映像范围和持久 context。入口前记录与 StartImage 最终返回分开：CoreExit/LongJump 可以绕过普通入口返回点，不能用 point21 缺失推造失败或死锁。驱动错误返回后映像可能卸载，记录需保留当次映像身份；不能把后续复用同一地址的代码归给旧映像。

GUID 不是 PE 认证；原始 PE 摘要必须在打包清单中绑定实际 FV 文件，运行时重定位后的内存不能直接套原始文件 SHA256。仍未完成 Core/profile 接线、包绑定与运行态身份验证。

## 本轮代码及验证

新增 scripts/map_oem_trace_rva.py：先强制本机 OEM PE 的315392字节与 SHA256 6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425；解析 ARM64 PE32+，仅接受唯一、文件有数据、可执行 section 中对齐的候选指令。返回 RVA 前四字节必须确为 BL 或 BLR，否则拒绝归因。BL 解码有符号立即数；BLR 只报告寄存器，不猜动态目标、函数名或服务名。静态调用点不是执行或死锁证据。

6项单元测试通过：正负 BL 偏移、BLR 未知目标、非调用指令、错 PE、范围/对齐/执行权限/截断、重叠 section。真实 OEM 五处旧审计指令重新核对：返回 RVA 1be8/1c3c/1c60/616c/61b0 对应 BL 3874、BL 5f78、BL 5f98、BLR x9、BL 61c0。输入是静态已知地址，不是真实采得的 OEM 日志。

证据：out/oem-rva-20261027-session-c999/mappings.json。原追踪检查在该目录 trace-regression/result.json 独立重跑通过5条命令，包括 ASan/UBSan、C到Python往返、7项Python测试（320模型快照）、AArch64对象与服务偏移/LR检查。未执行OEM PE、未新增板级固件构建。R027 image.img SHA256仍为0db64285d13c0e2f60e68403b0b5498433b0b0c0143f6ce336c1885dad4afb5a。

复现（设备仓WSL路径下）：

```sh
python3 -B -m unittest discover -s tests -p test_oem_trace_rva.py
python3 -B scripts/map_oem_trace_rva.py --pe out/firmware-vendor/Binaries/enuma/DisplayDxe/DisplayDxe.efi --return-rva 0x616c --output out/<全新目录>/mappings.json
python3 -B scripts/check_oem_service_trace.py --output out/<另一个全新目录>
```

## 取证出口阻塞与下步设计

现有 EnumaPixelTransactionArm.h 的物理回调有读写/屏障/hold/validation计数，PixelHold同步调用原Stall。已验收的窗口依靠同步完成恢复；如果把OEM执行夹在保存与恢复之间，非返回会跳过恢复，OEM还可能改变scanout或像素所有权，旧资格不能覆盖这个生命周期。如果在每次服务入口独立显示再恢复，则多次调用会超出旧总预算，并引入可观测的时延；高TPL/重入/异常或部分输出也没有已资格的异步恢复机制。

所以目前不能宣称存在符合旧预算的非返回取证出口，不能仅因RAM有记录就生成原厂实测候选。下一步应先实现独立的有限次数、可拒绝、锁存失败的入口观察状态机；输出在原TPL恢复后进行，记录器自身不调用被包装服务。窗口所有权必须在每次采样前重验，首次失败或非局部退出后停止再输出；还需证明中断捕获如何终止/恢复，或采用另一个已验证独立传输端。当前这些条件未完成，不借用OEM GOP/ConOut。

主假设仍是构造器/主入口内的真实依赖调用或其后续协议方法/硬件路径，比正常Exit后控制器连接更值得优先取证；现有S005/006/007只能提高该区间嫌疑。若采得入口返回/Exit汇合且随后停止，须转向Core后置路径；若采得明确失败返回，应沿真实错误分支分析；若只有服务入口无返回，只标本快照未观察到，并保留输出失败/异常/记录停止等竞争解释。三服务之外的协议方法/MMIO/SMC/锁及SMP仍不在验收范围。

实机继续暂停，无ADB/fastboot、部署、录像申请、远端推送、内存或verified修改。R027未消费。本轮本地提交仅上述代码/测试/文档，提交号以git log为准。
