# 当前状态：D-273，S-044 原生显示管线合并审计资格完成，准备实测

2026-10-26T03:24:42+08:00。用户要求“继续推进 触发硬停再停，尽量一次推进最多的验证点和实测点”。本候选尚未发出。全部当前文档提交推送、即时身份/原槽/解锁/备份/恢复和观测门禁（当前无相机）通过后直接单次临时boot。

## 已证实与主判断

S-023活动mask3、S-024双窗帧推进mask3、S-025 ExactEnable3 mask0；S-026同次活动/非零Timing稳定/Enable稳定/帧推进mask1，S-027非零Timing稳定mask1。S-028同次三次Timing零且活动/Enable稳定/帧推进mask2。因此第二路Timing零不等于接口停止；旧非零Timing/Enable低两位3门可能过严。所有S-001..028 consumed，不重试；S-024首次仅预启动查询失败未发图。

S-029完整native审计有效返回Topology类别：boot-origin22.241..22.328秒，Android44.719秒。S-030细分返回source-staging-topology-rejected：22.257..22.322秒，Android45.750秒。S-031返回border-only-normalized-two-source-route：17.246..17.316秒，Android40.812秒。三笔独立摘要和相机桌面通过，均consumed不重试。已定位到当次border位与严格staging门的差异，不能称全三样本稳定性通过。

S-032越过staging门后返回mixer-or-layout-topology-rejected，boot-origin27.225..27.339秒，Android51.297秒，独立摘要和相机桌面通过，已consumed。当前layout细分=False，只报告首个混合/模式/几何/左右分配拒绝；layout模式code5是拒绝，不是稳定候选。固定c45191c布局解析器4608字段扰动状态/输出一致，新增14880码义组合通过。

S-033进一步定位到mixer-dim-or-blend-rejected，17.400..17.467秒，Android40.391秒，独立恢复和相机通过，已consumed。模式位假设不是首个阻塞，转向blend/dim。当前blend细分=False；code2所选源层dim、code3其他层dim、code4操作字、code5常量alpha，code1非本组；其他层不等于不活动。全部11层乘11个dim位置、四个实际采样分类及17280码义组合通过，不新增硬件读或放宽判据。

S-034结果selected-blend-operation-rejected，origin27.238..27.321秒、Android49.094秒；独立摘要和相机通过，已consumed。此前一次fastboot预查询失败未发图，按D-233恢复核验重入后通过。当前结构审计=True：独立Native3只回答几何/源布局/原始快照稳定性，跳过纯解析中的blend/dim/processing合格判断，保留BLEND|ADDRESS|TOPOLOGY=22，绝不清除混合要求或发布GOP。原strict/Native1/Native2不变。新选择器code5仅为稳定结构，其他选择器拒绝requirements22。实际330读/两等待边界、原始blend变化与帧停滞拒绝、768混合字扰动几何与左右门保留、17280结构码义组合通过。

S-035无相机实测route-or-geometry-rejected，origin22.268..22.343秒、Android44.125秒，独立身份/分区摘要通过，已consumed。几何拒绝先于源解码和三样本完成，不能宣称当次稳定。当前结构几何细分=False：Native4先完成安全选择下的330读/两次100ms及原始配置/双窗帧稳定，再做纯RAM几何分类；code2混合器尺寸、code3源局部输出、code4左右分配、code5合计宽度拒绝，code1其他/采集/不稳定/解码/成功未分类。code2..5才支持同次三份原始配置稳定与两路双窗推进；仍不提供数值或物理显示证明。768字段扰动分类/解析器一致、330失败点/两等待/配置变化/帧停滞优先拒绝和19680码义组合通过。

S-036有效返回stable-source-local-output-rejected，origin22.476..22.543秒、Android45.078秒，独立身份/摘要通过，已consumed。此次支持同次三份原始配置稳定与双路双窗帧推进；首个纯几何拒绝为源OutXy或OutSize，不能推断两者哪个数值不符。当前精确整屏坐标视图=True：Native5先验证原始稳定，再要求左0/右X等于左LM宽且Y0、源尺寸各匹配LM、左右唯一/总宽匹配；仅RAM副本把右坐标表示为local0+明确逻辑origin，再执行原几何和完整格式/安全/stride/地址包含/共同base/覆盖检查。保留BLEND|ADDRESS|TOPOLOGY22，不声明物理路由或GOP。768混合字/128源输出字扰动、330失败/两等待/原始XY变化、旧API仍拒绝及9项native Python测试通过。此模式code3精确坐标契约拒绝、code4源解码拒绝、code5仅稳定逻辑结构。

