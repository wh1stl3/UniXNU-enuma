# 官网文档页面清单

2026-10-22：中文 72 页逐页审阅；英文 72 页完成链接结构及关键技术内容交叉核对。全部 144 页 HTTP 200，两个指定入口可到达全部页面。

源码清单参考提交：`d704728a6df9d1eb113873dc1b57e87f6846e361`。该提交不是站点部署版本的证明；页面 HTML 各自摘要与 3836 条有向链接关系见 `reports/enuma-official-docs-audit.json`。

未递归抓取站外的 223 个链接，也未抓取站点静态资源或执行页面脚本。`sitemap.xml` 为 404，使用 VitePress 导航、页面链接和完整 Markdown 源清单交叉覆盖。

| 中文章节 | 页数 | 覆盖内容 |
| --- | ---: | --- |
| 首页 | 1 | 项目范围、入口 |
| 指南及构建 | 9 | 环境、构建、内核、启动、诊断、身份、Setup、userdata |
| 概念 | 5 | 启动链、负载、预链接、安全、userdata |
| 移植 | 5 | 总览、设备仓库、UEFI、设备树、bring-up |
| 驱动 | 7 | 分层、UEFI、XNU、kext、匹配、Novatek、Adreno |
| XNU | 4 | 源码、4 KiB、补丁、启动参数 |
| 设备 | 32 | 目录、sheng、无人值守及 29 个社区设备页 |
| 参考 | 7 | CLI、配置、启动配置、输出、QEMU、排错、术语 |
| 贡献 | 2 | 文档、仓库结构 |

## 全部中文页面与英文对应页

