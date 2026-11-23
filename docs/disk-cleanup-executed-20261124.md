# enuma out 清理记录（2026-11-24，self-checked）

## 规则覆盖

`docs/context-brief.md` 原规则为「大批量删除（>50 文件）由用户手动执行，agent 不做跨目录批量删除」。用户当轮原话：「授权你进行删除 可以覆盖这个规则」。覆盖范围仅本次 enuma `out/` 清理。

## 执行

- 脚本一：主控报告 749 项、释放 11.05 GiB；执行日志 `/tmp/enuma-cleanup-1-20261124.log` 的汇总为 749 项、11,868,337,156 逻辑字节，逻辑字节不等于磁盘实际释放量。脚本一后主控记录 UniXNU 无新增差异。
- 脚本二 dry-run：主控报告 48 目录、680 链接、9 缺失跳过。链接先解除、重扫，之后才删除目录；保留 `CLEANUP_CONFIRM=YES` 门禁。
- 脚本二 apply：已执行一次。宿主工具错误地以 1 秒超时启动，报告 exit 143；WSL 子进程随后运行结束，不能把 143 当成脚本退出码。日志 `/tmp/enuma-cleanup-2-apply-20261124.log` 无最终汇总，未重试，脚本真实退出码未知。清单 48 项中 36 项现不存在、12 项仍存在；dry-run 时已有 9 项缺失，36 不是本次删除成功数。

## 事后核验

- 脚本一之后及脚本二进程结束后，UniXNU `status --porcelain` 与 `/tmp/enuma-cleanup-upstream-baseline-20261124.txt` diff 均为空。
- `_retained-signing` 6977 文件、`_retained-audit-docs` 80 文件、`_retained-images` 4 文件；r57 备份 SHA-256 `e669e3bdf2f7f5315d9eb28e1231bdd02fe5f6245c2a961b88e0fa1ebf071169`。
- `out` 顶层目录 196 个；`df -B1 /mnt/d` 可用 380,625,170,432 字节。
- 运行中的 `du -sb out` 因并发删除报告目录不存在、exit 1，不作为最终结果；清理前两脚本总 df 基线未提供。
- 提交前记录检查改用 `/home/wh1stl3/.local/bin/python3`：exit 0，24 structured areas checked；此前系统 Python 因缺少 `tomllib` 失败。
