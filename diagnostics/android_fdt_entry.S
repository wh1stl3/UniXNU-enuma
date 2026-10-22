/* Temporary stock ARM64 Image hook. Preserve Linux x0..x3 and restore SP.
 * All storage is appended inside the expanded Image, dead after stock entry.
 */
.section .text.entry,"ax"
.global _start
_start:
    mov x19, sp
    adrp x16, stack_top
    add x16, x16, :lo12:stack_top
    mov sp, x16
    stp x0, x1, [sp, #-32]!
    stp x2, x3, [sp, #16]
    bl enuma_fdt_entry
    ldp x2, x3, [sp, #16]
    ldp x0, x1, [sp], #32
    mov sp, x19
    b kernel_entry
.section .bss.stack,"aw",%nobits
.balign 16
    .space 16384
stack_top:
