# 固件编译入口归属

实际实现已迁至uefi-enuma提交00ddc01的Resources/Scripts/build_enuma_firmware.py，preflight桥同仓。UniXNU-enuma同名脚本缩为固定提交/清洁状态/文件摘要核验及兼容调用。直接入口显式接受--device-root；board、依赖锁、上游资格策略、私有输入与out输出仍由设备仓提供，不声称无设备契约独立构建。Android boot打包、设备测试/备份恢复仍在设备仓。

旧迁移前26b1f99 step2/5均实测自行回Android，用户确认无按键，ADB17.024/16.943秒，完成/root/原摘要通过。迁移后00ddc01 step2于21:55:15启动，ADB15.865秒、完整核验33.078秒，用户确认全程未按键，原摘要通过。

重建不是逐字节相同：step2解包比较显示SimpleFb、DxeCore及OEM内容一致；差异为SEC编译时间字符串的排列和三处相应引用位置，以及PcdDxe RSDS调试标识八字节；压缩级联放大整包差异。不能声称可重现构建或所有可执行字节相同。原始逐section比较在out/build-ownership-comparison，报告单独记录。此次不借迁移改诊断代码、内存或verified。

当前迁移版step2已构建/审计并实测，step5重建及bundle/四负例/workspace均已通过；最终构建和bundle结果见reports/enuma-gop-mode-split.json。迁移前配置和报告保留为*-26b1f99.json，不将其当当前源锁通过记录。后续step6读取Mode头部，尚不能写屏。

迁移后step5未单独实测；其SimpleFb和Core逐字节与已测旧step5相同，迁移版step2对照已自行返回。下一候选step6正在构建，后续单独审计与实测，不声称step6已通过。
