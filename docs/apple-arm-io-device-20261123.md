# r39 Apple ARM IO provider: offline evidence

Status: self-checked, static inspection only. The r39 screen text below is
parent-provided transcription, not independently read from an image.

## Crucial spelling

Correction: the user confirmed the screen's wait dictionary names
`AppleARMIODevice`. The earlier parent transcription added a spurious D;
the previously stated need to confirm that spelling is withdrawn. The actual
r39 prelinked binary says `%s: provider was not AppleARMIODevice.`.

From the repository root, with WSL GNU grep and llvm-nm:

```
for f in out/ufs-sm8250-launchd-aksid-20261123-r39/{native.macho,prelink.macho,kernel.macho.adt}; do
  for s in AppleARMIODDevice AppleARMIODevice AppleARMIO ARMIODevice arm-io; do
    printf '%s: ' "$s"; grep -aob "$s" "$f" | wc -l
  done
done
```

| file | AppleARMIODDevice | AppleARMIODevice | AppleARMIO | ARMIODevice | arm-io |
|---|---:|---:|---:|---:|---:|
| native.macho | 0 | 0 | 0 | 0 | 7 |
| prelink.macho | 0 | 11 | 15 | 11 | 17 |
| kernel.macho.adt | 0 | 0 | 0 | 0 | 2 |

`llvm-nm prelink.macho | grep -Ei 'AppleARMIODDevice|AppleARMIO|ARMIODevice'`
and the same command on native both produce zero lines. These files contain
other symbols, but their absence here is not proof that the prelinked kext
has no implementation: symbols can be stripped. `strings prelink.macho |
grep -F 'provider was not Apple'` returns `%s: provider was not
AppleARMIODevice.`; strings also include `AppleARMIO`, `AppleARMIO.cpp`,
`AppleARMIODevice`, `site.AppleARMIO`, `site.AppleARMIODevice`. Prelink
metadata contains `AppleARMPlatform.kext` and multiple personalities with
`IOProviderClass=AppleARMIODevice` depending on `com.apple.driver.AppleARMPlatform`.
This supports the AppleARMPlatform association, not proof of an exported,
constructible class or its runtime registration.

## Device tree and provider

The r39 ADT byte scan finds `arm-io` twice; it is not a parsed node inventory.
The corresponding native image has `/arm-io` and required-node diagnostics.
Neither establishes a published AppleARMIODevice. The platform driver creation
path and required properties remain unverified; an ADT node alone is not proof
of any IOService instance.

The historical frozen source
`out/enuma-gop-legacy-20261114-r2/package/EnumaLegacyDisplay.cpp:63-115`
allocates `new IOPlatformDevice` (:71,84), initializes it and a framebuffer
memory range (:85-91), names it `EnumaGOPFramebuffer`, attaches and starts it
under the resource service (:76,92), adds `device_type` OSData
`display-subsystem` (:97-100), names it `enuma-gop-display` in the device-tree
plane and attaches that to `/arm-io` (:95,103-105), then attaches, probes and
starts the display instance and registers the display (:105-115). The nub is
an `IOPlatformDevice`, not an AppleARMIODevice; its DT-plane parent does not
change its C++ metaclass. r39 build script :74-86 substitutes an r34 display
archive; equivalence of that archive to this historical source was not checked.
The parent-provided non-IOD log is consistent with that source, not a proof of
the r39 nub's full runtime properties.

## Matching and change assessment

XNU `iokit/Kernel/IOService.cpp:7619-7629` matches IOProviderClass with
`metaCast` normally, but has an explicit IOCompatibilityProperties/IOClass
exception (:7610-7625). Merely setting ordinary `IOClass` or
`IOProviderClass` properties on the nub does not make it that C++ type, and
does not make the framebuffer's actual dynamic cast succeed. The compatibility
exception has not been shown to apply to this query; using it to spoof a type
could bind an inappropriate client and is not recommended.

`AppleARMIODevice` is present as strings and personality references, not
established as a linkable and safely instantiable class; a hypothetical
constructor, `AppleARMIO::start` creation, resource semantics and required
properties have not been verified. Do not substitute a fabricated provider.
The exact waited-for client, remaining dictionary fields, and its relation to
display or SpringBoard are unknown. The non-IOD branch alone does not prove
the wait is blocking the GUI. The smallest justified action is to verify the
complete dictionary and the caller before proposing any code
change; no provider change is justified by current evidence.

