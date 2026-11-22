# enuma r23：软件 HID 占位（2026-11-22）

主机 `self-checked`，未上机。r23 用于检验 r22 未观察到 SpringBoard/backboardd
是否与缺 digitizer 有关，不是触摸驱动。

## 来源与接线

- [UniXNU/ShengHidInput@71a40e76daeae1bb4127546f96ffa7339c7a06ff](https://github.com/UniXNU/ShengHidInput/tree/71a40e76daeae1bb4127546f96ffa7339c7a06ff)，
  BSD-2-Clause-Patent。用 `git show` 取未修改的 `NativeHidInput.cpp`，许可证留在
  候选 `source/`。只在 r23 recipe 选入，不走会拉入 `ShengNovatekTouch` 的默认 catalog 依赖解析。
- 对照 [Ken-u/UniXNU-orangepi5@f96d273b526254d700bd42bfeadef0359a1d3c46](https://github.com/Ken-u/UniXNU-orangepi5/tree/f96d273b526254d700bd42bfeadef0359a1d3c46)，
  BSD-2-Clause-Patent：`package/Evb10Hid/NativeHidInput.cpp` 为其实现；
  `Evb10HidProbe.cpp` 提供零触点和延后注册；`LegacyDisplayProbe.cpp`
  加载原版 HID。enuma 复用接线方式，不复制板级自动 Home、触摸代码或时钟读取。
  ABI 检查来自 UniXNU 固定基座的 `scripts/build-sheng-hid-input.py`，
  Mach-O 延后构造参考 Orange Pi 5 的 `scripts/build-orangepi5-hid.py`，同许可证。
- 唯一新增参数 `sheng-touch-hid=1` 同时开启 publisher 和官方描述符中的
  TSP Touch Screen digitizer collection（usage page `0x0D`，usage `4`）。
  单个组合设备含键盘、consumer 报告描述及 TSP，不起 split 设备。
  `native_touch_*` globals 为 BSS 零值，触摸和按钮 sink 都不保存回调，
  `native_hid_input_requested()` 恒 false。不提交触点、按键或自动 Home，
  不走驱动的触点上报和 edge 改写路径。
- 仅在 r23 副本的 `load_init_program()` 内，Data 挂载成功后、现有 watchdog
  policy 之后、exec launchd 之前调用 publisher。此时已过常规 IOKit/BSD 注册边界，
  无需更早启动或绑定到显示探针。加载 r22 已预链接的原版 `IOHIDFamily` 和无代码的
  `IOHIDEventDriver` personality，针对原版 family 发布的 `IOHIDResource`
  软件服务匹配等待（超时参数 5 s），不伪造 provider。检查 `IOHIDDevice`
  运行时大小为 208，再 `preModLoad` → 手动构造 → `postModLoad` → init/attach/start。
  因组合描述符以键盘为首，匹配后将 digitizer 属性在 EventDriver 和其 interface
  写一次；`digitizer properties=1` 区分仅 device start 和属性写成功。

## 主机产物与差分

目录 `out/ufs-sm8250-launchd-hid-20261122-r23/`。基座
`693f5d9cae8a408dd18b39f3f9fdc4228c934241` 不动；构建前后上游 `main`
均为 `8542980d02b4d2cc5c32ee3542de1760b2562aac`。

| r23 文件 | 字节 | SHA-256 |
|---|---:|---|
| `objects/libShengHidInputStandin.a` | 442,280 | `61e12135a41a2752233d7ad701fedfb499bb838e813a2d7481091d30991a2e3d` |
| `objects/EnumaHidStandin.o` | 178,192 | `6476eee54d2852d47a62f412992c161302153f1675b34af4a93dce281f903d27` |
| `objects/NativeHidInput.o` | 257,400 | `a03a15cfe506f3e83ff50e98991a79a9ba754e64aed299b2c92d81edd606d348` |
| `objects/NativeHidInput.late.o` | 257,270 | `537f032122d77c4411d0a325128f207a0dea5de86037a0825007336abbd689fe` |
| `objects/hid-original-bindings.o` | 2,984 | `d6290d09b1830369a8b4f637ef73357a8c1272a8d7136a15fdc2c7f4a2be7d6b` |
| `objects/kern_exec.o` | 480,712 | `304bc5c75a2045082b537db57e5b154631e8ea4a7a9610fd65827da4b70f3ff2` |
| `native.macho` | 91,888,272 | `306b71f131c9814ea97e5daac7055546f1fc03327d8647ad8bb7426d8fe1f1a9` |
| `prelink.macho` | 124,731,392 | `edbb9422c9ae53f486aa540482aaa5f9b0b2489cc7428abfbbcfc76543ca1062` |
| `payload.img` | 167,772,160 | `72723451bd753ab40ad4ab999b68046addf7fbc8b495ff8be9da22ca2b8f3dba` |
| `boot.img` | 169,951,232 | `f82391886dea2a47915a51c6455b51924285dc3ff8e447adc768ea1775e0da1b` |

- 一处新增调用，重编 `kern_exec.o`（+72 B）；其余 1005 个 filelist 项不变，
  新增一个 force-load archive。native +12,320 B，prelink +12,288 B；
  两者均零 undefined（含 weak）。各有一个 `_load_init_program` →
  `_enuma_hid_standin_start`，在 watchdog hook 之后。`candidate-manifest.json`
  所列 6 个 HID 符号和 6 个格式/标识字符串各出现一次。
- 校核 207 个 HID vtable 槽、52 个原版绑定；原版 `IOHIDFamily` 的
  `__TEXT_EXEC` SHA-256 为 `7e4c5104814f2e773d5be13d092dec53ee44ba5a61a81264b229780406e86b72`。
  原版 `IOHIDDevice` 构造及调用边界一致；用 r22 的
  `IOService::handleClose(IOService *, IOOptionBits)` 头文件签名。
  延后对象无自动初始化 section、代码字节不变、metaclass 处于可写数据。
  原版预链接组件（含 codeless）及其指令哈希清单不变。
- 只换 FAT 中 `Payloads/kernel.macho` 与 `unixnu.toml`（新增参数，其余字段不变）。
  复用 r22 官方生成的 ADT 字节：包内读回 14,088 B，SHA-256
  `5f3ebeb6b29a9e47c7c314443dc3564db07caf830de5054e9bec0e5773f521d5`，
  `/chosen/darwinboot-memory-size=0xaa000000`（2720 MiB），
  `/defaults/sleep-disabled=1`；随机种子不重生成。trustcache 和 scratch Data 不变。
- `boot.img` 前缀只变 payload 派生的 header ID，FD、shim、Android DTB 相同。
  FAT 偏移 2,179,072，最终 boot 中读回的 FAT 哈希等于 `payload.img`。
  r22 8 个文件及其 1018 个固定链接输入构建前后哈希不变；r22 boot SHA-256
  `646e7d8dd2d1d3e4ae25d02c9b34cced7e1a1e7f20f34506cc9437b34fb360e7`。
  默认 series、默认配方、`UniXNU/` 和 ADT 未修改。

构建及 `porting-record.py check` 均 exit 0（后者检查 15 区）。复跑
（WSL Ubuntu-22.04 root；enuma 仓目录；相同冻结 r22/r21 输入，
`--out` 选全新目录；记录检查从 `UniXNU/` 运行）：

```sh
PATH=/home/wh1stl3/.local/bin:/opt/unixnu-linux/bin:/usr/bin:/bin \
  /home/wh1stl3/.local/bin/python3 -B scripts/build-enuma-r23-hid-standin.py \
  --hid-source out/r23-upstream/ShengHidInput --dtb /root/enuma-step10/inputs/enuma.dtb \
  --out out/ufs-sm8250-launchd-hid-20261122-r23-verify
python3 scripts/porting-record.py check --device ../enuma/UniXNU-enuma \
  --base origin/feat/step10-ramblock-probe
```

## 验收口径（未上机）

| 观察 | 判读 |
|---|---|
| `IOHIDResource=found`、`start=1`、`digitizer properties=1`，且观察到 SpringBoard | 支持 digitizer 是此前缺失的前提；同时记录 backboardd，不证明唯一因果或 GUI 可交互。 |
| 占位节点已发布且可匹配，但仍未观察到 SpringBoard | 本次不支持该假设，不排除其它前置；记录 backboardd 与匹配结果。 |
| 资源未发现、start 失败或 digitizer 属性未发布 | 实验前提未达到，不能用 SpringBoard 缺席否定假设。 |

占位节点可能让系统以为有实际内置输入设备，但不提供可用输入。
未验证 enuma 运行时资源发布、metaclass 注册、实际 IOKit / backboardd 匹配、
SpringBoard、图形输出或持久化。上机前需深审启动 hook；无独立 verifier 复跑。

## 改编代码的许可证

Copyright (c) 2026, UniXNU contributors. All rights reserved.
Copyright (c) 2026, Ken-u. All rights reserved.

SPDX-License-Identifier: BSD-2-Clause-Patent

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

Subject to the terms and conditions of this license, each copyright holder
and contributor hereby grants to those receiving rights under this license
a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable
(except for failure to satisfy the conditions of this license) patent
license to make, have made, use, offer to sell, sell, import, and otherwise
transfer this software, where such license applies only to those patent
claims, already acquired or hereafter acquired, licensable by such copyright
holder or contributor that are necessarily infringed by:

(a) their Contribution(s) (the licensed copyrights of copyright holders and
    non-copyrightable additions of contributors, in source or binary form)
    alone; or

(b) combination of their Contribution(s) with the work of authorship to
    which such Contribution(s) was added by such copyright holder or
    contributor, if, at the time the Contribution is added, such addition
    causes such combination to be necessarily infringed. The patent license
    shall not apply to any other combinations which include the
    Contribution.

Except as expressly stated above, no rights or licenses from any copyright
holder or contributor is granted under this license, whether expressly, by
implication, estoppel or otherwise.

DISCLAIMER

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
