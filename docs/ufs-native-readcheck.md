# Native read diagnostic: host increment and review boundary

Latest increment: temporary ShengUfs `UfsEnumaReadContract.h` validates a
synthetic profile and full DMA region; `tests/enuma_read_contract.cpp` is
host-only self-checked. `.cache/native-read-contract-20261112/` contains copies,
hashes and patch. It is not wired to a provider or native entry; booleans in the
input are modeled claims, **not runtime proof**. No actual command adapter,
terminal lifetime, production provenance, target build or device test exists.

2026-11-12 follow-up: ignored `.cache/native-read-review-20261112/` contains
per-hunk baseline hashes, deliberately compile-blocked partial `review-only.patch`,
host-testable ordered model and `deep-brief.md` with concrete missing hunks. The
runtime adapter is **not implemented**; patch annotations are not a working
native hook. Fourteen first-failure injections are host-only self-checks.

Self-checked host fixture interface only; no device entry, actual UFS command,
integration, independent verification or claim of safe takeover. The model's
synthetic booleans do not establish real ownership. Disabled and missing resources
reject. It distinguishes preallocation backing/producer/mapping conditions, TR
empty, TM empty and TR stop readback. It compares exactly one supplied block;
matching is evidence about fixtures, not GPT validation or media identity.

Existing board snapshot: primary GPT on historical sda has 4096-byte logical
blocks, capacity 61880320 blocks; sda-to-UFS-LUN is unknown. Historical primary
is not current geometry; no LUN 0 assumption. Live DT lacks iommus. Saved DALSys
private UFS records `[0,1,4e0,30,0]` and `[10,1,e0,30,0]` match HAL selectors;
the Linux SM8250 binding also contains e0/4e0. Neither establishes enuma runtime
SID, CB, exclusivity or effective mapping. Software client ctx is not a CB.
See ufs-resource-evidence.md:236-300,493-525,585-614 and
ufs-handoff-design.md:5-38; protocol-index callchain is referenced there.

## Exact baseline and review proposal (not a patch)

Fixed ShengUfs e2b32cc, read via git show: `NativeUfs::start` -> `startRoot` ->
`hostBringUp` maps HC, allocates and clears new DMA **before** `hostStopQueue`;
the latter checks both TR/TM doorbells then stops only TR; `smmuBypassStream`
uses hardcoded 0x60 and selects its bank, then `hostStartQueue`, NOP, query,
possibly START STOP UNIT, and up to 20 TUR attempts on LUN 0. `RootCommands.h`
`hostRead4k` hardcodes 4096 bytes; normal `startRoot` proceeds to publication.
Those defaults, retry/wake and publication are not this diagnostic's contract.

For one deep review, propose a default-0 compile flag plus mutually exclusive
dedicated diagnostic boot argument in `NativeUfs.cpp::start`, guarded by the
existing enuma platform selector before any MMIO; no `adoptAndRead`. A separate
diagnostic bring-up variant must enforce old backing exclusion before allocator,
map HC, allocate new retained DMA, check TR empty and TM empty, stop TR/readback,
apply only a specifically evidenced SID/CB mapping contract, start the new queue,
NOP and read-only power query, one TUR on explicitly bound LUN, READ CAPACITY,
check exact historical-reference geometry and issue exactly one READ(10), compare
to externally supplied known GPT block, then terminate without publication.
No START STOP, retry, reset, media WRITE or mount. Sleeping/power-not-ready fails.
`RootQueue.h` and `RootCommands.h` need review for one-shot/error paths and a
bounded explicit-LUN capacity/read helper; all first errors terminal. Failure must
not free DMA or old backing/mappings until independently proved retired; queue
and allocation lifetime/termination must be designed, not assumed by this note.
READ CAPACITY(10) sentinel/overflow and READ(10) range must refuse. Real code must
not take the model's caller-supplied booleans as proof. No diff implemented.

Review questions: can the stated producer exclusion and every active backing
category be established before allocation; does empty TR/TM plus TR stop suffice
for the specific next operations (not as global DMA retirement); what exact SID,
CB and SMMU policy preserve other users; how retain all potentially active old
and new buffers on every failure; what terminal output is safe and observable?
This is DMA/IOMMU/lifecycle high-risk and requires deep review before code merge.

Unique bounded next evidence request: obtain a platform-owner/firmware-maintainer
handoff contract for this exact board, identifying UFS stream-to-context mapping,
other users, producer exclusion, backing retention and DMA completion semantics;
it may close or explicitly fail those gates, but does not identify sda's LUN.
Separately a future authorized Android sysfs H:C:T:L controller-to-sda association
can bind historical identity only if accessible, and must be reconciled with the
current native LUN and capacity; previous unprivileged attempt was denied. Neither
request authorizes hardware access. No new capture framework is proposed.
