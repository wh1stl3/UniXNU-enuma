# enuma SPI IPI INTID inventory — 2026-11-24

Status: **self-checked**, host-only static analysis; no build or device access.
Physical occupancy and distributor capacity are **unknown**; r61 is not cleared
for device use by this inventory.

## Scope and mapping

The active UniXNU base is `693f5d9cae8a408dd18b39f3f9fdc4228c934241`;
SM8250 common is `166235ec2480ff0992627b7aafa15c65ce6b4efa`. The board
`dts/enuma.dts:8,39-41` includes that common DTS and enables UFS.
The official generator `UniXNU/scripts/unixnu/devicetree.py:240-252` reads
the interrupt parent's width and copies the original cells in little-endian:

```python
cells = entry.cells(key)
width = controller.scalar('#interrupt-cells') if controller else 0
properties.append((key, struct.pack(f'<{len(cells)}I', *cells)))
```

Thus the generator **does not add 32** or convert a specifier to a single
INTID. Its export selection is only enabled entries having `unixnu,adt-name`
(`devicetree.py:370-377`); the ADT is not a complete board IRQ inventory.
For a standard GIC SPI specifier `<0 N flags ...>`, N is the SPI-relative
number and the corresponding INTID is N+32: INTID 1008–1015 corresponds to
SPI 976–983 (`0x3d0`–`0x3d7`). This is the GIC binding interpretation, not a
conversion observed in the generator. The actual downstream kernel consumer
conversion was not located; no claim is made that every consumer implements it.

## Actual candidate ADT and wider snapshot

Read the r61 `payload.img` member `Payloads/kernel.macho.adt` using
`member()`/`parse()` in `scripts/compare-display-config-20261123.py:18-47`.
SHA-256 is `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457`,
matching `docs/enuma-r61-smp2-host-20261124.md:29-35`. All **115 properties**
were inspected: the only property names containing `interrupt` are
`/arm-io/intc:#interrupt-cells` and `/arm-io/intc:interrupt-controller`.
There are **no `interrupts` or `interrupts-extended` properties**, hence no
nodes with declared INTID 1008–1015 or SPI 976–983 and no device purposes to
list. This is stronger than scanning just the numerical range, but only for
this ADT. The earlier r34 inventory `docs/enuma-adt-properties-20261123.txt`
is a different ADT and is not substituted for r61.

Separately, the historical live FDT decompilation
`.cache/firmware/fdt-live.dts` SHA-256
`db567ce4d5fdf0805a5351a3fd65ceb68bbe1fb1a508f78039dd5e30c382f7a8`
was searched for exact hexadecimal cells `0x3d0`–`0x3d7` and
`0x3f0`–`0x3f7` in `interrupts` and `interrupts-extended` property lines;
there were no matches. This text search is supplemental, not a complete
phandle-aware GIC routing/firmware reservation analysis, and the snapshot is
not a live current hardware reading. It does not prove a free hardware IRQ.
Other encodings, firmware/secure-world users and hard-coded users remain open.

## Controller capacity and decision

`UniXNU-sm8250-common/dts/sm8250.dtsi:43-50` declares
`#interrupt-cells = <4>` and the GIC register ranges; `interrupt-controller`
is a flag. The r61 ADT has the same four-cell value and no interrupt-count
property. Four is the number of cells per *specifier*, not the number of SPIs.
Neither the register-window size nor this property proves INTID 1008 is
implemented. GICD_TYPER was not read and no controller capacity claim is made.

1008/1009 physical occupancy: **undetermined**, confidence insufficient for
no-conflict; risk **high** until capacity and reservation/routing are proven.
On the stated ArmCpu path, priority writes affect 1008–1011 and dispatch
intercepts 1008–1015, so checking only the two selected CPUs is insufficient.
No alternate INTIDs can be recommended without equivalent capacity, routing,
reservation and dispatch-range evidence; the hardware GIC/firmware allocation
and software users must first be inventoried. No runtime delivery is inferred.
