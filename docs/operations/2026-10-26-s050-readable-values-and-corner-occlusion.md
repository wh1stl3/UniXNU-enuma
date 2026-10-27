# D-300：S-050 已恢复；真实日志数值可读，圆角遮挡使完整页面未通过

2026-10-26，Asia/Shanghai。设备工作根 D:/Code/PortingiOS/enuma/UniXNU-enuma，实际固件 firmware/；独立 uefi-enuma 不混用。用户在确认“正在录像”后执行 R-022 唯一临时 boot，S-050/R-022 已 consumed，不重复。没有刷写、擦除、改槽、提交推送或 nuwa 操作。

18:21:03 发出冻结镜像 f684ef22ea79178953ff8efcc81fb2243f189a096ef276a676c6a27e7b4b6e5b，执行ID2070e2ad-2885-4c83-a948-26311baa1737；boot命令返回0。Android自动启动完成62.594秒，启动原点40.634..40.753秒完整落入预声明39.252..41.748秒唯一code5窗，间接支持本次CPU事务及原区域恢复读回。18:23独立只读后验确认Android/root/A槽/解锁及boot_a/vendor_boot_a与本地备份摘要一致，boot ID与本次返回一致。当前设备Android，零恢复按键欠项。

用户照片已放入 Media-enuma/S-050-R022，直接查看可读出完整 ordinal=0000001f（31），status高低32位均00000000，完整EFI_STATUS=0（EFI_SUCCESS），末尾“+”可见，表示更早环形记录有丢失，数量未知。左侧C页面标识受屏幕圆角遮挡，完整三行转录不通过；遮挡字符保留?，不按预期补字。日志数值可读是本次实质进展，不把整页记为通过。

这些数值属于冻结源码选择的此前已完成point13记录，不能当作当前显示provider返回值；画面没有GUID/sequence/boot ID，不能用ordinal31直接命名驱动或宣称全固件成功。单张照片不能独立验收8秒持续时长。S-047固定字母实验不再重复。

按观测不完整规则停止追加实机，R-022单次授权和claim已消耗，S-001..050不得自动复用。保留照片原字节与冻结R-022源码/镜像/资格；下一步仅离线分析圆角遮挡、给新页面设置有依据的内缩布局并独立验证，不能原图重跑。尚未实现或批准新像素候选，不清requirements22，不改变内存/verified/分区权限。

D298完整3MiB开发FD e8251bf1和Boot v3 6bc685ae的离线构建成果保留，仍是stage10/BDS前停点、空ramdisk，不能当菜单实机候选。D295归因日志/D296-297 QEMU菜单链与WT后端保留；真实全局DEBUG、ConOut、正式GOP、菜单及输入仍未验收。

原始实拍媒体只在 D:/Code/PortingiOS/enuma/Media-enuma/S-050-R022，本地主机未录音/摄像，不上传。证据：reports/enuma-native-route-S-050-result.json、reports/enuma-s050-visible-log.json、out/r022-live-20261026/postcheck.json；完整操作见 [D-300](operations/2026-10-26-s050-readable-values-and-corner-occlusion.md)。当前不再等待录像开始，无追加启动进程。

补充证据边界：本次仅收到一张由用户关联到S-050目录的照片，没有整段视频用于独立测量显示时长或证明全程。直接目视转录第一行使用?保留遮挡，严格完整页面解码器拒绝该转录；不补C后再声称整页通过。+表示Dropped非零，不给出不存在的具体丢失条数。冻结页无GUID，ordinal不能直接对应APRIORI位置。

记录修正：独立postcheck辅助脚本沿用了precheck的clock-samples.local.json文件名，覆盖了辅助预检原始时钟采样；precheck.json摘要保留。已将该侧文件明确另存为post-clock-samples.local.json并记录clock-sidecar-note.json，不把它标作预检原始数据。实际S-050主runner独立保存的pre-boot-clock.local.json及post-boot-clock.local.json均完整，摘要已绑定，时钟判读用主runner原始结果。未重新执行试验以补记录。

旧滚动观察报告的同字节原件仍在S-049 human-capture目录，并另存out/r022-live-20261026/prior-system-trial-observation.json；旧资格/冻结二进制未覆盖。R-022批准前与consumed前配置分别保留。claim保持原创建记录，consumed标记/本次执行ID与结果分别绑定。
