# v12实测：故障推进到DisplayDxe VBIF写入

2026-10-28 v12实测完成：原单次trial已消费，首次fastboot boot在30秒传输超时，用户确认仍在FASTBOOT且未按键；随后用户明确授权“你可以自行回到Android并重跑v12”。绑定设备经host fastboot reboot返回Android，身份/root/A槽/解锁及原分区、备份摘要核验通过。未把该次传输超时称固件故障。

同一精确v12镜像另记retry1，保留原qualification及消费账本，未伪造新固件trial/session。原生Windows派生运行器保留原资格/来源/身份/备份门禁，新增独占retry1账本，保存超时部分输出；没有改写绑定源码。重跑Sending/Booting均OKAY，约0.35秒，之后设备自行回Android，独立恢复与原分区/备份核验再次通过。无flash/erase/改槽。两次尝试分别留证；传输异常原因尚未确定，原生成功不证明WSL就是根因。

26.074867秒视频已落地，SHA256 42542b9e282543a7143ada13137dd55c8f5ce695b7a84e40d8e2b472420aad40。独立读取6/12/21秒三页，清晰无待确认字符，session 0x509d1d695c7e0fdc与精确镜像一致。原媒体只留Media-enuma/OEM-dispcc-v12-20261028-9da1688c。

## 新故障与进度

- PC 0x9a6ff140，ESR 0x96000047，FAR 0x0aeb0004，LR 0x9a6ff120。
- E12唯一归属：base 0x9a6d4000，RVA 0x2b140，size 0x4d000；E13 GUID 4138022f-06c7-4f79-9c94-7e33b511a4e7，与本FD原厂DisplayDxe唯一匹配。
- 原PE摘要6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425；实际指令0xb8154128，即 `stur w8,[x9,#-172]`。ESR为同EL data abort，WnR=1，DFSC=7（L3翻译故障），FnV=0；宽度由实际指令确定为32位。
- 本机FDT的mdss_mdp节点明确vbif_phys=0x0aeb0000/0x2008，故障为VBIF+4。构建映射Display MDP只到0x0ae85000，无描述符覆盖本次FAR。
- LR是本函数内BL到0x2b398后的位置；helper返回后才发生写故障。不能用这个LR声称构造器/GOP方法的上层调用阶段已经确定。

相较v11的ClockDxe+0x11d58读取DISP_CC故障，本轮实际到达原厂DisplayDxe的VBIF写操作，是推进证据；仍未证明OEM返回、完整DXE、生产GOP、ConOut或BDS成功。未采集实时页表，运行中修改仍不能彻底排除。

## 下一步

首先审查本机FDT对应VBIF最小页对齐映射0x0aeb0000/0x3000及设备属性，核对真实PE访问和相邻显示资源（regdma、sid、DSI/PHY）映射覆盖，避免只追单个字节或任意扩大整个外设空间。候选尚未制作，不自动追加实机。新补丁仍需LF检查、完整构建、最终SEC/FD核对与新资格。R027及旧镜像冻结，共享主线只读。

用户当轮“可以上机”今后即表示正在录像且在场可恢复，不重复确认；仍做即时设备/备份与精确候选核验。媒体仅有无法辨认且影响结论的字符才询问。文档最后统一发布，网络不阻塞本地工作。

证据：reports/enuma-oem-dispcc-v12-live-20261028.json；本地out/oem-dispcc-live-20261028。镜像SHA256 a14b999f39c590b1c0a43ea3f4cdb560396d713c03b5641d41c4f40fa6797e5c，trial 9da1688c-96a7-4adf-9774-f4661f5a5d13，原尝试及明确授权retry1均已结束。

公开资料与本机资源逐项覆盖审查已完成，见[VBIF公开源码研究](operations/2026-10-28-oem-vbif-public-research.md)。已确认VBIF+4为CLKON；DSI0/1、REGDMA、SID等也有静态映射缺口，下一版先查原厂PE访问，再逐项补齐，避免只追一个故障字节。
