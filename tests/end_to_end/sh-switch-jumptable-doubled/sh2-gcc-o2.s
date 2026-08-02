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
	.global	_test
_test:
	mov.l	r8,@-r15
	mov.l	r14,@-r15
	mov	r15,r14
	mov	r5,r6
	mov	#0,r5
	mov	#1,r3
	mov	#3,r8
	mov	#2,r7
L5:
	mov	r5,r1
	mov	r7,r0
	mov.w	@(r0,r4),r2
	add	r1,r1
	mov	r1,r0
	mov.w	@(r0,r4),r1
	cmp/gt	r1,r2
	bf	L4
	mov	r3,r5
L4:
	add	#1,r3
	cmp/gt	r8,r3
	bf.s	L5
	add	#2,r7
	mov	r5,r2
	add	r2,r2
	mov	r2,r0
	mov	#3,r1
	cmp/hi	r1,r5
	bt.s	L8
	mov.w	r6,@(r0,r4)
	mov	r2,r1
	mova	L13,r0
	mov.w	@(r0,r1),r1
	add	r1,r0
	jmp        @r0
	nop
	.align 2
L13:
	.word	L9-L13
	.word	L10-L13
	.word	L11-L13
	.word	L12-L13
L9:
	bra	L8
	add	#3,r6
L10:
	bra	L8
	add	#5,r6
L11:
	bra	L8
	add	#7,r6
L12:
	add	#11,r6
L8:
	mov	r14,r15
	mov.l	@r15+,r14
	mov.l	@r15+,r8
	rts
	mov	r6,r0
