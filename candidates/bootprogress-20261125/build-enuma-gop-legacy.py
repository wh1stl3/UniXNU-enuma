#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Adapt the pinned earlier enuma CPU/GOP builder to explicit, paired inputs."""
import argparse
import hashlib
import json
from pathlib import Path

DEVICE = Path(__file__).resolve().parents[2]
DONOR = "f18b4df865405f2a287b84977d7aca745e056d656d9fc9df1662970ce2969de7"
BUILDER_SHA = "3b3d92bf8c1517ae9844ca537fb0e096fd4199092f9a981fa4498fc3c2673586"
PACKAGE = {
    "EnumaLegacyDisplay.cpp": "04b8fbfd5d932ed1e78cd6e2ee5bc2a00f933ad0afe671f13bd93cd970fe04a2",
    "LegacyABI.in.h": "de849bfad5fea2aefabf0d3d95d6ce58abcc583b225e05fd59af7c88031865ee",
}


def one(text, before, after):
    if text.count(before) != 1:
        raise ValueError("expected one scanout site: " + before)
    return text.replace(before, after)


def wire_scanout(text, core):
    text = one(text, 'extern "C" bool native_legacy_prepare_scanout(void);',
               'extern "C" bool native_legacy_prepare_scanout(const PE_Video *);\n'
               'extern "C" bool enuma_bp_scanout_context(void);')
    text = one(text, '    void kickOnce() {', '    __attribute__((noinline)) void kickOnce() {\n'
               '        if(!enuma_bp_scanout_context())return;')
    start = text.index('        // The diagnostic renderer repaints')
    end = text.index('        // Surfaces may be write-combined', start)
    text = text[:start] + """        noteSurface(surface,memory);
        const bool half=nativeHalf(native_legacy_surface_format(surface),native_legacy_surface_planes(surface));
        stat(7);note(7,-1,request);
""" + text[end:]
    text = one(text, '''            if(!native_legacy_prepare_scanout()) {native_legacy_transfer_observed(kIOReturnNotReady,request,0);return;}
            directToBoot();''', '''            if(!native_legacy_fill_layout(reinterpret_cast<volatile void *>(bootMapping->getVirtualAddress()),
                bootMapping->getLength(),blank.v_rowBytes,bw,bh)) {
                native_legacy_transfer_observed(kIOReturnBadArgument,request,0);return;
            }
            if(!native_legacy_prepare_scanout(&blank)) {native_legacy_transfer_observed(kIOReturnNotReady,request,0);return;}''')
    start = text.index("    const uint8_t *table=halfTable();", text.index("static bool convertHalfRows"))
    end = text.index("    for(uint32_t y=0;", start)
    text = text[:start] + text[end:]
    start = text.index("static bool convertHalfRows")
    end = text.index("class NativeLegacyDisplay;", start)
    text = text[:start] + """static __attribute__((noinline)) void convertHalfRows(volatile void *dst,uint64_t dstStride,const void *src,
                            uint64_t srcStride,uint32_t width,uint32_t height,const uint8_t *table) {
""" + text[text.index("    for(uint32_t y=0;", start):text.index("    return true;", start)] + "}\n" + text[end:]
    start = text.index("        if(half) {", text.index("void kickOnce()"))
    end = text.index('            __asm__ volatile("dsb sy"', start)
    text = text[:start] + """        if(half) {
            const uint8_t *table=halfTable();
            if(!table || !native_legacy_copy_layout(reinterpret_cast<volatile void *>(bootMapping->getVirtualAddress()),
                bootMapping->getLength(),video.v_rowBytes,reinterpret_cast<const void *>(source->getVirtualAddress()),
                source->getLength(),sourceStride,width,height) ||
                sourceStride<uint64_t(width)*8 || ((sourceStride|source->getVirtualAddress())&7)) {
                OSSafeReleaseNULL(source);native_legacy_transfer_observed(kIOReturnBadArgument,request,0);return;
            }
            if(!native_legacy_prepare_scanout(&video)) {OSSafeReleaseNULL(source);native_legacy_transfer_observed(kIOReturnNotReady,request,0);return;}
            uint64_t copyStart;__asm__ volatile("isb\\n\\tmrs %0, cntpct_el0":"=r"(copyStart));
            convertHalfRows(reinterpret_cast<volatile void *>(bootMapping->getVirtualAddress()),video.v_rowBytes,
                reinterpret_cast<const void *>(source->getVirtualAddress()),sourceStride,width,height,table);
""" + text[end:]
    # BGRA / diff fallback uses a successful common layout. Allocate and
    # decide the optional diff branch before the irreversible release.
    start = text.index("        if(!native_legacy_prepare_scanout()) {")
    end = text.index("            if(!diffOff && shadow && shadowBytes>=need)", start)
    text = text[:start] + """        uint64_t need=(uint64_t)width*height*4;
        static int diffOff=-1;
        if(diffOff<0){unsigned v=0;PE_parse_boot_argn("sheng-fb-diff",&v,sizeof v);diffOff=(v!=1);}
        if(!diffOff && !shadow && need<=(64ull<<20)){shadow=IOMallocAligned((vm_size_t)need,16384);if(shadow){shadowBytes=need;shadowValid=false;}}
        const bool diff=!diffOff && shadow && shadowBytes>=need &&
            !((reinterpret_cast<uintptr_t>(shadow)|bootMapping->getVirtualAddress()|video.v_rowBytes)&7) && !(width&1);
        if(!native_legacy_prepare_scanout(&video)) {
            OSSafeReleaseNULL(source);native_legacy_transfer_observed(kIOReturnNotReady,request,0);return;
        }
        uint64_t copyStart;__asm__ volatile("isb\\n\\tmrs %0, cntpct_el0":"=r"(copyStart));
        uint64_t stored=UINT64_MAX;
        {
            if(diff)""" + text[end + len("            if(!diffOff && shadow && shadowBytes>=need)"):]
    header = core / "NativeLegacyRequest.h"
    request = header.read_text()
    start = request.index("static inline int native_legacy_fill_pixels")
    end = request.index("    for (uint32_t row=0;", start)
    request = request[:start] + """static inline int native_legacy_fill_layout(volatile void *destination,
    uint64_t destinationBytes, uint64_t destinationStride, uint32_t width, uint32_t height) {
    uintptr_t dst=(uintptr_t)destination;
    return dst && !(dst&3) && !(destinationStride&3) &&
        native_legacy_surface_bounds(width,height,destinationStride,destinationBytes,destinationBytes) &&
        destinationBytes<=UINTPTR_MAX && dst<=UINTPTR_MAX-destinationBytes;
}
static __attribute__((noinline)) int native_legacy_fill_pixels(volatile void *destination,
    uint64_t destinationBytes, uint64_t destinationStride,
    uint32_t width, uint32_t height, uint32_t value) {
    if (!native_legacy_fill_layout(destination,destinationBytes,destinationStride,width,height)) return 0;
    uintptr_t dst=(uintptr_t)destination;
""" + request[end:]
    request = one(request, "static inline int native_legacy_copy_pixels",
                  "static __attribute__((noinline)) int native_legacy_copy_pixels")
    request = one(request, "static inline uint64_t native_legacy_copy_diff",
                  "static __attribute__((noinline)) uint64_t native_legacy_copy_diff")
    header.write_text(request)
    return text


