# 构建环境与远端状态

2026-10-22 核对：本仓尚无 origin，也没有 .github/workflows；GitHub 当前账号为 wh1stl3。只读参考仓 UniXNU-nuwa 的 origin 是 https://github.com/wh1stl3/UniXNU-nuwa ，可见性 PUBLIC。查询 wh1stl3/UniXNU-enuma 未找到仓库。本轮没有创建远端、推送代码或触发 Actions。

本地适配不依赖远端，但远端是代码备份、交接和托管 CI 的必要配套。不能把目前的本地固件构建描述为已完成远端 CI。

| 环节 | 已核对的环境要求 | 本仓状态 |
| --- | --- | --- |
| BootShim / Mu UEFI / SEC-DXE 诊断 | 当前固定编译链可在 WSL Ubuntu-22.04 构建 | 已实际构建并测试若干定时复位候选 |
| Python 输入审计和 boot v3 往返 | 当前测试使用 Windows Python；部分配置含 Windows 源路径 | 30 项通过；不可直接把当前路径搬到 runner |
| XNU 10063.141.1 的现有 UniXNU 构建链 | Xcode、iPhoneOS SDK、Darwin 工具；适合 macOS runner 或自有 Mac | 尚未建立 enuma 的 macOS 作业，未完成本板内核链接/预链接 |
| 手机 USB / fastboot / ADB | 当前连接设备的本地主机 | GitHub 托管 runner 不承担本机 USB 测试 |

依据固定 UniXNU 75bc13dd：scripts/unixnu/kernel.py 的 build() 明确检查 xcodebuild，调用 scripts/build-xnu-4k-baseline.sh；后者使用 ditto、Apple SDK 及 XNU 构建工具。现有脚本还把中间文件写在其源码树下，因此 runner 应在独立可写工作区取固定提交，不能在本机只读上游目录直接运行。

nuwa 只有 .github/workflows/firmware-candidate.yml，runs-on 为 ubuntu-24.04；这不是 macOS 内核流水线，不能照搬成 enuma 的 XNU 构建证据。

后续应建立 enuma 自身远端，并分别设置 Linux 固件任务和 macOS 内核任务。macOS 作业先验证固定 UniXNU/XNU 提交、Xcode 与 iPhoneOS SDK 的实际版本，再构建 enuma 配置，保存编译日志、符号/链接审计和产物摘要。IPSW 与设备备份不提交 Git；donor 组件从已固定的版本取得并核对。board.toml 的 archives / kernel.prelink 尚未闭合，不能仅有绿色的环境检查便宣称完成内核构建。

GitHub runner 的 macOS 标签、架构和软件会更新，应在实施时核对并记录实际镜像版本，不盲用 macos-latest。官方说明：https://docs.github.com/en/actions/reference/runners/github-hosted-runners 。本轮只核对环境要求，未选择已验证的 macOS/Xcode 组合。