| 中文页面 | 英文对应页 |
| --- | --- |
| [UniXNU](https://unixnu.com/zh) | [English](https://unixnu.com/) |
| [构建](https://unixnu.com/zh/building) | [English](https://unixnu.com/building) |
| [启动链](https://unixnu.com/zh/concepts/boot-chain) | [English](https://unixnu.com/concepts/boot-chain) |
| [启动负载](https://unixnu.com/zh/concepts/payload) | [English](https://unixnu.com/concepts/payload) |
| [内核预链接](https://unixnu.com/zh/concepts/prelink) | [English](https://unixnu.com/concepts/prelink) |
| [完整性与启动策略](https://unixnu.com/zh/concepts/security) | [English](https://unixnu.com/concepts/security) |
| [userdata 布局](https://unixnu.com/zh/concepts/userdata) | [English](https://unixnu.com/concepts/userdata) |
| [文档站](https://unixnu.com/zh/contributing/documentation) | [English](https://unixnu.com/contributing/documentation) |
| [仓库布局](https://unixnu.com/zh/contributing/repository) | [English](https://unixnu.com/contributing/repository) |
| [支持的设备](https://unixnu.com/zh/devices) | [English](https://unixnu.com/devices) |
| [Redmi Note 14 Pro+ 5G（amethyst）](https://unixnu.com/zh/devices/amethyst) | [English](https://unixnu.com/devices/amethyst) |
| [一加 5（cheeseburger）](https://unixnu.com/zh/devices/cheeseburger) | [English](https://unixnu.com/devices/cheeseburger) |
| [小米 15（dada）](https://unixnu.com/zh/devices/dada) | [English](https://unixnu.com/devices/dada) |
| [Redmi 9A（dandelion）](https://unixnu.com/zh/devices/dandelion) | [English](https://unixnu.com/devices/dandelion) |
| [DroidVM 客户机（Gunyah 上的 crosvm）](https://unixnu.com/zh/devices/droidvm) | [English](https://unixnu.com/devices/droidvm) |
| [一加平板 2 Pro（erhai）](https://unixnu.com/zh/devices/erhai) | [English](https://unixnu.com/devices/erhai) |
| [一加 6T（fajita）](https://unixnu.com/zh/devices/fajita) | [English](https://unixnu.com/devices/fajita) |
| [小米 13（fuxi）](https://unixnu.com/zh/devices/fuxi) | [English](https://unixnu.com/devices/fuxi) |
| [一加 Ace 5（giulia）](https://unixnu.com/zh/devices/giulia) | [English](https://unixnu.com/devices/giulia) |
| [三星 Galaxy Tab A7 10.4（gta4l）](https://unixnu.com/zh/devices/gta4l) | [English](https://unixnu.com/devices/gta4l) |
| [OnePlus 7 Pro（guacamole）](https://unixnu.com/zh/devices/guacamole) | [English](https://unixnu.com/devices/guacamole) |
| [Redmi K40 Pro（haydn）](https://unixnu.com/zh/devices/haydn) | [English](https://unixnu.com/devices/haydn) |
| [一加 Ace 5 Pro（hummer）](https://unixnu.com/zh/devices/hummer) | [English](https://unixnu.com/devices/hummer) |
| [小米平板 5（nabu）](https://unixnu.com/zh/devices/nabu) | [English](https://unixnu.com/devices/nabu) |
| [小米 13 Pro（nuwa）](https://unixnu.com/zh/devices/nuwa) | [English](https://unixnu.com/devices/nuwa) |
| [努比亚红魔 8 Pro / 8 Pro+（nx729j）](https://unixnu.com/zh/devices/nx729j) | [English](https://unixnu.com/devices/nx729j) |
| [一加 13T（oneplus13t）](https://unixnu.com/zh/devices/oneplus13t) | [English](https://unixnu.com/devices/oneplus13t) |
| [OPPO Find X7 Ultra（PHY120）](https://unixnu.com/zh/devices/phy120) | [English](https://unixnu.com/devices/phy120) |
| [小米平板 8 Pro（piano）](https://unixnu.com/zh/devices/piano) | [English](https://unixnu.com/devices/piano) |
| [Redmi K30 5G（picasso）](https://unixnu.com/zh/devices/picasso) | [English](https://unixnu.com/devices/picasso) |
| [小米平板 6（pipa）](https://unixnu.com/zh/devices/pipa) | [English](https://unixnu.com/devices/pipa) |
| [Galaxy Z Fold3（q2q）](https://unixnu.com/zh/devices/q2q) | [English](https://unixnu.com/devices/q2q) |
| [QEMU virt](https://unixnu.com/zh/devices/qemu) | [English](https://unixnu.com/devices/qemu) |
| [Redmi K20 Pro / Mi 9T Pro（raphael）](https://unixnu.com/zh/devices/raphael) | [English](https://unixnu.com/devices/raphael) |
| [小米 6（sagit）](https://unixnu.com/zh/devices/sagit) | [English](https://unixnu.com/devices/sagit) |
| [小米平板 6S Pro（sheng）](https://unixnu.com/zh/devices/sheng) | [English](https://unixnu.com/devices/sheng) |
| [无人值守测试流程](https://unixnu.com/zh/devices/sheng-unattended-test) | [English](https://unixnu.com/devices/sheng-unattended-test) |
| [Redmi Note 10 Pro（sweet）](https://unixnu.com/zh/devices/sweet) | [English](https://unixnu.com/devices/sweet) |
| [小米平板 7 / POCO Pad X1（uke）](https://unixnu.com/zh/devices/uke) | [English](https://unixnu.com/devices/uke) |
| [Redmi K70（vermeer）](https://unixnu.com/zh/devices/vermeer) | [English](https://unixnu.com/devices/vermeer) |
| [Microsoft Surface Duo 2（zeta）](https://unixnu.com/zh/devices/zeta) | [English](https://unixnu.com/devices/zeta) |
| [设备树匹配](https://unixnu.com/zh/drivers/device-tree-matching) | [English](https://unixnu.com/drivers/device-tree-matching) |
| [kext 包](https://unixnu.com/zh/drivers/kexts) | [English](https://unixnu.com/drivers/kexts) |
| [Adreno 740 驱动](https://unixnu.com/zh/drivers/native-adreno) | [English](https://unixnu.com/drivers/native-adreno) |
| [Novatek NT36532E 触控驱动](https://unixnu.com/zh/drivers/native-novatek-touch) | [English](https://unixnu.com/drivers/native-novatek-touch) |
| [驱动分层](https://unixnu.com/zh/drivers/overview) | [English](https://unixnu.com/drivers/overview) |
| [UEFI 驱动](https://unixnu.com/zh/drivers/uefi-drivers) | [English](https://unixnu.com/drivers/uefi-drivers) |
| [XNU 驱动](https://unixnu.com/zh/drivers/xnu-drivers) | [English](https://unixnu.com/drivers/xnu-drivers) |
| [启动镜像](https://unixnu.com/zh/guide/boot) | [English](https://unixnu.com/guide/boot) |
| [构建内核](https://unixnu.com/zh/guide/build-kernel) | [English](https://unixnu.com/guide/build-kernel) |
| [调试与日志](https://unixnu.com/zh/guide/debugging) | [English](https://unixnu.com/guide/debugging) |
| [MobileGestalt 身份](https://unixnu.com/zh/guide/mobilegestalt) | [English](https://unixnu.com/guide/mobilegestalt) |
| [总览](https://unixnu.com/zh/guide/overview) | [English](https://unixnu.com/guide/overview) |
| [构建环境](https://unixnu.com/zh/guide/requirements) | [English](https://unixnu.com/guide/requirements) |
| [Skip Setup](https://unixnu.com/zh/guide/skip-setup) | [English](https://unixnu.com/guide/skip-setup) |
| [userdata 镜像](https://unixnu.com/zh/guide/userdata) | [English](https://unixnu.com/guide/userdata) |
| [移植总览](https://unixnu.com/zh/porting) | [English](https://unixnu.com/porting) |
| [bring-up 顺序](https://unixnu.com/zh/porting/bring-up) | [English](https://unixnu.com/porting/bring-up) |
| [设备仓库](https://unixnu.com/zh/porting/device-repository) | [English](https://unixnu.com/porting/device-repository) |
| [设备树](https://unixnu.com/zh/porting/device-tree) | [English](https://unixnu.com/porting/device-tree) |
| [UEFI 固件](https://unixnu.com/zh/porting/uefi-firmware) | [English](https://unixnu.com/porting/uefi-firmware) |
| [启动配置](https://unixnu.com/zh/reference/boot-configuration) | [English](https://unixnu.com/reference/boot-configuration) |
| [命令行](https://unixnu.com/zh/reference/cli) | [English](https://unixnu.com/reference/cli) |
| [设备配置](https://unixnu.com/zh/reference/configuration) | [English](https://unixnu.com/reference/configuration) |
| [术语表](https://unixnu.com/zh/reference/glossary) | [English](https://unixnu.com/reference/glossary) |
| [输出布局](https://unixnu.com/zh/reference/output-layout) | [English](https://unixnu.com/reference/output-layout) |
| [QEMU 测试](https://unixnu.com/zh/reference/qemu) | [English](https://unixnu.com/reference/qemu) |
| [故障排查](https://unixnu.com/zh/reference/troubleshooting) | [English](https://unixnu.com/reference/troubleshooting) |
| [启动参数](https://unixnu.com/zh/xnu/boot-arguments) | [English](https://unixnu.com/xnu/boot-arguments) |
| [4 KiB 页表](https://unixnu.com/zh/xnu/four-k-page-tables) | [English](https://unixnu.com/xnu/four-k-page-tables) |
| [补丁参考](https://unixnu.com/zh/xnu/patch-reference) | [English](https://unixnu.com/xnu/patch-reference) |
| [源码与补丁](https://unixnu.com/zh/xnu/source-and-patches) | [English](https://unixnu.com/xnu/source-and-patches) |

## 链接检查

- 未发现缺失的站内页面目标。
- 发现 1 个中文跨页锚点失效：`/zh/guide/mobilegestalt` 指向 `/zh/guide/requirements#target-ipsw`，目标中文页面使用 `目标-ipsw`。页面本身可打开，属于文档导航问题。
- 首页使用 VPContent 结构而非 main 标签，已单独复取并解析，未把空提取结果当作已审阅正文。

路线结论见 [官网路线核对](2026-10-22-official-docs-route-review.md)。
