# 原生管线首拒绝定位

S-029首次完整native路由审计间接分类Topology，boot-origin区间
22.241..22.328秒完整落入预定code3窗口；44.719秒Android完成，独立
原分区摘要核验和相机桌面通过。它越过了当次到达拓扑检查之前的接口
资格，不能宣称完整三样本稳定性通过，不能从类别推出具体CTL/LM。

下一候选只记录原首次错误发生阶段，不添加MMIO读取：CTL选择、源
staging、混合器/布局拓扑分别code2/3/4，其他拒绝code1，完整稳定候选
code5。与fafb8a3 native源码逐330个失败位置比较调用/输出一致；旧
严格GOP路径固定基线保持。实际上机结果以独立归档为准。

条件性主判断：若stage选择拒绝，应先核对“所有非零LM字均被当作活动
源”和严格拒绝border位的模型。固定小米
[52a2f18 sde_hw_ctl.c](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/sde/sde_hw_ctl.c#L852-L854)
将CTL_MIXER_BORDER_OUT定义为bit24；没有任何源配置或没有BASE源时可
置此位。该位本身不是另一条SSPP。旧step23虽有相同来源的局部解码，
但其同源对照超时，step23本身未执行，不能借用为本次已验证结论。

若细分返回CTL选择，应优先查活动CTL数量/INTF_ACTIVE位图，不能先动
border；若返回混合器/布局，则staging并非当次首个拒绝，转向具体LM
模式/混合/左右布局。当前不改任一拓扑门，不声称已定位border，也不
由固定内核代码推断本机UEFI接管时实际寄存器值。

## S-030：已定位源staging

S-030细分code3，boot-origin22.257..22.322秒，Android45.750秒，独立
恢复与相机桌面通过。首拒绝在EnumaSelectVideoRoute，而不是本次CTL
选择或后级LM检查。它没有读完三次完整管线，不能称稳定路由通过。

下一候选只对已经捕获的24个staging字分类：全部已知border差异且局部
规范化后恰好两条不同单源路由；已知源数量或编码不支持；未知/virtual
字段；混合器数量或重复源。原快照不变，原失败仍返回，不因规范化能
解码而继续读取后级。主机全部64种border组合、768单比特扰动和类别
负例通过；这不是本机border值的证据，必须等待新的合格实测。
# S-031 result and native border view (2026-10-26)

S-031's boot-origin interval17.246..17.316s lies wholly in predeclared code2.
Android completed40.812s; independent identity/root/slot/unlock/partition hashes
and camera desktop passed. The image is consumed. This supports the captured
staging's only strict two-source selection mismatch being the documented border
bit24. It is not direct register output or evidence of complete stable routing.

Next source52158d9 (documentation pin c45191c) isolates the correction in a new
native border sampler, leaving strict and original native APIs intact. Only the
RAM parsing view clears bit24; raw capture and stability retain that bit. Strict
route selection must still pass before selected SSPP/mixer reads. The same view
feeds mixer resolution and decode, preventing border-only inactive mixers from
being mistaken for routed mixers. Reads remain bounded330 and waits2x100ms.
Unknown bits, source count/duplicates, layout, format, address bounds and raw
configuration changes still reject. Successful audit still requires independent
CPU/SMMU address and downstream association before a pixel experiment or GOP.

## S-032 and first layout predicates (2026-10-26)

S-032 origin27.225..27.339s uniquely mapped to mixer/layout topology rejection;
Android completed51.297s, independent recovery and camera desktop passed. This
supports progress through native source selection/capture, not three complete
stable samples. The image is consumed. Source60dd3d9 adds only first rejection
classification: blend, mode, geometry or left/right assignment. Fixed c45191c
resolver status/output parity covers4608 saved-word mutations.

Working hypothesis: the mode predicate may reject legitimate per-stage alpha
output bits. This is a source-backed possibility, not a measured LM word.
The fixed [MiCode LM implementation](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/sde/sde_hw_lm.c)
lines139..150 updates alpha output while preserving bits31/30; lines70..88 set
the right-mixer flag in bit31, and lines104..120 pack FG/BG constant alpha.
The matching [CRTC implementation](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/sde/sde_crtc.c)
lines1330..1338 derives mixer_op_mode from stage/alpha conditions and line1492
passes it to setup_alpha_out. Current resolver rejects all mode bits except31.
A blend/geometry/side category would displace this hypothesis as the first
blocking predicate. Even a mode category needs precise bit/source correlation
before changing admission; bit30 remains unexplained and is not accepted.
