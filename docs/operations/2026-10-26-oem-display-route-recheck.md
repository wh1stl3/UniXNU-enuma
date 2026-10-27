# D-310：原厂 DisplayDxe 路线卡点复核

用户要求检查第二条 GOP 路线。本轮仅离线读取现有源码、原始二进制、历史结果并重跑独立输出审计；无设备动作、无新候选、无提交推送。D309允许人工恢复的规则保持。

## 当前结论

原厂路线具备本机 DisplayDxe、CPRDxe 与 K81 面板资源，不能称没有可复用驱动或必须重写显示栈。尚未闭合的是原厂驱动在当前 Mu/BootShim 环境中的执行与初始化链。最强历史证据将嫌疑集中于 PE 调用区间，但没有具体故障函数或实际 EFI_STATUS；不能称已经确认 DisplayDxe 内部挂死。

| 事实 | 支持什么 | 不支持什么 |
| --- | --- | --- |
| S005 入口前 point20 自动返回，Android完成35.219秒 | 支持入口前路径可达 | 不唯一证明检查点命中或 PE 开始执行 |
| S006 直接 PE 返回后 point21 未观察到返回，75秒后人工恢复 | 提高构造器/主函数调用区间的嫌疑 | 不排除主动 Exit、异常、复位或观测路径问题 |
| S007 Exit 汇合 point22 同样未观察到返回，之后人工恢复核验通过 | 降低“正常 Exit 后仅后置控制器连接卡住”的优先级 | 仍不能确定哪个调用或硬件访问未完成 |
| 当前调度器发现函数查 FD Reserved/FD_Reserved，内存表没有两名称 | 这一特定来源无法发现 scheduler 指针并发布相应 HOB | 不证明所有 OEM 协议提供者缺失，也不证明超时根因 |
| 驱动 Kernel protocol/HOB 查询失败时可清线程标志并返回成功 | 缺 scheduler 不一定挂死；返回成功不等于面板初始化成功 | 不允许用空接口替代真正调度器 |
| EnableDisplayThread=0 的 S002 仍无可读结果且需人工恢复 | 单改线程开关未带来可观察改善 | 不证明所有调度/锁问题被排除，也不证明同步 SetMode 已调用 |

历史结果绑定 reports/enuma-system-transport-S005-result.json、S006-result.json、S007-result.json；原始报告中的当时恢复 pending 字样不覆盖其后独立恢复核验。所有旧镜像均 consumed，不重跑。

## 排除已经撤回的错误解释

- “两个未知 DEPEX GUID 阻止派发”：原厂 DisplayDxe 位于相关 FD APRIORI 零基32，Mu Dispatcher 将队列成员设为 Dependent=FALSE、Scheduled=TRUE。DEPEX 不能作为其不执行的充分解释；入队也不能证明实际已进入 PE。不得补空 GUID stub。
- “原始 XBL 没有完整显示资源”：早期误查裁剪工作树；原始 XBL 实际包含本机驱动和面板资源。
- “关显示线程即可完成同步初始化”：二进制分支直接避开 ThreadCreate/Resume，并不自动执行同步 SetMode；该方向已试过而未见改善。
- “缺标准 gDS/HOB 配置表”：当前 Mu 有正常安装来源，不能仅凭驱动构造器消费这些表就认定缺失。

## 本轮重新核验

命令（设备仓根）：

```powershell
python -B scripts/audit_display_handoff.py --tool-path out/reverse-tools --output out/oem-display-recheck-20261026/handoff-audit.json
```

实际用本机 Codex Python 执行，退出0。审计独立解析保存的 XBL 与 R014 FD，DisplayDxe 均为315392字节、SHA256 `6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425`；实际协议/HOB/线程调用和原 ABL/保存 DTB 静态契约检查通过。没有覆盖原 reports/enuma-display-handoff-audit.json。

当前源码仍有 GetXblHobAddresses 名称缺口，EnableDisplayThread 为0。原厂构造链先执行十个库构造器，再进主函数；关闭后面的显示线程不会跳过这十个构造器。这是静态执行顺序，不是十个构造器的运行结果。

## 下一步应取得的决定性信息

如重新推进原厂支线，应围绕目标实际映像记录真实 Boot Services 调用的服务名、返回状态及返回地址，首先区分构造链、协议/配置/HOB 消费与后续硬件初始化；避免继续增加只有黑屏/时间差的早停点。实际发生的未返回调用或明确失败状态，才决定适配哪一个真实接口。

现在128条 DXE 状态日志只在 Core 边界记录 StartImage，不能自动给出闭源 PE 内部调用；当前像素日志候选还明确排除了 DisplayDxe/CPRDxe，所以 S052 成功不能验收原厂路线，也不能直接拿该候选诊断它。新原厂取证候选须重新绑定模块选择、日志输出、恢复与范围，不能复用 S001..007 或 R024。

调度器来源、锁/事件 ABI、厂商服务及硬件初始化是按现有证据保留的嫌疑集合；目前没有足够依据说原厂路线一定更快或已经不可行。不修改内存表来凑名称，不造成功 stub，不补猜原厂指针。
