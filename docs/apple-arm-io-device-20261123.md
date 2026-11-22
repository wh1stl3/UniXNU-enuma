# r39 Apple ARM IO provider: offline evidence

Status: self-checked, static inspection only. The r39 screen text below is
parent-provided transcription, not independently read from an image.

## Crucial spelling

The supplied wait dictionary says `AppleARMIODDevice` (two consecutive D
characters after IO); the supplied log uses the same spelling. The actual r39
prelinked binary says `%s: provider was not AppleARMIODevice.` (one D).
These are different class names. The exact wait spelling needs confirmation
against the original image before attributing it to a real class or client.

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
complete dictionary and the caller/class spelling before proposing any code
change; no provider change is justified by current evidence.

The requested sheng/sirius/Orange Pi 5 provider comparison was not established;
no claim that those systems pass this same wait is supported here.
