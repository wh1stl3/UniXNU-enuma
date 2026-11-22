# enuma 显示 provider 溯源裁定

本次只裁决显示 provider 这一项，其余组件来源未查。状态：`self-checked`，
静态内容比较，未构建、未上机。

## sheng 换类提交

本地 `UniXNU/UniXNU-sheng` 镜像对 `*LegacyDisplayProbe*` 分别做
`git log --all -S 'new IOService'` 和 `-S 'new IOPlatformDevice'`：
两次换类的提交对象分别是 `0ebf192adac51ad951c3afb7b375fd8c6c5930b4`
和 `40cc031827fba9e7ef6c71d8512499b4b8a32327`；后者的 `-S` 结果另有
`fb2d4ed` 初始导入，不是这次换类。

两个换类对象是**同一个代码改动的两份历史对象**，不是两个不同文件、
也不是两个相继的修复：二者均改 `package/LegacyDisplayProbe.cpp`，
该文件的父版本 blob 都是 `09c49c40c432412b0b7f362dd0305ab4713b2b48`，
修改后 blob 都是 `23349601e3896403d114243fc76b477bf805bb86`；
整棵父树均为 `272bb1ad00fbebceedd97ff6cca7745cf0f01566`，
改后树均为 `c45b1a5e5a11ce42ec0dab2e8cf96d16cf18cdea`，
但父 commit 分别为 `197106bcd703bcf4124d3cf132ae6e48e9f3a503`
与 `c6aa5cb7d5fd31db09e672769d082a84d2b54c93`。
两份该文件 diff 的 `git patch-id --stable` 都是
`521cc11bd81efa0b3deda1eef20aa05e05609e3b`。
指定的 sheng `c8f92b20` 分支祖先链使用 `40cc031`；`0ebf192` 是另一
历史对象。两份报告各引用其中一个 hash 并不构成代码引用错误；若称 hash
在全历史中唯一或把两者当成两次不同修改，才是错误。
两者均为 `IOPlatformDevice` → `IOService`，原注释指出
`IOPlatformDevice::compareName` 期待 platform expert 而非 resource provider。

## enuma 内容比对

以当前分支 `40cc031^` 与 `40cc031` 的
`package/LegacyDisplayProbe.cpp`，比较历史候选
`out/enuma-gop-legacy-20261114-r2/package/EnumaLegacyDisplay.cpp`：
WSL `diff -u ... | wc -l` 分别为 **748 行（改前）**、**759 行（改后）**；
两份上游文件分别为 585 和 596 行，enuma 为 182 行。按上述 blob 内容，
用 `0ebf192^` / `0ebf192` 会得到同一对上游文件。

* nub 创建：enuma 与改前一样使用 `IOPlatformDevice`，改后用 `IOService`。
* parent / 资源：三者均 attach/start 到 resource service，并设 framebuffer 内存。
* DT：均可设 `device_type=display-subsystem`、挂 `/arm-io`；enuma 必须成功，
  sheng 则受 `offline-legacy-phase=4` 门控，名称亦不同。
* 次序：sheng display 为 probe → attach → start；enuma 为 attach → probe →
  start → 显式 display `registerService()`。sheng 另有 phase 3 presenter。

**裁定：独立演化。**enuma 的 nub 类更像改前，但两次完整 diff 都远大于
enuma 文件自身，且流程、门控和注册次序不同；少 11 行不足以确定抄入
commit 或历史先后。现有比较不证明 r40 实际链接了该候选，也不证明 enuma
是从 sheng 改前版本抄入；所以是否「漏抄」该修复无法判定。