S-037有效返回source-capture-or-layout-rejected，origin27.444..27.524秒、Android52.562秒，独立身份/摘要通过，已consumed。未出现精确整屏坐标契约拒绝码，但宽泛code4仍不能直接等同某个解码状态。主嫌疑转为源格式/alpha与严格RGBX假设，次为地址/布局一致性；以新状态分类反驳或确认。当前整屏视图源解码细分=False：同一Native5、同一采样和判据，仅ReasonNativeDecode19且零输出要求时分code2几何/覆盖、code3格式/编码、code4边界/一致性、code5安全/其他源解码拒绝；code1未分类含采集/几何/运行/成功。19680真实头文件选择器组合和9项native Python测试通过。code2..5才定位到该次已通过安全采集、原始稳定、精确坐标与几何之后的解码拒绝，不提供寄存器数值或物理显示证明。

S-038有效返回source-format-or-encoding-rejected，origin22.400..22.520秒、Android44.610秒，独立身份/摘要通过，已consumed。此次定位到Native5的实际源解码Format拒绝，支持此前原始稳定/精确整屏坐标/几何阶段已通过；仍不区分格式字、opmode或unpack数值。当前alpha通道视图=True：Native6仅允许所选源236ff/237ff且至少一个237ff，RAM副本只清SRCC3_EN bit8以检查RGB存储通道；原始格式不变并比较稳定性。其他格式/压缩/无alpha输入拒绝，其他编码/安全/stride/地址/覆盖判据不变。成功仍保留22，并强制alpha_semantics_unproven=true；不能把ReservedMask当可写零alpha的GOP契约。64格式位扰动、三种alpha组合、330失败/两等待/原始alpha变化/其他编码拒绝、旧Native5保持Format拒绝和10项native Python测试通过。

S-039有效返回stable-8888-logical-structure-alpha-blend-address-and-downstream-unproven，origin32.452..32.522秒、Android57.704秒，独立身份/root/A槽/解锁/设备及本地备份摘要通过，已consumed。支持同次完整逻辑描述，不等于真实CPU像素访问或SMMU。S-040有效返回cpu-stage1-memory-attribute-not-write-through，origin27.434..27.538秒、Android50.390秒，独立身份/分区/备份摘要通过，已consumed。只支持首个覆盖页的读AT非fault且输出恒等，随后的属性非0xbb触发提前返回；写AT及其余页未执行，不推断实际属性或SMMU。当前CPU stage1查询=True：仅Native6 complete/requirements22后，对覆盖候选范围的每4KiB页查询读写转换，最多18432次AT；禁止像素数据访问/页表setter/缓存维护，保留22和alpha义务。code1前置或CPU上下文/回调拒绝、2转换/权限fault、3非恒等、4非0xbb、5全部页的stage1 R/W恒等WT；EL1最终stage2、真实RAM、SMMU、混合及可见输出仍未证明。56000故障注入/18432边界/11项Python测试通过，实际打包四AT/上下文/DAIF和PAR恢复已审查。

当前CPU属性细分=False：保持S-040查询/停止点不变，只细分原code4的最后PAR属性；code2=44 normalNC、3=ff normalWB、4=00/04/08/0c Device、5=其他非WT，code1未分类（含其他失败/全WT）。不改变缓存配置、不清任何义务、不声称其余页/写查询已执行。ARM允许PAR报告实际实施后的属性；A77文档有WT降NC规则，故S-040不是页表错误证明，主假设转为正常NC报告，执行核身份未证实。源码/实际库清单的控制台审计与菜单验收矩阵已独立落地。

S-041有效返回first-non-wt-attribute-other-encoding，origin32.469..32.529秒、Android53.922秒，独立身份/设备及备份摘要通过，已consumed。排除该次首个失配PAR的精确44、ff和00/04/08/0c；正常NC精确44假设未获支持，不等于所有Normal/WB策略被排除，因为分配/Transient提示有不同编码。下一步只分类缓存策略，继续保留首结果/未执行边界。

