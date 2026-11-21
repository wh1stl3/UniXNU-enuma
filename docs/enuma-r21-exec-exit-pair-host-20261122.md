# enuma r21 exec/exit 配对主机候选（2026-11-22）

`self-checked`，未上机；独立 verifier 和 deep_reviewer 尚未复核。
候选位于 `out/ufs-sm8250-launchd-keystore-20261122-r21/`，不进入默认 recipe。

## 探针

生成副本 `self-check/build-final/source/bsd/kern/kern_exec.c` 中，
`exec_mach_imgact()` 成功路径 `goto done` 前、`set_proc_name()` 后：

```c
{
    char comm[17];
    int pid = proc_getpid(p);
    strlcpy(comm, p->p_comm, sizeof(comm));
    printf("enuma-exec: pid=%d comm=%s\n", pid, comm);
}
```

该点不经过 `badtoolate`；它表示镜像激活成功，并不保证后续 spawn 设置或
用户态执行成功。普通 exec 路径还涉及 shadow proc，配对必须按 PID 及时间判断。

生成副本 `bsd/kern/kern_exit.c` 的 `proc_prepareexit()` 开头、两个调用方释放
`proc_lock(p)` 后：

```c
if (!proc_is_shadow(p)) {
    char comm[17];
    int pid = proc_getpid(p);
    int status = rv;
    int sig = WIFSIGNALED(status) ? WTERMSIG(status) : 0;
    strlcpy(comm, p->p_comm, sizeof(comm));
    printf("enuma-exit: pid=%d st=%d sig=%d comm=%s\n",
        pid, status, sig, comm);
}
```

原 `proc_exit()` 尾部打印已删除：该处 `p` 可能已经被回收。
`p_comm` 最多记录 16 字节，长名称可能截断、不同名称可能同前缀；
`thread_terminate()` 路径调用 `proc_prepareexit(p, 0, TRUE)`，`st=0`
不意味着正常退出。探针仅拷贝局部变量，不新增全局缓冲。

| 观察 | 判读 |
|---|---|
| 相同 comm 多次 exec，中间有匹配 PID 的 exit | 支持重启循环；须排除同名进程、PID 复用和 exec 替换。 |
| 一次 exec 后窗口内无匹配 exit | 仅窗口内未见退出，不等于已证明存活；日志遗漏或探针遗漏也可造成。 |
| 有 exit 无匹配 exec | 可能创建失败或探针遗漏，须检查；也可能开始观察前已创建。 |

## 机械证据

`native-link.map` 中 exec/exit 格式串各一处；native 和 prelink 对应的
`_exec_mach_imgact` / `_proc_prepareexit` 反汇编中，各有一条通过
`adrp`+`add` 引用对应格式串并调用 `_printf` 的指令。两个镜像的调用点：
exec `0xfffffff00bd09008`，exit `0xfffffff00bd16998`；两个格式串各唯一。
日志在 `self-check/build-final/logs/disasm-{exec,prepareexit}.log` 和
`disasm-prelink-{exec,prepareexit}.log`。这是对应函数内计数，非全镜像引用扫描。

相对 r20，对象集合相同，仅 `kern_exec.o` 与 `kern_exit.o` 不同：
前者 SHA-256 `67f3b058209da04d6125a72d6f5db8a3437f9111678f5b56cb7712ca45d07490`，
后者 `2481cac19e4b7919e3099db51059f8d0fca40bdcb16c3bbe417e04e333eea64d`。
其余对象逐个 SHA-256 相等，打包脚本执行断言。

| r21 产物 | 字节 | SHA-256 |
|---|---:|---|
| native | 91,875,952 | `b505a024c6f8d226826ad56a6c6c0cec8884dc352c8b3f99dfd4e336adc6c28f` |
| FAT kernel / prelink | 124,719,104 | `5c24e268ad59309c08629e6b3a5a770386b364ae072e61052fa7581c02f887bd` |
| payload | 167,772,160 | `546ba82a1e7ae2b1427f76c86d91ec84df109345bf7019c41166364d7fcf03de` |
| boot | 169,951,232 | `cb02ded1039189582dfb1458a218068c93cdcee152151b4708353d0c2320c23f` |
| FAT ADT | 14,048 | `099dda97e8c01592cf9542b806b868ce098415ef9bab8ed7a01c8d03edd95059` |
| FAT scratch Data | 1,142,976 | `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470` |
| FAT unixnu.toml | 786 | `4508b87529d5169ffbb616de3fc5ee2eda25d36f7ae4a6fe6d18878a3018ce28` |

r20 的六项 manifest 文件逐个重算哈希和长度均相符；其中 boot 为
`579da83aee339da92b8071a87044d207155c2b33012618aadf27f323e7f1c0ed`，
payload 为 `b98dc66e0c40539c3e8caea9acdba747cdf9e4ac17b40d07767dd9fba609e3ab`。
六项与 r20 比较仅 kernel、payload、boot 不同；ADT、initrd、unixnu.toml
相同。沿用的 r6 ADT wrapper 在 payload 构造时注入 ADT，打包脚本回读并校验。
boot-args 与 r20 相同，Windows Git OpenSSL 重算两个版本 boot/payload 与上表一致。

本轮不重编内核；复用已编译 r21 对象进行打包，脚本退出 0。r21 打包脚本
继承 r20 的历史 kernel 元数据，仅替换 native/prelink 哈希并注明继承；
manifest 中其他历史 delta/符号/调用关系字段不构成 r21 独立复核证据。
运行时日志完整性、实际进程生命周期、服务存活、显示和持久化均未验证。