def wire_release(text):
    text = one(text, "extern int disableConsoleOutput;\n", "")
    text = one(text, "bool entered, lateEntered, scanoutReleased;", "bool entered, lateEntered;")
    start = text.index("bool native_legacy_prepare_scanout(void) {")
    end = text.index("// CPU-only policy:", start)
    return text[:start] + """bool enuma_bp_gui_take(const PE_Video *);
bool native_legacy_prepare_scanout(const PE_Video *v) {
    return displayObject && enuma_bp_gui_take(v);
}
""" + text[end:]


def load_builder(source, tree, report, handoff=False):
    path = source / "scripts/build-enuma-gop-legacy.py"
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != BUILDER_SHA:
        raise ValueError(f"builder SHA mismatch: {path}")
    for name, expected in PACKAGE.items():
        p = source / "package" / name
        if hashlib.sha256(p.read_bytes()).hexdigest() != expected:
            raise ValueError(f"backend SHA mismatch: {p}")
    text = raw.decode()

    def replace(old, new):
        nonlocal text
        if text.count(old) != 1:
            raise ValueError(f"expected one pinned builder site: {old}")
        text = text.replace(old, new)

    replace("SOURCE = Path(__file__).resolve().parents[1]", f"SOURCE = Path({str(source)!r})")
    replace("DEVICE = SOURCE.parents[1]", f"DEVICE = Path({str(DEVICE)!r})")
    line = next(line for line in text.splitlines() if line.startswith("TREE = Path("))
    replace(line, f"TREE = Path({str(tree)!r})")
    replace("candidate.with_suffix('.json').read_text()", f"Path({str(report)!r}).read_text()")
    replace("record(candidate.with_suffix('.json'))", f"record(Path({str(report)!r}))")
    replace("argv[argv.index('-o') + 1] = str(dest)", """argv[argv.index('-o') + 1] = str(dest)
            for option in ('-MF', '-MT', '-MJ'):
                if option in argv:
                    at = argv.index(option)
                    del argv[at:at + 2]""")
    replace("image = macho(blob)", """image = macho(blob)
    need(plan['original_sha256'] == """ + repr(DONOR) + """, 'wrong iPad7,1 21H461 donor')
    module = 'com.apple.iokit.IOSurface'
    extent = next(e for e in plan['extents'] if e['module'] == module and e['segment'] == '__TEXT_EXEC')
    start = backed_offset(image['segments'], extent['va'], extent['size'], len(blob))
    need(hashlib.sha256(blob[start:start + extent['size']]).hexdigest() ==
         plan['original_executable_sha256'][module], 'IOSurface text/report mismatch')""")
    if handoff:
        replace("        path.write_text(text)", "        text = wire_scanout(text, core)\n        path.write_text(text)")
        replace("compile(record(SOURCE / 'package/EnumaLegacyDisplay.cpp'), out / 'EnumaLegacyDisplay.o')",
                """backend = wire_release(record(SOURCE / 'package/EnumaLegacyDisplay.cpp').read_text())
        (out / 'EnumaLegacyDisplay.cpp').write_text(backend)
        compile(out / 'EnumaLegacyDisplay.cpp', out / 'EnumaLegacyDisplay.o')""")
    g = {"__file__": str(path), "__name__": "_legacy", "wire_scanout": wire_scanout, "wire_release": wire_release}
    exec(compile(text, str(path), "exec"), g)
    return g


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("candidate", "plan", "source", "tree"):
        p.add_argument("--" + name, required=True, type=Path)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--output", type=Path)
    mode.add_argument("--inspect", type=Path)
    p.add_argument("--handoff", action="store_true")
    p.add_argument("--check-vtable", type=Path, help="archive builder result.json to verify against final ABI")
    a = p.parse_args()
    g = load_builder(a.source.resolve(), a.tree.resolve(), a.plan.resolve(), a.handoff)
    if a.inspect is not None:
        abi = g["qualify"](a.candidate.resolve())
        if a.check_vtable is not None:
            old = json.loads(a.check_vtable.read_text())["abi"]
            for i, symbol in enumerate(old["compiled_vtable_symbols"]):
                if i in abi["pure"]:
                    if abi["methods"][i] != abi["names"]["___cxa_pure_virtual"]:
                        raise ValueError(f"abstract slot {i}: wrong exported target")
                elif i >= 168:
                    if old["methods"][i] != abi["methods"][i]:
                        raise ValueError(f"private Legacy slot {i}: absolute target drift")
                elif not symbol.startswith(("__ZN19NativeLegacyDisplay", "__ZNK19NativeLegacyDisplay")):
                    if abi["names"].get(symbol) != abi["methods"][i]:
                        raise ValueError(f"native slot {i}: final export mismatch for {symbol}")
            abi["compiled_slots_requalified"] = len(old["compiled_vtable_symbols"])
        del abi["names"]
        with a.inspect.open("x") as report:
            json.dump(abi, report, indent=2)
    else:
        g["build"](a.candidate.resolve(), a.output.resolve())


if __name__ == "__main__":
    main()
