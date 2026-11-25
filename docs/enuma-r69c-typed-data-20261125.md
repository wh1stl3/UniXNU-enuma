# enuma r69c typed Data 打包 — 2026-11-25

状态：主机打包及哈希 `self-checked`；后续已刷写 boot_b，未启动，设备效果尚未验证，见 `ufs-sm8250-r69c-flash-20261125.md`。

## r69b 与修复

- r69b 单次启动在 SystemOS、OS、SystemCryptex 挂载后报告 `offline scratch Data mount failed: 22`；完整观察见 `ufs-sm8250-r69b-device-20261125.md`。
- 构建集成记录指出 r69b 未启用 typed Data 分支，因而走 `/dev/md0` 路径；r69c 修正为 `XNU_NATIVE_RAM_BLOCK=1`，保留 Data UUID `62F1BC9E-4868-4CFF-BF7E-59AFCD474B4F`。这是 panic 22 的源码侧原因判断，尚未由 r69c 实机结果确认；见 `enuma-r69b-build-integration-20261125.md`。
- 本次只使用已有内核打包，不重新编译或独立验证该宏及其运行时行为。

## 打包及检查

- `.cache/r69c-package.sh` 的 REF 为 r69b、DEST 为 r69c；运行 exit 0。
- `out/ufs-sm8250-full-20261125-r69c/boot.img`：169951232 字节，SHA-256 `1387002a44053385d9c0a4159e90478fa3a3122e7a5c59923fb152bc9cc02c70`。
- `payload.img`：167772160 字节，SHA-256 `ba426e99d75efa0896511fba2238f7060cf39198f8af86f3a3809b11cd42a1cc`；其中 `Payloads/kernel.macho` 经 `mtype | sha256sum` 得 `2b4fc2d7483a6c73f30146fe3198c332bec697ac5a0e0ab706ad2ec8ec522bff`。
- 脚本断言 boot 参数、Android header cmdline、固件与 DTB、非内核 payload 成员与 r69b 相同，且内嵌内核与输入相同；manifest 字段名里的 `r66` 实际指本次 REF r69b。
- 本轮没有设备操作；打包成功不证明 Data 挂载或系统启动成功。
