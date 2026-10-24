# 当前状态：D-171，ADT与FAT系统输入已生成，下一步v3运输和报错

按用户要求继续完整链/真实错误迭代。本轮已实际生成11,024字节完整结构ADT与96 MiB FAT，包含既有54MiB实验系统预链接、两份原始trust module及启动配置；不是Android boot镜像，未进入XNU或iPadOS。

## 本轮结果

FAT SHA256 49b4d6229e88180c338eb41a347f8ecf9572ba60c7efc476ccf4573936818773，路径out/full-boot/payload/payload.img；ADT SHA256 f8b5e0bc127967f785b464486f1a0ec0fac798592824206fd1ef91e7b0fb7cd2。复用固定umi编码器与UniXNU payload.build，不另写FAT builder、不拷umi硬件profile。chosen/NVRAM/产品安全兼容属性/CPU0/GIC/timer已组合；root UUID、私有平台种子、Data和GOP未伪造。

mtype从真实FAT回读并检查内核/trust摘要。当前固定DarwinBoot的真实AdtNode/ValidTrustCaches在ASan/UBSan主机环境接受实际输入，每个截断位置及损坏trust负例被拒绝；原窗口分配测试通过。不是UEFI分配或实机执行。实验prelink仍保留runtime/loadable限制。

历史FDT三段DRAM仅作ADT信息，非可用连续内存；board/bringup-plan未改内存字段，512MiB请求保持R-001，physical_base未知。没有新增verified或分区操作。已有FAT默认拒绝覆盖，因为ADT含新鲜随机熵。

## 下一步与主判断

保存stock vendor_boot v3的vendor ramdisk为2230字节。umi模板要求whole-initrd为精确FAT；将此vendor前缀按原长或补齐页后放在FAT前的两种离线假设都不满足该契约。实际入口FDT/组合规则未知，不能选2230或4096作为固件常量，更不能复制umi保留映射。

优先核对本机ABL与boot-v3公开实现的组合规则和实际入口FDT/start/end/映射生命周期，再复用只读BlockIO发布唯一有界FAT子范围并确认SFS和文件身份，同时接入真实错误通道。之后迁移SM8250 PMGR/UFS、root/Data；不重复内核CI或预链接发出。完整启动资格仍未满足。

专项见operations/2026-10-25-full-adt-fat.md；机器证据enuma-full-adt.json、enuma-full-payload.json、darwin-adt-contract.json、enuma-payload-transport.json、enuma-system-roadmap-audit.json。原D-170路线和B审计保持历史有效。

## 实机、授权与发布

本轮无设备动作、人工恢复请求或新硬停。最后实机是02:11的A/detail15：16.187秒ADB、31.312秒结束Android/root/A槽/解锁/原分区摘要核验；仅为当时记录，当前实时状态未刷新。R-016 consumed，不重复A、不自动发B；B离线备用。R-002失败跨复位日志不复活，R-015暂停，旧像素/内存/verified/破坏性分区门禁不变。

UniXNU固定5fdbd5d，firmware固定aa9ec66，umi引用3eb7257；board仍example=true。本轮之前7f8c54c已推送；本轮修改以同轮Git提交及远端核验为准。所有原始产物仅out/，参考仓只读，无新增人工待办。
