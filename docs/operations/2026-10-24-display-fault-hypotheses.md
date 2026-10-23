# 显示故障主判断与可推翻条件

用户要求结合具体情况和公开资料给出更明确的判断。以下是工作假设的优先级，不是新增实机结论；不把主观排序包装成统计概率。源码固定到本仓已锁的小米内核52a2f180865f8368828985d6384130acd093fa93，6份显示源摘要见reports/enuma-native-display-diagnosis-sources.json。对照旧Qualcomm d066来源可见额外版本差异，不因此改写旧探针语义。

## 主判断

当前主要故障位于持续显示的接管/路由闭环，而非Boot v3头解析。第一嫌疑是像素候选选择未证明活动路由，第二嫌疑是ABL到UEFI之间保留了配置字而实际输出链路未存活。Boot格式本身低优先级；DTB/vendor_boot输入路径可能间接影响交接，须独立验证。

1. **首查：写到了合法但不参与当前输出的SSPP或图层区域，中等偏高优先级。** 本仓EnumaScanoutFindBoundedDescriptor遍历8个SSPP，在第一个地址/格式/跨度合法项立即返回；它没有查询CTL/LM挂接关系、最终输出位置、缩放/裁剪、混合层遮挡或双DSI路由。R-005使用这一候选。CPU成功写入/恢复也不会让未参与输出的buffer出现在屏幕上。step12的支持与白条未确认并不矛盾。可推翻条件：证明候选所属SSPP确实被当前活动CTL/LM挂接，沿输出位置/裁剪/混合/双DSI链路覆盖可见区域，且其内存是实际fetch目标。

2. **次查：持续显示交接不完整，中等优先级。** step14互补时序只支持至少一个TIMING_ENGINE_EN非零；静态配置可保留，不能证明时钟、fetch、DSI、面板/背光或双链路正在完整工作。实际对应小米源码另有INTF_STATUS(+0x26c)状态路径，并由catalog功能位选择；旧d066来源没有该路径。当前step14/15/16仍只声明原配置/计数谓词，不能称真实enable状态已全面查清。可区分证据：计数前置通过后是否推进、硬件版本/适用状态位、活动CTL及INTF/pingpong绑定。若计数推进支持且路由正常，面板/背光段优先级上升；若前置符合但不推进，交接/时钟/fetch优先级上升，仍要排除计数语义及等待异常。

3. **随后查：地址翻译与内存可见性，中低优先级。** 当前没有拿到实际SMMU状态，不能把SSPP地址一律当CPU物理地址。但小米KMS的splash路径明确将保留区做一对一SMMU映射；结合候选被限制在cont_splash物理区，不能仅因黑屏就认定IOVA是首要根因。需匹配当时实际映射。R-005实际PE具有cache维护和屏障，降低“完全漏掉clean”的嫌疑，仍不排除属性/别名/系统缓存差异。该实验没有导出寄存器数值，也没有在白色保持阶段读回白色；返回时序不能当像素可见性证明。

4. **低优先级：Boot v3头部导致不执行。** 多轮同源正/互补差异支持已到达目标驱动后的不同谓词分支，且能自动恢复Android，明显不符合单纯ABL拒收/完全未进入UEFI的解释。v1可能改变DTB选择/交接路径，但“版本号改成1”不会自动实现显示驱动、活动buffer选择或背光。若找到明确DTB交接差异或匹配enuma v1实测，再设计隔离变量的临时A/B；不整套移植外仓内存/分区配置。

RGB/BGR通道顺序也不是白条全无的首选解释：R-005写0xffffffff，各颜色分量均满。旋转、可见区域/缩放和混合则仍可能隐藏小条；不能因通道顺序降低而一并排除几何路由。

## 日志和菜单的独立原因

当前诊断候选在SimpleFb驱动返回点按Core门控主动延时复位；文本后端尚未接入INF/FDF/调用者，DXE/BDS/UniXNU菜单也未放行。菜单没有出现有明确的软件阶段原因，不能全部归因于同一个黑屏故障。完成可见显示后还需接文本输出并继续派发/启动管理器；换Boot头不能补齐这些阶段。

