# Pool后备页搜索的全局定时门

2026-10-23（Asia/Shanghai）。承接D-041和用户“继续吧”。保持51MiB DXE Heap、512MiB owned请求、原内存表/example/verified/OEM字节与R-002停止状态。只在已固定Mu的真实pool后备页搜索结果接入有界Timer/PSCI，不复制nuwa堆数值或帧缓冲出口。

## 精确契约

固件7276dcd，Mu cfb93724a06ff86ff5ba971413368a7809ee42a5。在MdeModulePkg/Core/Dxe/Mem/Page.c的CoreAllocatePoolPages调用FindFreePages之后、原Start==0失败分支及转换之前调用EnumaPoolSearchCheckpoint(Start)。detail26观察Start==0，detail27观察非零成功，后者作为同调用点正对照。为全局门：GUID必须省略，ordinal1仅CLI占位，builder拒绝目标驱动筛选，不能归因Display或当作PE返回门。

原pool包装层已持gMemoryLock；hook不取锁/解锁、不遍历map、不分配、格式化或打印，不调用GetMemoryMap，也不改变Start/类型/guard/返回状态/资源。只复用已固定的Arm计时器MicroSecondDelay和直接PSCI ResetCold；进入选定门即延时复位、复位返回则deadloop，不继续probe。实际库实现固定仍要核对，持锁复位本身改变时序，不能说无扰动。

失败并不等于总堆容量耗尽：可能与允许地址、bin、类型、对齐、guard或可用连续块有关。本门不覆盖所有AllocatePages/AllocatePool参数错误，也没有请求大小/free/largest数值或驱动归属。未命中只是未观察该门，不能据此排除所有内存错误；搜索成功只代表该次搜索非零，不表示完整分配/转换或GOP成功。

## 来源与构建接线

不加入新board patch清单，沿已有dxe-dispatch-details扩展patch增加Page.c片段；原25文件/六patch保持。Page.c在out规范化LF并校验固定基线，source preflight复制新header和原Stage header至Mem目录；原官方backend严格应用/还原，builder将Page.c纳入core还原校验。45项来源锁固定header/扩展/元数据，无新地址或持久RAM。

17组实际header ASan/UBSan覆盖0/非零/UINT64_MAX、2/7秒、禁用stage/detail及持锁adapter。51组Dispatcher/image header检查确认全局26/27不由分发器伪造；46项Python包含组合patch重复重放及CLI全局选择拒绝通过。新增测试首轮发现自身旧系列误加新断言、CLI缺required参数，已修正测试夹具并重跑通过；未发生设备动作。源码CI39885298128通过并回读PASS，但不代替实际固件构建。

## 实测顺序与恢复

先构建/审计/打包detail27成功正对照，再根据可控返回结果测试detail26失败分支与延时对照；保持无UFS32-OEM诊断模式与默认33模式区分。每次重新核对唯一enuma、boot完成/root/解锁/槽位、匹配备份与分区摘要，临时fastboot boot后核验实际恢复。过程时序/镜像和FD摘要全部保留。无flash/erase/改槽，不以黑屏/复位当驱动或XNU成功。运行结果后续追加。

## 第一份正对照

7276dcd无UFS32模式、全局detail27成功门2秒于09:44:53临时启动：ADB16.108秒、Android完成31.624秒，自动恢复/root/原boot与vendor_boot摘要正常。镜像c7807951e9b0c1b6c300185b39f0334b984893fdf5004c360356af5b365e4876，FD3af3c06d84280270a6e87cc6ac234ade040191c4135028d4335b359a79d08966。官方backend/core还原（含Page.c）、32OEM/BootShim/v3审计通过。单样本短返回与成功门一致，尚无本门2/7对照，不能据此精确计时或认定完整分配成功；detail26正在构建。

锁与库核对：固定Pool.c的CoreAllocatePool先取mPoolMemoryLock，CoreAllocatePoolPagesI再取gMemoryLock，调用Page.c后才释放；本hook不操作两锁。DSC选择ArmArchTimerLib与ArmPsciResetSystemLib，后者ResetCold只在栈设PSCI SYSTEM_RESET参数并调用ArmMonitorCall，前者延时读取自由运行计数器，不依赖gBS分配或事件；不把这一静态事实替代实机复位核验。

## 完整2/7结果

同source7276dcd、无UFS32模式。成功门27：2秒09:44:53 ADB16.108/完成31.624秒；7秒09:58:57 ADB21.478/完成35.243秒，差5.370秒，支持真实hook可执行。7秒镜像724ee8c9647a8ea08fc064979796435f1e58491004ff97cedefd54482de25397，FD90b56ca6cb9ea63b5ef2705e47fdde68793dc56b642764f7bcf603d7738c4856。

失败门26：2秒09:49:36 ADB31.129/完成46.588秒；7秒09:54:19 ADB32.248/完成46.555秒，差1.119秒，无应有5秒响应，未观察该失败门。2秒镜像666772173f91e061945190981b64c16d52b0e46bc697fd6d102a2b8e2acabc74，FD2311495361099e1da7b9096d0478958fcf084156fa4aefb52d3ad1bad8f5a056；7秒镜像a84e9e7fdd434a3bb841c4abbc09af49e7dd91bee40482c7e17670fc34c83d5c，FD4fff5cefc865346eabfad588f9397ad6b6275f7f9b9bb1b5ba9b4f7dfdc6e6eb。

四候选官方backend/core还原、32OEM PE-DEPEX、BootShim和v3审计通过；四次自动Android/root/原boot与vendor_boot摘要正常，无flash/erase/改槽。所有噪声样本保留。不能用负向门证明零分配失败，也没有本轮free/largest/request值；成功搜索不代表后续guard/保护转换成功。没有依据实施nuwa式扩堆，仍保持51MiB与512MiB请求分别不变。

用户继续要求从其他设备借鉴方案。已复核alioth/elish的Metronome、基础协议顺序和SimpleFb路线，下一里程碑优先独立SimpleFb诊断而非改堆；原生默认和该版证据保持，具体新source/模式与测试另记，不提前称已进入GOP或XNU。
