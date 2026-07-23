glabel test
mov.l base, r1
mov.w offset, r0
mov #0, r2
mov.b r2, @(r0,r1)
rts
nop
offset:
.word 0x0133
.align 2
base:
.long 0x060997F8