## 后续执行次序

先完成本轮已授权的计数配置与100ms有界增量正/互补验证，范围保持。之后优先固定真实硬件版本与对应小米CTL/INTF布局，核对候选SSPP→LM→CTL→pingpong/INTF→双DSI路径以及实际状态，不再把任意第一个合法描述当活动buffer。需要带来源的数值快照时先设计与审计现有日志通道；不盲增非零布尔测试，也不先写使能试错。读探针范围变化仍按AGENTS门禁，不继承R-005像素授权。

来源：[小米CTL](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/sde/sde_hw_ctl.c)、[INTF](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/sde/sde_hw_intf.c)、[catalog](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/sde/sde_hw_catalog.c)、[KMS](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/sde/sde_kms.c)、[AOSP启动头规范](https://source.android.com/docs/core/architecture/bootloader/boot-image-header)。本地实测仅reports/enuma-r005-device.json与enuma-dsi-timing-device.json，当前计数结果未产生前不得填入推断结论。

## 本轮计数实测后的更新

configuration: refused (query1-query2 ADB 5.297秒)；progress: refused (query1-query2 ADB 4.249秒)。互补时序非寄存器数值日志；配置/进展支持不证明buffer路由、面板或可见写屏；拒绝不证明不活动，近回绕复位/瞬变仍有歧义。 计数采样前置未获支持；即便step16也拒绝，不能据此断言已实际等待/采样、帧计数为零或显示停摆。ABL可能未启用计数而仍在输出；本轮保持只读，不为获得数值而写计数使能。

五笔均已由用户确认全程无按键且通过独立Android/root/原槽/解锁/原分区摘要核验。未获得可解释的计数进展观测，因此维持活动路由/持续显示交接优先的工作假设；不能将前置拒绝升级成显示时钟、面板或Boot v3故障定论。后续优先对应小米版本INTF_STATUS与CTL/LM挂接的有来源只读观测，而非重复相同前置或写计数使能。

## 本轮原生双窗实测后的更新

同源原生状态对照和正/互补时序支持：major6下至少同一活动DSI接口在两个连续窗口各发生1..64的非回绕帧计数递增，采样状态与配置保持。取得双窗有界递增的间接执行证据，非数值寄存器日志、面板可见性或SSPP路由证明。 query1-query2 ADB差-5.296秒包含启动噪声，不能当精确频率或实测100ms。

三笔均已由用户确认全程无按键且通过独立Android/root/原槽/解锁/原分区摘要核验。双窗判据以本节实测解释为准；活动路由及持续显示交接仍须独立核对，不能升级为面板或Boot v3故障定论。后续优先对应小米版本INTF_STATUS与CTL/LM挂接的有来源只读观测，而非重复相同前置或写计数使能。

主判断更新：整条SDE接口完全停摆的嫌疑下降，活动buffer/SSPP图层路由、fetch/地址可见性和面板后段成为首查；Boot v3头解析仍低优先级。旧时序/计数enable组合前置不适合直接判定当前ABL遗留管线的活动性，不能把旧拒绝当停止。双窗推进不证明内存fetch成功或物理面板显示，下一项最有区分力的观测是将先前候选Source与实际CTL/LM挂接及INTF绑定对应。

## 候选staging关联实测更新

同源step18对照和step19正/互补时序支持：major/minor6.0下首个合法描述的非virtual SSPP在某CTL/LM中staged，CTL选择的同一活动DSI两窗各递增1..64；描述/选中staging/接口掩码/时序配置保持。仅稳定配置关联和所选接口推进，不证明LM实际输出、fetch成功或物理/可见路由。 query1-query2 ADB差-4.297秒包含启动噪声，不能当精确频率或实测100ms。

稳定挂接关联获得支持，降低“首候选完全未挂接”嫌疑，下一步优先核对LM实际输出/pingpong/DSC、混合裁剪和fetch/地址可见性，再查面板后段。 R-005 consumed，不重放像素或盲写寄存器。
