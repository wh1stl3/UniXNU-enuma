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

## 几何检查实施前排序

f0cef6f稳定staging/所选DSI递增支持后，“首候选完全未挂接”和“整个接口停摆”嫌疑降低。中等置信工作假设转向混合裁剪/遮挡、LM实际输出/pingpong/DSC连接，以及fetch/地址可见性。先用012715b step20区分源/输出尺寸不匹配和关联LM矩形越界；这是只读配置检查，实际像素/fetch与后段关系仍需证据。如果几何通过则降低简单缩放/越界解释，不能据此排除遮挡或scaler模式。若取得该候选像素实际被取数且到达面板的证据，应进一步下调这些假设；Boot v3仍无必要切换。固定小米52a2f18 sde_hw_sspp.c和sde_hw_lm.c及原enuma FDT契约见reports/enuma-scanout-geometry-sources.json。

## 候选输出矩形配置几何实测更新

同源step19对照和step20正/互补时序支持：保留首候选稳定staging及所选活动DSI两窗递增条件，首候选源/输出宽高相同、至少128x8、整个输出矩形位于关联LM配置范围内，输出大小/位置/LM大小每窗保持。仅配置几何，不证明scaler/decimator模式、排除区、alpha/遮挡、LM实际输出、fetch或可见路由。 query1-query2 ADB差-5.39秒包含启动噪声，不能当精确频率或实测100ms。

稳定配置几何获得支持，降低简单源/输出尺寸不匹配和矩形越界嫌疑；下一步首查alpha/遮挡及LM→pingpong/DSC实际连接，与fetch/地址可见性并列中等优先。若取得可见的候选像素/fetch对应证据则可推翻该主判断；再查面板后段。 R-005 consumed，不重放像素或盲写寄存器。

## 混合配置检查实施前排序

012715b互补支持源/输出尺寸一致、完整输出矩形位于关联LM内，简单几何不匹配嫌疑下降。首候选完全未挂接、接口停摆也已有相反证据。当前中等置信主判断：局部其他staging/dim/alpha配置及LM实际输出连接、fetch/地址可见性仍需区分；先以ff3db30 step21保守模式取得增量。固定小米LM dim bit16表明没有其他SSPP不等于没有遮挡；major6使用packed常量alpha。若step21通过，应下调该LM局部其他staging/dim/常量透明解释，把实际LM→pingpong/DSC和fetch/地址可见性列首查；若拒绝，先分离未知/边框、dim、合法其他blend模式，不能直接判实际遮挡。真实候选取数/像素到达物理输出的证据可以推翻该方向。来源与11项FDT偏移见reports/enuma-scanout-blend-sources.json。

## 候选单源混合配置实测更新

单源混合谓词refused，未取得合格的保守配置证据；不能直接认定遮挡或透明。拒绝可能来自其他/未知字段、边框/dim、合法的其他混合模式或继承门控/稳定性，需拆分。 query1-query2 ADB差4.359秒包含启动噪声，不能当精确频率或实测100ms。

保守混合配置未获支持，结合同源step20对照优先分离其他staging/边框、dim及BASE/混合模式，再判断是否需要检查真正遮挡；不把合法的其他alpha模式直接当错误。 R-005 consumed，不重放像素或盲写寄存器。

## 六类拒绝定位实施前主判断

按用户更大胆推进要求，中等置信主判断是ABL遗留混合状态与过严观察器不匹配，先查border bit24和合法alpha模式，暂不把step21拒绝当显示故障。小米固定52a2f18 CTL在无base source时也会设置border位，LM有独立dim层，major6用packed alpha；本机DSI/staging/几何已有支持。step22一次稳定采样六类、正反时间编码交叉验证，拒绝容差外数据。border-only则优先修正观察器假设并查INTF_MUX；dim则查覆盖stage/矩形；alpha则解码实际系数；其他staging则解码字段和层次；继承失败先隔离门控/稳定性。若新证据反对优先假设，按类别调整，不扩大写入授权。固定源与FDT沿enuma-scanout-blend-sources.json。

## step22超时修正

六类时间编码实机超时、人工恢复独立通过，没有分类结果。新增长等待/继续采样是首查隔离点，中等置信，不能宣称面板/混合硬件问题。撤回将长时间编码作为下一轮取证通道的决策，改回两次已验证100ms与单一staging（局部忽略border位）判据。此前过严观察器假设仍待验证，非事实。

## 同源对照超时后的根因排序修正

c45e52a step20对照也超时、人工恢复独立通过；与成功8fd3e62 step20的SimpleFb .text/data/pdata/reloc完全一致，79模块77一致。长编码或新blend采样不能单独解释两次失败。中等置信先查恢复后ABL/启动状态、PcdDxe有效内容、打包及是否实际进入DXE/MMIO；当前没有执行位置证据，不定责面板/DSI/alpha。先离线解析差异并准备更早停止定位候选，冻结未执行显示探针。
