# enuma交接提示词：完整ADT/FAT已生成（D-171）

继续enuma/SM8250的iPadOS17.7.11/21H461完整链移植。用户希望一笔沿完整链到实际失败点、采集报错并修复一批。先读AGENTS、STATUS、DECISIONS D-170/D-171及operations/2026-10-25-full-adt-fat.md。

已完成：54,231,040字节实验prelink；新11,024字节ADT复用固定umi编码器，接本机历史FDT硬件信息；96 MiB真实FAT通过固定UniXNU payload.build生成，含内核/ADT/两份原始trust module/config。FAT SHA256 49b4d6229e88180c338eb41a347f8ecf9572ba60c7efc476ccf4573936818773。真实FAT回读和当前DarwinBoot实际解析函数ASan/UBSan主机测试通过。不要重复平台内核CI/预链接/另写FAT builder。

下一步：核对实际boot-v3组合和入口FDT/start/end及映射生命周期，适配umi只读RAM载荷边界并确认SFS及文件身份，接真实报错通道，然后迁移PMGR/UFS/root/Data。保存vendor ramdisk为2230字节，原长或页补齐前缀+FAT两种离线假设均不满足umi whole-initrd FAT契约；实际偏移未知，禁止直接硬编码2230/4096或复制umi保留窗口。ADT DRAM字段仅历史FDT信息，不是空闲连续RAM；board内存字段未改，入口请求仍R-001 512MiB。缺root UUID/平台种子/Data/GOP，不伪造。prelink runtime/loadable限制保持，未进入XNU/Hello。

固定UniXNU5fdbd5d/firmware aa9ec66/umi3eb7257；umi测试firmware48bc412与模板/最新树分清。参考仓只读，不运行会修改它们的builder。board仍example=true，无*_verified=true新增，无分区操作。本轮无实机；A历史单笔恢复通过且R-016 consumed，B仅离线备用，R-002失败/R-015暂停。新实机前全部文档提交推送并核即时身份/备份/日志恢复门禁，新增内存字段等按AGENTS审查。原始二进制只在out/，当前发布以Git为准。
