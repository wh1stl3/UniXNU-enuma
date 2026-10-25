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
