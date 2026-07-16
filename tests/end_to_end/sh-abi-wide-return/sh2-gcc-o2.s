	.file	"input.i"
	.data

! Hitachi SH cc1 (cygnus-2.7-96q3 SOA-960904) arguments: -O -fdefer-pop
! -fcse-follow-jumps -fcse-skip-blocks -fexpensive-optimizations
! -fthread-jumps -fstrength-reduce -fpeephole -fforce-mem -ffunction-cse
! -finline -fkeep-static-consts -fcaller-saves -freg-struct-return
! -fdelayed-branch -frerun-cse-after-loop -fschedule-insns2 -fcommon
! -fgnu-linker -m2

gcc2_compiled.:
___gnu_compiled_c:
	.text
	.align 2
LC0:
	.long	1
	.long	591751049
	.align 2
	.global	_test
_test:
	mov.l	r14,@-r15
	mov	r15,r14
	mov	r4,r4
	mov	r4,r5
	shll	r4
	subc	r4,r4
	mov.l	L2,r1
	mov.l	@(4,r1),r2
	mov.l	@r1,r1
	mov.l	@r15+,r14
	clrt
	addc	r2,r5
	addc	r1,r4
	mov	r4,r0
	rts
	mov	r5,r1
L3:
	.align 2
L2:
	.long	LC0
