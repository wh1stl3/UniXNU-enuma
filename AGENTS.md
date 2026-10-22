# UniXNU-enuma 工作约定

目标：以 UniXNU 为底座，让小米平板 5 Pro 5G（enuma / SM8250 系列）运行 **iPadOS 17.7.11**。用户于 2026-10-22 选择该版本；不是 nuwa 的 iPhone/iOS16 路线。

## 目录与只读边界

- `D:\Code\UniXNU-enuma` 为本任务唯一工作仓库。
- `D:\Code\UniXNU-nuwa` 只读参考，且有其他会话工作；不得改文件、提交或影响其 CI。
- `D:\Code\PortingiOS`、`D:\Code\PortingiOSWithUniXNU` 及其中上游源码全部只读。
- 上游源码按固定提交和本地路径引用，不整棵复制进设备仓。WSL 路径大小写须保持真实名称。
- 所有工具输出显式指向本仓 `out/`，不得使用上游默认输出目录。`local.toml` 不提交。

## 版本管理（沿用 UniXNU-nuwa）

- 分支 `main`，每个里程碑一个提交，不攒大提交。
- 格式：`[unixnu-enuma][<area>] <一句话结论>`，正文包含 `[Change]`、`[Evidence]`、`[Risk]`。
- area：docs / build / kernel / firmware / loader / device。
- 不提交构建产物、上游源码树、DTB 原件、凭据、设备序列号或超过约 10 MB 的二进制；实测文本证据经敏感信息检查后提交。
- 不强推、不跳过 hooks、不改写已推送历史。远端发布状态与本地提交分开记录。

## 硬停四类

以下动作先写 `docs/NEED-REVIEW.md` 后停下等确认。每项写编号、背景、至少两个候选及代价、推荐理由、最小批准范围：

1. 修改任何 `bringup-plan.json` / `board.toml` 中内存大小或基址字段；
2. `fastboot boot` 自制镜像、flash、erase 或改槽位；
3. 新建或重写任何诊断 / 固件镜像；
4. 把任何 `*_verified` 置为 `true`。

历史资料中的验证标记只是来源事实，不等于本仓已验证或获得新的执行授权。旧仓单次授权不得重复使用。

## 人工与设备

- 只差本人按键：记 `docs/PENDING-HUMAN.md`，继续独立工作。
- 会改变设备内容且必须人在场：写 `docs/NEED-HUMAN.md` 并停。
- 恢复操作只在已有授权范围内执行，结束必须回 Android 并确认 `sys.boot_completed=1`。
- 设备动作必须明确选定 enuma，不能把同时连接的 nuwa 当成目标。

## 交接五件套

- `docs/STATUS.md`：当前唯一真相，每里程碑全文重写，只保留有效结论、下一步和限制。
- `docs/WORKLOG.md`：只追加，时间 · 结论 · 提交号 · 证据路径；新提交号在后一条记录，避免自引用。
- `docs/DECISIONS.md`：D-xxx 决策、来源和证据，不删除，被取代时标记 superseded。
- `docs/NEED-REVIEW.md`：待决项与批准范围，批准后记录 approved。
- `docs/PENDING-HUMAN.md`：仅人的按键/在场待办。
- 长篇分析放 `docs/operations/`；新会话依次读 AGENTS、STATUS、DECISIONS、NEED-REVIEW。

## 证据与驱动复用

- 固定措辞：静态检查通过 < QEMU 执行通过 < 实机通过，三者不能互换。
- 结论必须有命令、文件行号、日志或提交；未知项写未验证/TODO。
- 上游更新先 diff，跟进另开提交。固定仓库、提交、文件哈希、许可和依赖。
- 优先复用真实通用实现及同 SoC 来源，不使用空实现冒充驱动。
- enuma 不是 elish/nabu/sheng；SM8250 不是 SM8550。MMIO、IRQ、面板、触控、电源、GPU、UFS PHY 和 SMMU 必须逐项核对。
- iPadOS 身份由匹配的 IPSW、BuildIdentity、ADT 产品节点和用户态共同决定。固定版本 sheng 生成器的 `ipad_identity` 同时控制产品节点和安全属性，不能当成独立的 OS 选择器，也不能说它只控制激活；新工具须按自身实现审查。
