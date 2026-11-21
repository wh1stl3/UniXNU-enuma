# Framebuffer WC/cache source check — 2026-11-22

Status: source-only, self-checked; no device test or new build.

- `UniXNU-sheng@c8f92b20`: the inspected Git tree has no `fb_wc`, `fb-wc` or `fb-cached` parameter. `package/BootProgressDisplay.h:29` describes an output optimization, not a mapping attribute. The tree references `drivers/GopFramebuffer` in `scripts/build-gop-legacy-display.py:329-344` but does not contain that component's source; its implementation was not checked.
- [`HuajiFruit/UniXNU-sirius@ac0c900485f3c0cd18de9707579a1cdcd3365503`](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/drivers/GopFramebuffer/NativeLegacyDisplay.cpp): `drivers/GopFramebuffer/NativeLegacyDisplay.cpp:658-663` parses `sirius-fb-wc` and maps the scanout with `kIOMapWriteCombineCache` rather than `kIOMapInhibitCache`. Lines 455-467 parse `sirius-fb-cached`, map the source surface with `kIOMapCopybackCache`, and perform cache maintenance before the CPU copy. These are GOP mapping options and cache maintenance, not allocation flags.
- Historical enuma r5 GOP source, `out/enuma-gop-production-20261114-r5/display/source/NativeLegacyDisplay.cpp:842,634`, maps scanout with `kIOMapInhibitCache` and the source with `kIOMapCopybackCache`, respectively. This does not establish r19's linked source or the early text console's actual pmap attributes.

Conclusion: the sirius parameters optimize the GOP frame-copy path, not the early text console path. They are not a supported cause or fix for the observed 11.7 ms/line and are **not a console optimization path**. The early console mapping and runtime bottleneck remain unverified; an indirect effect through shared physical-page cache attributes has not been established.