当前整段CPU策略审计=True：独立新诊断按原范围/18432上限执行每页R/W AT，保留fault/地址位和原始Frame要求；只在回调RAM副本替换ATTR以复用严格循环，绝不改实际PAR/页表。仅全部遍历后code2全段内外NC、3全段内外WT、4全段内外WB（允许分配/Transient提示差异）、5混合/其他；code1前置/上下文/回调/转换/非恒等拒绝，不能称全段通过。code2..5才支持该次所有覆盖页两类权限与恒等输出；code5不是正常内存资格。原严格WT与首属性API不变，不清22或alpha/真实数据/SMMU义务；CPU原始属性字节和提示位未留存/未导出，不能说具体MAIR数值已获知。全部256编码、混合/提示变化和18432最大路径主机测试通过。

S-042有效返回all-pages-stage1-rw-identity-normal-wt，origin22.454..22.558秒、Android44.172秒，独立身份/分区/备份摘要通过，已consumed。支持该次全部覆盖页R/W转换非fault、恒等且内外策略均WT，具体分配/Transient提示字节未获知；不能称页表错误、真实数据可读、EL1最终stage2/SMMU或可见输出通过。下一笔只隔离单个对齐32位数据读，不做缓存同步或任何像素写。

当前单字CPU读取=True：在同次Native6完整描述和整段R/W恒等NormalWT之后，再核对1600x2560/stride/extent/范围/对齐/requirements22，仅对描述base执行一次volatile32位load。零像素/MMIO写、零DC/DSB缓存同步、零映射改动，不导出/解释像素内容、不发布GOP。code1前置/上下文/转换/地址拒绝、2Normal策略与WT基线不同、3混合/其他、4读取契约/回调拒绝、5仅一个字读取完成；5不称整段数据可读、可写/实际显示/SMMU或alpha通过。max_framebuffer_reads=1是上限，未执行和超时不能写成已读。主机单次回调/非法范围/策略拒绝/数值独立结果及无相机精确只读门禁通过。

S-043有效返回single-aligned-cpu-word-read-completed-no-data-export，origin32.477..32.543秒、Android56.312秒，独立身份/分区/备份摘要通过，已consumed。实际单个32位load及私有栈值依赖的完成获间接时间码支持；不导出数值，不称整段RAM、写入/SMMU/可见输出通过。下一笔只隔离一个DSB SY，零像素写、零DCclean/invalidate，避免把屏障与新存储混成不可定位结果。

当前单屏障隔离=True：保留S-043单字路径，所有同次完整描述/整段WT/范围验证后，wrapper先且仅先执行一次DSB SY回调，再执行相同数据load及私有栈值依赖。没有DCclean/invalidate、像素写或缓存属性改变。code1..3前置/策略拒绝，4屏障或读取契约/回调拒绝，5单次DSB及单字读取完成；5不证明存储后的屏障或整行cache维护。max_barriers=1、barrier_kind=dsb-sy-before-data-read，失败前置零回调/屏障失败不读/调用顺序和计数及第五ARM profile仅一DSB通过。

当前native_border_view=True。独立native border路径在解析副本仅清bit24，原始字保留并逐样本比较；原Native2其余严格源/混合器/布局条件不变；结构模式Native3另保留混合未验证要求。原严格和原native采样API不变，staging模式仍只分类。独立border路径全部64组合保留原始快照、330读失败、border中途变化/未知位/混合器/等待/帧稳定性拒绝通过。

新独立native sampler采用固定小米52a2f18 v1 STATUS bit0门控FRAME，允许Timing零和Enable低位非3，但保留完整Timing/Enable字相等、双路三样本活动、两个100ms窗口各非回绕递增1..64。复用现有六CTL、所选两源SSPP、两LM混合配置和布局解码，采集前置首次拒绝立即返回；Native4把纯RAM布局判据放到安全采集与稳定性之后，不读取未满足路由前置的管线。旧严格GOP路径与固定基线逐回调一致，不因本审计自动放宽GOP。

## 当前候选与验证

固件93820068e213114d6eef7bf96c7c27e8d242cac8已推送。原R-004 MDP0xae00000/0x85000，最多330次读取、两次100ms，最高偏移0x6c26c；Splash0x9c000000/0x2400000不变。无像素/MMIO写、新映射、board/verified或分区操作，不发布GOP，不继承consumed像素批准。原完整采样成功保留ADDRESS|TOPOLOGY；结构模式成功保留BLEND|ADDRESS|TOPOLOGY=22要求。

