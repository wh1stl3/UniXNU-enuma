# enuma交接提示词：boot v3运输候选已完成离线资格（D-172）

继续enuma/SM8250的iPadOS17.7.11/21H461移植。用户希望尽可能完整链启动、读取实际错误、每轮修复一批，并尽量同一启动验证多个点。先读AGENTS、STATUS、D-170至D-172及operations/2026-10-25-boot-v3-payload-transport.md。

已有：54MiB实验prelink、完整结构ADT、真实96MiB FAT；新增EnumaRamPayloadDxe复用固定umi只读BlockIO，适配本机boot v3原长vendor+generic拼接。实际ABL PE指令已确认原长推进，无页对齐。运行时仍严格核x0 FDT、现有映射、起止/长度/不重叠、前缀/BPB/完整FAT CRC，再发布块设备；不扫描、不猜第二偏移、不新增映射。CRC是传输损坏检查，不作认证。

firmware pin698b7c17dbbd80993070a45e2aa5ae15d330b63b，已推送。完整UEFI实际构建通过；32个保留OEM PE/DEPEX不变，仅省略UFSDxe。boot-v3镜像103817216字节，SHA256 194fa0f2bf51236ba7d1ed2f741ea1597104c8278197a0485b039b8e100f8b9e，资格归档out/full-boot/transport/qualified-698b7c1。实际编译宏、FD内新PE、常量数组/写保护机器码及AOSP往返核对通过。host ASan/UBSan范围/非对齐首尾/溢出/损坏/写入拒绝通过。不要重复已有内核CI/预链接或另写FAT/BlockIO。

同一候选记录13项：MAP/FDT/INITRD/PREFIX/BPB/FAT CRC/BLOCKIO/CONNECT/SFS/KERNEL/ADT/TRUST/CONFIG；前置失败停止依赖项，未执行NOT_READY。SFS/文件放在BDS，旧60秒暂停在payload模式移除。报告只同次有效，Print/DiagDraw可见输出在enuma尚未实证。

下一步先闭合可观察错误和恢复条件，再让一笔受控完整输入启动读取这批结果。本轮没有实机，不把构建或报告协议当运行通过；PMGR/UFS/root/Data/UUID/平台种子仍缺，prelink runtime/loadable限制保持，未进XNU/Hello。源门禁不能因多验证点放宽。

UniXNU仍5fdbd5d，board仍example=true；无board/plan内存字段变更、R-001仍512MiB，无新增verified或分区操作。firmware/为权威，standalone D:/Code/uefi-enuma旧74598df和已有Mu脏状态保留。参考仓只读，二进制只在out/。A/R-016 consumed、B备用、R-015暂停、R-002失败不复活，实机前全部文档发布及即时身份/备份/日志恢复门禁保持。发布状态以Git与远端核验为准。
