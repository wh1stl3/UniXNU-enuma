# enuma 会话交接 — 2026-11-25

- 最新 r66 + IPC 单次观察、审查及证据边界：[观察记录](ufs-sm8250-r66-ipc-device-20261125.md)；离线封装：[记录](enuma-r66-ipc-20261125.md)。`self-checked`，阶段不提升，GUI 未验收。
- 本轮授权及 claim 已消耗，禁止访问、删除或重放；新设备动作须另获授权。
- 下一步先离线调查 AX lookup 注册者；请求者名称截断未知，现无可确认注册者结果。不得据 IPC 总数差推断未回复数量、launchd 对 routine 800 的收发或 Mach `msgh_id`。
- 未跟踪 `docs/enuma-r69d-data-stage-20261125.md` 是独立 r69d 离线打包记录，本轮未复核其产物、不混入 IPC 更正；保留供后续核实后单独入库。未跟踪 `scripts/build-kernel-local.sh`、`scripts/clean-out-20261125.sh`、`scripts/compile-kern-exec-20261125.py`、`scripts/fix-and-compile-20261125.py`、`scripts/hook-check-20261125.py`、`scripts/inject-hooks-and-rebuild.py` 为既有构建、清理或源码操作脚本，未经本轮审验，保留未执行、未提交。其他仓保持原样。
