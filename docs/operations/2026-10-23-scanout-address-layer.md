# splash源地址层

固件17aa47a，R-004映射不变。新增step9只读八个SRC0_ADDR，遇到splash区间[0x9c000000,0x9e300000)便返回，最多八读，不读几何或格式。

40个host用例/对象、既有240 GOP检查通过；同源对照step3和step9全链接打包审计通过，四bundle负例/workspace通过。实际step9 DLL/map和反汇编已归档，读循环RVA0x1308..0x132c，唯一寄存器读取RVA0x131c；不是硬件执行轨迹。

22:58:05对照ADB15.863秒/核验31.446秒。23:02:06 step9 ADB16.936秒/核验29.136秒。用户分别确认无按键，两次Android/root/原摘要通过。短返回支持至少一个源地址字段在splash范围，但不是数值快照、唯一性、活动管线、完整物理地址或写屏范围验证。结果不是硬停；继续step10拆分格式/压缩，不先假设完整几何。

证据reports/enuma-scanout-address-device.json和enuma-scanout-address-bundle.json；原始截图/日志/产物仅out。后续主机报告可能由下一源码阶段更新，不将新阶段检查冒充旧镜像运行证明。
