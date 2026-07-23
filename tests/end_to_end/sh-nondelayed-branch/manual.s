glabel test
tst r4, r4
bf L1
mov #0, r0
rts
nop
L1:
mov #255, r0
rts
nop

glabel test_bt
tst r4, r4
bt L2
mov #255, r0
rts
nop
L2:
mov #0, r0
rts
nop