## Follow-up: load, allocation and comparisons

`llvm-objdump --macho --private-headers` on r39 `prelink.macho` shows
`__PRELINK_TEXT` at VM `0xfffffff00427c000`, file offset 91910144, and
`__PRELINK_INFO,__info` at file offset 124268544. The AppleARMPlatform
metadata dictionary at file offset 124281545 contains:

```
CFBundleIdentifier           com.apple.driver.AppleARMPlatform
CFBundleVersion              1.0.2
_PrelinkExecutableLoadAddr   0xfffffff004286080
_PrelinkExecutableSourceAddr 0xfffffff004286080
_PrelinkExecutableSize       0xfc2b
_PrelinkKmodInfo             0xfffffff006add500
_PrelinkBundlePath            /System/Library/Extensions/AppleARMPlatform.kext
```

The executable address falls inside `__PRELINK_TEXT`; `llvm-objdump
--macho --section-headers` also shows `__mod_init_func` sections, but these
are not attributed to AppleARMPlatform. This establishes an executable and
kmod metadata in the artifact, not that the kext was started or that this
class's metaclass was registered. Searching r39's build logs for
`AppleARMPlatform` returned no lines; those are host build logs, not a full
device startup log. Neither runtime load state nor publication of an instance
is established. A waiting service match cannot distinguish an unregistered
class from a registered class with no matching published service.

In the local XNU source, `libkern/c++/OSMetaClass.cpp:1285-1297,1314-1319`,
`allocClassWithName` looks up the metaclass and invokes `meta->alloc()`;
absence or a failed allocation returns null. The r39 symbol scan and class-name
strings do not identify a usable metaclass table entry, allocator implementation,
or runtime registration. The actual AppleARMPlatform implementation was not
found in inspected sources. Thus the `AppleARMIODevice` allocation result,
its abstract/concrete status, caller access, initialization, and required
`reg`/interrupts/parent resources are unknown; neither the existence nor
necessity of those specific properties is established.

Pinned public source comparisons (BSD-2-Clause-Patent on the cited files):

* [UniXNU/UniXNU-sheng@5ae8b4876a378a5104330a5ae514ec9d6deae373,
  package/LegacyDisplayProbe.cpp:663-707](https://github.com/UniXNU/UniXNU-sheng/blob/5ae8b4876a378a5104330a5ae514ec9d6deae373/package/LegacyDisplayProbe.cpp#L663-L707):
  `new IOService` (:666), framebuffer memory (:673), then manually attaches
  and starts the display (:706-707); the comment explains why it uses a
  plain service rather than IOPlatformDevice under the resource service.
* [HuajiFruit/UniXNU-sirius@ac0c900485f3c0cd18de9707579a1cdcd3365503,
  package/LegacyDisplayProbe.cpp:605-652](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/package/LegacyDisplayProbe.cpp#L605-L652):
  `new IOPlatformDevice` (:605), attaches and starts display (:649-652).
* [Ken-u/UniXNU-orangepi5@729ba25f4d67225ff3853ba1e435b95af97e59e3,
  package/LegacyDisplayProbe.cpp:836-868](https://github.com/Ken-u/UniXNU-orangepi5/blob/729ba25f4d67225ff3853ba1e435b95af97e59e3/package/LegacyDisplayProbe.cpp#L836-L868):
  `new IOPlatformDevice` (:836), attaches and starts display (:867-868).

These manually attached display paths do not themselves require matching an
AppleARMIODevice before calling display start. They do not establish that the
unknown r39 waiter is a display client, nor that an equivalent waiter never
appears on those devices. The separate Orange Pi device record at that pinned
revision reports SpringBoard and scanout; the Sirius record reports display
registration and black frames. Neither explains the identity of r39's waiter.

If allocation cannot be used, a targeted alternative is to change the
identified waiter's match only if its implementation can safely consume the
existing service and its full matching constraints are known. That is a
conditional possibility, not an established fix: a client may depend on
AppleARMIODevice methods or real hardware semantics. Merely publishing a
generic provider or changing its ordinary class properties will not satisfy
the normal class match. No fake resources or class spoofing are justified.
