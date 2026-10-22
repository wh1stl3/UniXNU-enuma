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

## 后续实施：已批准公开建仓

用户随后明确选择在 wh1stl3 下新建公开 UniXNU-enuma。已创建 origin=https://github.com/wh1stl3/UniXNU-enuma.git，main 首次推送包含 8aa2d95。前文“尚无远端”保留为核对时点的记录。

新增 .github/workflows/macos-xnu.yml，手动选择 preflight / bootstrap。固定 macos-15 与 /Applications/Xcode_16.4.app/Contents/Developer，实际运行必须核对 Xcode 16.4、iPhoneOS SDK 18.5；SDK 版本不是目标 iPadOS 版本，编译 deployment 为 iOS 17.0，donor 仍为 17.7.11。所选组合来自官方 runner 镜像清单：https://github.com/actions/runner-images/blob/main/images/macos/macos-15-arm64-Readme.md ，是否可用以实际运行报告为准。

preflight 从已锁 UniXNU 提交读取源/feeds，编译一个 arm64 freestanding 对象并保存环境证据。bootstrap 再用四个固定 Apple 参考提交运行真实 build-xnu-4k-baseline.sh 和 audit-xnu-kernel.py。所有设备 CONFIG_XNU 功能在该模式明确置 0；因此它是通用 4 KiB 构建环境验证，不能称为 enuma 平台内核，更不生成预链接/payload/boot 镜像。完整板级归档涉及 corecrypto、pthread、ArmDTPlatform、ArmCpu 等，仍需后续单独接通。

本板候选 defconfig 的 BOOT_PROGRESS 从 y 修正为 n：固定脚本明确要求 UFS/owner-root/Virtio/corecrypto 的组合，当前 UFS 已禁用，保留 y 会在配置检查阶段必然失败。本次未开启这些尚未审查的硬件路径，也未修改 board.toml 或 example 标记。

工作流仅有 contents:read，checkout 不保留凭据，只上传 out/ci/macos/evidence（日志/来源/SDK/可选通用基线）到短期 Actions artifact。设备镜像、备份、私有标识和上游整树不提交 Git；macOS 克隆及全部中间文件在本仓 out/ 下，与本机只读上游无关。实际 run 链接/结论将记录在 STATUS 和 reports 中。
