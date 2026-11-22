# offline-legacy-unit-scale 源码调查

状态：self-checked，纯静态分析；无构建、无设备操作。来源为本地 Git 对象 `UniXNU-sheng@c8f92b208068eeaa4cd2b0f592671f04ee70076e`，不是 nuwa 设备数据的移植。

## 解析和作用

全树 Git grep 四种拼写，参数配置位于 sheng `board.toml:61,185,243`，实际解析位于 `package/LegacyDisplayProbe.cpp:437,455-470` 的 `native_legacy_gop_mapping_observed`：

```cpp
unsigned enabled=0;PE_parse_boot_argn("offline-legacy-unit-scale",&enabled,sizeof(enabled));
if(!enabled)return true;
// ... checks ...
unitScaleChosen=IORegistryEntry::fromPath("/chosen",gIODTPlane);
if(!unitScaleChosen || !publishOrMatchWord(unitScaleChosen,"display-scale",enabled,unitScaleAdded) ||
   !publishOrMatchWord(unitScaleChosen,"display-rotation",video.v_rotate,unitRotationAdded)) {
```

源码 `:460-467` 明确记载它是 UI 逻辑点与实际扫描像素之比：2 表示每轴 2 个实际像素每逻辑点；仅发布 scale，扫描拷贝仍逐实际像素对应，不是 swap 重采样、面板密度或诊断专用参数。实际下游消费者和 enuma 运行时效果未在此确认。

`LegacyDisplayProbe.cpp:43-51` 以 4 字节 `OSData` 写入 `/chosen`；已有属性必须类型、长度、值完全匹配，不能覆盖冲突值。`:462-464` 要求 scale 1..3、phase 4、无重复设置、视频几何和映射物理地址一致且旋转为零；`:473-482` 回读验证两属性。`:36-41,725,732` 在启动成功时保留新属性，失败只撤销本次新增属性；原有匹配属性不删除。启用后失败会令回调返回 false，不只是诊断。

## enuma 对照

r5 冻结归档 `out/enuma-gop-production-20261114-r5/display/source/NativeLegacyDisplay.cpp:852` 从 `startHardware` 调用同名回调；板级 `out/enuma-gop-production-20261114-r5/patch-replay/out/enuma-gop-legacy-20261114-r2/package/EnumaLegacyDisplay.cpp:139-148` 的回调目前只校验映射并返回。`:108-115` 是 `displayObject->start(nub)` 后注册服务；因此为保证与 sheng 同一时序，应在板级映射回调通过校验之后、返回之前设置 `/chosen`，而非等 `start` 返回后才写服务属性。要等价还须保留已有值冲突处理、旋转属性、失败回滚及 phase 等门禁；不是单纯无条件加一个服务属性。该静态可行性不证明冻结归档可修改部署，亦不证明现有 r35 ADT 值已被下游消费。

可选 sirius 对照：`HuajiFruit/UniXNU-sirius@ac0c9004` 的 `drivers/GopFramebuffer/NativeLegacyDisplay.cpp` 经 raw 源码检查未解析此参数，`startHardware` 仍调用 `native_legacy_gop_mapping_observed`；仅检查此文件，不能据此断言 sirius 全仓无解析器。
