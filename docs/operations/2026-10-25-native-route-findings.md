# 原生管线首拒绝定位

S-029首次完整native路由审计间接分类Topology，boot-origin区间
22.241..22.328秒完整落入预定code3窗口；44.719秒Android完成，独立
原分区摘要核验和相机桌面通过。它越过了当次到达拓扑检查之前的接口
资格，不能宣称完整三样本稳定性通过，不能从类别推出具体CTL/LM。

下一候选只记录原首次错误发生阶段，不添加MMIO读取：CTL选择、源
staging、混合器/布局拓扑分别code2/3/4，其他拒绝code1，完整稳定候选
code5。与fafb8a3 native源码逐330个失败位置比较调用/输出一致；旧
严格GOP路径固定基线保持。实际上机结果以独立归档为准。

条件性主判断：若stage选择拒绝，应先核对“所有非零LM字均被当作活动
源”和严格拒绝border位的模型。固定小米
[52a2f18 sde_hw_ctl.c](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/sde/sde_hw_ctl.c#L852-L854)
将CTL_MIXER_BORDER_OUT定义为bit24；没有任何源配置或没有BASE源时可
置此位。该位本身不是另一条SSPP。旧step23虽有相同来源的局部解码，
但其同源对照超时，step23本身未执行，不能借用为本次已验证结论。

若细分返回CTL选择，应优先查活动CTL数量/INTF_ACTIVE位图，不能先动
border；若返回混合器/布局，则staging并非当次首个拒绝，转向具体LM
模式/混合/左右布局。当前不改任一拓扑门，不声称已定位border，也不
由固定内核代码推断本机UEFI接管时实际寄存器值。

## S-030：已定位源staging

S-030细分code3，boot-origin22.257..22.322秒，Android45.750秒，独立
恢复与相机桌面通过。首拒绝在EnumaSelectVideoRoute，而不是本次CTL
选择或后级LM检查。它没有读完三次完整管线，不能称稳定路由通过。

下一候选只对已经捕获的24个staging字分类：全部已知border差异且局部
规范化后恰好两条不同单源路由；已知源数量或编码不支持；未知/virtual
字段；混合器数量或重复源。原快照不变，原失败仍返回，不因规范化能
解码而继续读取后级。主机全部64种border组合、768单比特扰动和类别
负例通过；这不是本机border值的证据，必须等待新的合格实测。
# S-031 result and native border view (2026-10-26)

S-031's boot-origin interval17.246..17.316s lies wholly in predeclared code2.
Android completed40.812s; independent identity/root/slot/unlock/partition hashes
and camera desktop passed. The image is consumed. This supports the captured
staging's only strict two-source selection mismatch being the documented border
bit24. It is not direct register output or evidence of complete stable routing.

Next source52158d9 (documentation pin c45191c) isolates the correction in a new
native border sampler, leaving strict and original native APIs intact. Only the
RAM parsing view clears bit24; raw capture and stability retain that bit. Strict
route selection must still pass before selected SSPP/mixer reads. The same view
feeds mixer resolution and decode, preventing border-only inactive mixers from
being mistaken for routed mixers. Reads remain bounded330 and waits2x100ms.
Unknown bits, source count/duplicates, layout, format, address bounds and raw
configuration changes still reject. Successful audit still requires independent
CPU/SMMU address and downstream association before a pixel experiment or GOP.

## S-032 and first layout predicates (2026-10-26)

S-032 origin27.225..27.339s uniquely mapped to mixer/layout topology rejection;
Android completed51.297s, independent recovery and camera desktop passed. This
supports progress through native source selection/capture, not three complete
stable samples. The image is consumed. Source60dd3d9 adds only first rejection
classification: blend, mode, geometry or left/right assignment. Fixed c45191c
resolver status/output parity covers4608 saved-word mutations.

Working hypothesis: the mode predicate may reject legitimate per-stage alpha
output bits. This is a source-backed possibility, not a measured LM word.
The fixed [MiCode LM implementation](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/sde/sde_hw_lm.c)
lines139..150 updates alpha output while preserving bits31/30; lines70..88 set
the right-mixer flag in bit31, and lines104..120 pack FG/BG constant alpha.
The matching [CRTC implementation](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/sde/sde_crtc.c)
lines1330..1338 derives mixer_op_mode from stage/alpha conditions and line1492
passes it to setup_alpha_out. Current resolver rejects all mode bits except31.
A blend/geometry/side category would displace this hypothesis as the first
blocking predicate. Even a mode category needs precise bit/source correlation
before changing admission; bit30 remains unexplained and is not accepted.

## S-033 corrects the first-blocker hypothesis

S-033 origin17.400..17.467s maps to dim/blend rejection; Android40.391s and
independent recovery/camera passed. Thus mode bits are not the first blocking
predicate on this observation. Source b915308 explains the already captured
blend words without changing admission: selected-source dim, dim outside that
stage, operation mismatch, or alpha mismatch. Tests cover11x11 stage/dim
locations, all four actual110-read sampler rejection paths and17280 selectors.

The fixed [MiCode blend definitions](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/sde/sde_hw_mdss.h)
lines60..75 distinguish constant/pixel alpha selection, inversion, modulation
and transparency. Current0x100 requires FG constant for foreground and BG
constant for background, with packed FG255/BG0. Other encodings must not be
accepted merely because this exact word is absent. If operation/alpha is the
blocker, evaluate explicitly constant-only effective FG255/BG0 semantics,
rejecting pixel selection/modulation/transparency and unknown bits, before any
admission change. Dim outside the source stage is not automatically inactive.

Saved post-Android FDT SHA256643aa3ec450139d38f8cde9a94bca6d9e8e75e752cb7aa992685d34267434c62
independently matches six mixer offsets45000..4a000, length320,11 blend offsets
20..110 at stride18 and blendstage count11. See
reports/enuma-native-blend-fdt.json. This checks descriptor provenance only,
not handoff register values or dim inactivity.


## S-034 result and next structural observation

S-034 valid code4 selected-blend-operation-rejected; origin27.238..27.321,
Android49.094s, independent identity/digests and camera desktop pass. First
preissue identity gate failed without issuing image; D-233 recovery/reentry
passed before the single consumed boot. No all-mixer/all-sample inference.

Main hypothesis: the exact opaque blend predicate is narrower than inherited
configuration. MiCode52a2f180865f8368828985d6384130acd093fa93
[sde_crtc.c](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/sde/sde_crtc.c)
420..476 configures distinct opaque, premultiplied and coverage operations.
This does not identify the actual value. Rather than assume opacity, the next
independent structural sampler retains BLEND as unproven and examines geometry,
source decode and raw stability. It leaves actual blend/dim/processing words
untouched and checks their equality between samples. Bit31 only establishes
left/right geometry per the pinned LM setup_out implementation. Successful
structure is not visual composition or GOP readiness. A geometry/decode/runtime
rejection refutes the hypothesis that blend qualification is the sole blocker.


## S-035 structural result and stability-first geometry question

S-035 valid code3 route-or-geometry-rejected; origin22.268..22.343,
Android44.125s, independent identity/root/slot/unlock and both partition/backup
digests pass. User disabled camera for current nonvisual probes. This refutes
blend as the sole blocker; native geometry or subsequent topology decode
still rejected. It does not establish three-sample stability.

Next Native4 first captures and checks three raw snapshots under the existing
safe single CTL/two source/two mixer capture contract, then explains pure
geometry rejection. Main hypotheses: source output local coordinates/size
assumption or right-mixer assignment, ahead of panel-size mismatch. The
category can refute either without changing any layout admission or issuing
additional register kinds. Code2..5 additionally requires both interfaces to
advance in two bounded windows while full source/mixer/staging words remain
stable. Code1 provides no such implication. Blend and CPU/downstream remain
unproven. Maximum330 reads/two100ms/R-004 mapping unchanged.


## S-036 raw stability plus source output rejection; global-coordinate hypothesis

Valid stable-source-local-output-rejected, origin22.476..22.543; Android45.078s,
independent root/slot/unlock/partition and backup digests pass; consumed. This
supports three raw snapshots stable and both interfaces advancing1..64 across
two100ms windows in this observation. It localizes the first pure geometry
failure to nonzero OutXy or output size mismatch, without numeric values.

Main hypothesis (moderate): the right source uses whole-panel coordinates.
Pinned Xiaomi52a2f180865f8368828985d6384130acd093fa93
[sde_hw_sspp.c](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/sde/sde_hw_sspp.c)
613..651 writes configured destination x/y/width/height to OUT registers; this
does not prove the handed-off coordinates. Native5 tests the exact left0/right
left-width/full-size contract using saved words, then expresses that right
offset in a logical origin on a copy. Raw stability and all original source
decode predicates remain. Code3 refutes this exact model; code4 moves the
blocker into source decode; code5 is a stable logical structure only, retaining
blend/address/physical topology requirements. No pixel or hardware writes.


## S-037 broad source return; S-038 unchanged-sampler status question

S-037 valid source-capture-or-layout-rejected, origin27.444..27.524,
Android52.562s, independent identity and device/backup digests pass; consumed.
The exact global-coordinate rejection code did not appear, but code4 also
covers source capture failures; do not equate it with one decoder status.
Main suspicion is source format/alpha versus the exact RGBX predicate, then
address/common-layout consistency; source geometry/coverage can refute this.
New global-detail changes only the selector: require actual NativeDecode
reason19 and zero output requirements before grouping the returned status.
Other phases and success map to unclassified1. Code5 is rejection. Native5,
raw stability, exact coordinate copy and decoder remain byte-source identical.
The19680 selector matrix and nine camera-free native Python tests pass.


## S-038 actual Format rejection; exact alpha-enable hypothesis

S-038 valid source-format-or-encoding-rejected, origin22.400..22.520,
Android44.610s, independent identity/partition and backup digests pass;
consumed. Its selector requires actual NativeDecode reason19/zero output,
therefore this observation reached decode after raw stable samples, exact
global coordinate and geometry checks. Format status still includes exact
format word, opmode and unpack failures; it is not a numeric register dump.

Main hypothesis is the enabled alpha variant of the otherwise expected8888
format. Pinned Xiaomi52a2f180865f8368828985d6384130acd093fa93
[sde_hw_sspp.c](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/sde/sde_hw_sspp.c)
315..322 defines source component widths and bit8 SRCC3_EN. Native6 tests only
236ff/237ff with at least one alpha-enabled source, clearing bit8 solely in
the logical channel view while preserving raw stability. It retains every
other decode check and requires alpha_semantics_unproven=true/requirements22.
Code3 refutes this exact coordinate/format hypothesis; code4 leaves another
decode condition; code5 is logical structure only. Alpha-safe pixel writes,
blend, CPU/SMMU and physical routing still require their own proof.


## S-040 CPU stage1 expected attribute rejected

Valid code4, boot-origin27.434..27.538s, Android50.390s; independent root,
A-slot/unlock and both device/backup digests pass. Imagebfab7998...consumed.
The actual first page read query returned PAR.F=0 and identity page output,
then ATTR63:56!=bb; it returned before write query or remaining pages. Thus
neither those queries nor actual data access/SMMU are established. R-004
static WRITE_THROUGH_XN is not evidence of the effective DXE mapping.
Next isolated diagnostic classifies the first mismatching PAR attribute,
without changing mappings or adding framebuffer data access. Normal NC/WB
are both plausible, Device would raise a mapping-type concern. Do not change
the expected attribute or call WB/NC qualified solely to obtain code5.


## PAR reporting versus descriptor attributes: stronger downgrade hypothesis

Arm architecture permits PAR ATTR/SH to report implemented resulting
attributes rather than the literal translation descriptor/MAIR value. See
[Arm PAR description](https://documentation-service.arm.com/static/60d32e78677cf7536a55bad7).
The [Cortex-A77 TRM8.3](https://documentation-service.arm.com/static/64ac62b4df6cd61d528c60a0)
states that inner WT and outer WT/NC are downgraded to NC. Therefore the
S-040 non-bb report is not proof that the installed page table was changed
or wrong. Main hypothesis becomes normal-NC effective reporting; it remains
an inference until S-041. Executing-core identity and actual MAIR/table
contents are not established by that hypothesis. WB and Device remain
alternative distinguishable results; do not modify page/cache attributes.

S-041 retains original stage1 query order, guards, bound and first failure,
wrapping the callback only to retain its last PAR. Only actual code4 is
reclassified:44→2 normalNC;ff→3 normalWB;00/04/08/0c→4 Device;other→5.
Code1 includes earlier failure and all-WT, so it is not success. All256
attribute encodings are tested at first read/write/last query with fault
and nonidentity precedence; query count and requirements remain unchanged.
No inference about remaining pages follows a first mismatch classification.


## S-041 other encoding; independent whole-range semantic policy

Valid code5, origin32.469..32.529s, Android53.922s, independent root/slot/
unlock and device/backup hashes pass. Consumed837085b1... . Exact44,ff and
00/04/08/0c excluded on that first mismatch. The exact44 hypothesis was not
supported. MAIR's inner/outer nibbles encode policy plus allocation/transient
hints, so other encodings can still mean normal WT or WB. Do not infer a
numeric byte or wrong mapping. Fixed
[Arm MAIR table](https://documentation-service.arm.com/static/61b75264a2506b46a5c32065)
has nibble4 NC,1..3/8..b WT,5..7/c..f WB,0 other. Use only that shared field
encoding, not any R-profile-specific memory setup from the supplement.

S-042 independently traverses the full decoded range, both R/W ATs/page, and
aggregates semantic policy. Only RAM copies of callback ATTR are normalized
to reuse the unchanged bounded R/W identity loop; actual PAR was already
restored. Code1 prior/context/fault/nonidentity;2 all Normal inner/outerNC,
3 allWT,4 allWB,5 mixed/other. Every2..5 requires full traversal;5 is not
normal memory admission. Hints/raw attribute bytes are inspected transiently
and not retained/exported (clarifies the loose wording in firmware44f8a66
value-transport). No page/cache attribute change or data access, all22 and
alpha/SMMU/downstream obligations remain. Host256 encodings, within-policy
hint changes, cross-policy changes and failure precedence/counts pass.

Actual existing Mu FrameBufferBltLib VideoFill constructs RGB masks only;
setting caller BLT Reserved=ff alone cannot make the stored RGBA alpha opaque.
Existing real-backend host test SetMode clears all four bytes tozero in24
permutations. Any later opaque adapter must cover the actual fill/buffer
conversion path, not just set the incoming BLT reserved field. DiagDraw's
hardcoded top-byte colors also require channel-mask adaptation. Neither
path executes in the current early-return diagnostic.


## S-042 all pages R/W identity NormalWT; isolate physical read next

Valid code3, origin22.454..22.558s, Android44.172s; independent root/A/unlock
and device/local-backup hashes pass. Consumed7dd02e04... . All covering4KiB
pages and both permission queries traversed, nonfault, identity and inner/outer
normalWT semantics; exact allocation/transient hints still unknown. Thus the
earlier exactbb rejection does not establish wrong memory type or a changed
page table. This does not prove actual data or EL1 finalstage2/SMMU/display.

S-043 repeats the same full-range policy audit, admitting a separate data
step only for its WT code3, then rechecks frame extent/stride/geometry and
reads one aligned32-bit word at decoded base. The callback guards exact base,
Splash containment, alignment and count1. No DC-CIVAC/DSB, writes or data
export. Code1 earlier failure;2 other Normal policy;3 mixed/other;4 read
contract/callback rejection;5 one word completed. Read0/ffffffff/other all
produce the same completion code; nothing about content is inferred. This
is separate from the S-042 AT-only baseline so a new failure is not casually
attributed to a pixel store or cache-sync step that was never added.
