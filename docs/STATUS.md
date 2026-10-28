# v14 软件资格完成，待实机

v14 已完成 build2/qualification2：同时核对原厂参数来源和实际 MMU 建表代码，新增故障寄存器与异常后地址翻译取证。73 项 Python、8 组宿主检查、354 处链接指令删除、36 项映射变异、28 处参数指令删除和 27 个页表分配失败点检查通过。2501 项来源绑定；软件就绪，trial 未消费，尚未上机。

## 精确候选

- 镜像：`out/oem-context-20261028/qualification2/image.img`，3153920 字节。
- SHA256：`2e3e6814fac86e6a7da35887f03c50abf0e6986bdf7d8d4a22949621a2961a4c`。
- 资格 SHA256：`946ba1408495899bea81980fc896df487d2b81d7569d552607545496433ec067`。
- FD SHA256：`c749df261bc12c9aba52fefb33688e68f91e0befce4da513e8708e120dfbb720`。
- trial：`4dd84d0a-d44f-4230-9747-5baae31b61be`；session：`0xffffaabcc96a520b`；未 claim/未发送。
- 固件提交：`07c9bf6c6c2bf924d9fb5c38d3231d024266adbb`。使用逐文件绑定工作树快照构建；提交发生在构建后，不称提交后重编。

## 当前实测边界

最近一次实测是已消费的 v13：设备自行返回 Android，三页定位 DisplayDxe+0x2b140 / ESR 0x96000047 / FAR 0x0aeb0004，与 v12 一致。恢复和原双分区/备份核验已通过。本轮没有刷新在线设备状态，没有消费 v14。

v14 参数静态路径未发现直接 ABI 错位；实际建表算法宿主重放可正确映射 VBIF。两项都不能替代现场值。新六页将提供故障寄存器、TTBR/TCR/SCTLR 及受门控的异常后 PAR 读写翻译结果，不保证修复或推进到正式 GOP。

共享主线只读，R027 冻结；24 份旧镜像/资格摘要保持。原厂 PE、v13 MMIO 范围、RAM/verified/分区未改。旧源码准入已过期，旧镜像本身保持。

用户当轮“可以上机”即录像和在场恢复就绪；届时核对精确资格/未消费、当前设备和备份/恢复，再仅一次临时 boot。六页各四秒，总停留 24 秒，失败短路保护保留；75 秒仅主机观察期限，不能当自动返回保证。不 flash/erase/改槽；无页不判成功。

详见 [v14 操作记录](operations/2026-10-28-oem-context-v14.md)、[报告](../reports/enuma-oem-context-v14-20261028.json)、[v13 实测](operations/2026-10-28-oem-v13-live-fault.md)。本地证据 `out/oem-context-20261028`。OEM 真实返回、全 DXE、正式 GOP、ConOut/BDS/输入和 XNU 实机启动仍未验收。
