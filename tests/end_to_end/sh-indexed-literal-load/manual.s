glabel test
mov.l base, r1
mov.w offset, r0
mov.b @(r0,r1), r0
rts
nop
offset:
.word 0x0010
.align 2
base:
.long 0x06001000

glabel test_negative
mov.l base_negative, r1
mov.w offset_negative, r0
mov.b @(r0,r1), r0
rts
nop
offset_negative:
.word 0xFFF0
.align 2
base_negative:
.long 0x06001020

glabel test_dynamic
mov r5, r0
mov.b @(r0,r4), r0
rts
nop