选择器native_route_detail=False、native_route_staging=False；五码分类{"1": "prior-context-translation-or-identity-rejected", "2": "normal-policy-differs-from-wt-baseline", "3": "mixed-or-other-cache-policy-rejected", "4": "single-barrier-or-word-read-contract-rejected", "5": "single-dsb-sy-and-aligned-cpu-read-completed-no-data-export"}。码义以本候选归档为准：staging模式code2仅支持局部清除已知border后恰好两条不同单源路由、无其他未知字段，code3源数量/编码、code4其他字段、code5混合器数量/重复源，code1其他结果。staging模式code5不是成功；不继续后级采样，不修改原快照。完整SimpleFb GUID dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92返回点13/detail16接受warning1..5，cold延时2/7/12/17/22秒后deadloop，无dispatcher fallback。

ASan/UBSan原严格路径固定基线330失败位置/负例回归、新native330读失败和两等待失败、活动门控/配置/帧稳定性通过；对fafb8a3 native基线逐330边界比较调用顺序/状态/输出一致，三个拓扑位置fixture通过；staging64个border组合/768单比特扰动/快照不变及负例、12480staging结果映射通过；真实头文件7200普通和10080细分类映射、504入口/GUID/状态案例通过。主机测试只证明模型与边界，不替代实机。实际构建源码/宏、PE、FD R-004表、完整96MiB FAT与Boot v3已冻结审查。

镜像SHA256 232c49649fb8eda3d79fc696ecc08ae1b1a0fc5b0670df757ac1077cc3dee8ed；FD 50ffa7caf44651c6c7ec699ad8f3341025ea603e3af56af2671967cd8a84a9df；归档out/inherited-gop/qualified-native-cpu-barrier-9382006。资格reports/enuma-native-route-qualification.json、代码审计reports/enuma-native-route-code.json；详细审查docs/operations/2026-10-25-native-route-code-audit.md。

固定S-021/S-022校准计划{"baseline_envelope_seconds": [10.25199999997858, 10.347999999998137], "tolerance_seconds": 1, "sampler_seconds": [0, 0.2], "code_windows_after_issue": [[11.25199999997858, 13.547999999998137], [16.25199999997858, 18.547999999998137], [21.25199999997858, 23.547999999998137], [26.25199999997858, 28.547999999998137], [31.25199999997858, 33.54799999999814]], "source_trials": ["S-021", "S-022"], "full_interval_containment": true, "uncertainty_limit_seconds": 0.25, "limitation": "Indirect timing inference; boot overhead can change. No exact register or unique execution-path proof."}。整个boot-origin区间须唯一窗口包含，三样本新boot-id且交集宽<=0.25秒；不按观测调整容差。时间码仍是间接分类，不是直接寄存器值、物理路由或可见显示证明。

## 恢复、硬停与下一步

最近独立恢复out\device-tests\20261026T030530-recovery-reconciliation.json：Android完成/root/A槽/解锁、boot_a和vendor_boot_a与本地备份摘要一致。每笔之后重新核验。用户2026-10-26明确当前未到点屏阶段无需摄像头，本候选采用--no-camera，保留同一有界runner的ADB/fastboot状态、新boot-id/三次uptime时基和身份/分区摘要；出现可见输出、需判读画面或人工恢复时再启用摄像头。native Python测试包含无相机成功/预启动失败/超时与consumed账本，均stub设备调用。原始视频/图像仅本地out，不上传、不录音。

D-233：镜像发出前fastboot查询异常不作整轮硬停；恢复核验后允许重新进入一次fastboot，完整product/slot/unlocked门禁仍须通过。不重复已发图，不忽略FAILED正文。真实75秒无识别恢复、恢复失败、所选观测通道失效/时基失败（无相机试验不要求图像）或新时间码模糊，停止追加并当轮落实交接；有效负分类继续分析。

当前目标为UEFI固件日志上屏后接UniXNU菜单；见docs/operations/2026-10-26-uefi-console-menu-validation.md独立验收矩阵和reports/enuma-console-path-audit.json。GraphicsConsole/ConSplitter、Print、DiagDraw与菜单入口已有代码/打包但本诊断早于BDS返回，未实测；全局DEBUG实际空SerialPort，GOP就绪不会自动恢复日志。DiagDraw直接写固定颜色，须先处理mask/alpha/同步并隔离Print，正式GOP发布/安全屏幕日志接收与早期RAM记录重放缺失。按当前CPU分类继续隔离；后续仍需CPU真实数据访问/SMMU/混合与下游证据，不能声称点屏，iPadOS图形不作为本阶段验收。
