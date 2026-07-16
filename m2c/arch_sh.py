from __future__ import annotations
from dataclasses import replace
from typing import Callable, Dict, List, Optional

from .error import DecompFailure
from .options import Target
from .asm_instruction import (
    Argument,
    AsmAddressMode,
    AsmInstruction,
    AsmLiteral,
    AsmState,
    Register,
    Writeback,
    get_jump_target,
)
from .instruction import (
    Instruction,
    InstructionMeta,
    Location,
)
from .translate import (
    Abi,
    AbiArgSlot,
    Arch,
    ArgLoc,
    BinaryOp,
    CarryBit,
    Cast,
    Expression,
    InstrMap,
    InstrArgs,
    Literal,
    NodeState,
)

from .evaluate import (
    condition_from_expr,
    handle_add,
    handle_addi,
    handle_load,
    handle_sub,
    make_store,
)

from .types import FunctionSignature, Type


class Sh2Arch(Arch):
    arch = Target.ArchEnum.SH2

    re_comment = r"!.*"
    supports_dollar_regs = False
    supports_at_addressing = True
    has_delay_slots = True

    home_space_size = 0

    stack_pointer_reg = Register("r15")
    frame_pointer_regs = [Register("r14")]
    return_address_reg = Register("pr")

    base_return_regs = [(Register("r0"), False)]
    all_return_regs = [Register("r0"), Register("r1")]

    argument_regs = [Register(r) for r in ["r4", "r5", "r6", "r7"]]
    simple_temp_regs = [Register(r) for r in ["r0", "r1", "r2", "r3"]]
    temp_regs = argument_regs + simple_temp_regs + [Register("condition_bit")]

    saved_regs = [
        Register(r) for r in ["r8", "r9", "r10", "r11", "r12", "r13", "r14", "pr"]
    ]

    all_regs = (
        saved_regs
        + temp_regs
        + [stack_pointer_reg]
        + [
            Register(r)
            for r in [
                "mach",
                "macl",
            ]
        ]
    )

    aliased_regs: Dict[str, Register] = {}

    @classmethod
    def missing_return(cls) -> List[Instruction]:
        meta = InstructionMeta.missing()
        return [
            cls.parse("rts", [], meta),
            cls.parse("nop", [], meta),
        ]

    @classmethod
    def normalize_instruction(
        cls, instr: AsmInstruction, asm_state: AsmState
    ) -> AsmInstruction:
        return instr

    @classmethod
    def parse(
        cls, mnemonic: str, args: List[Argument], meta: InstructionMeta
    ) -> Instruction:
        inputs: List[Location] = []
        clobbers: List[Location] = []
        outputs: List[Location] = []
        is_return = False
        is_load = False
        is_store = False
        has_delay_slot = False
        is_conditional = False
        jump_target = None
        eval_fn: Optional[Callable[[NodeState, InstrArgs], object]] = None

        if mnemonic == "rts":
            assert len(args) == 0
            inputs = [Register("pr")]
            is_return = True
            has_delay_slot = True
        elif mnemonic == "nop":
            assert len(args) == 0
        elif mnemonic == "mov":
            assert len(args) == 2 and isinstance(args[1], Register)
            outputs = [args[1]]
            if isinstance(args[0], Register):
                inputs = [args[0]]
                eval_fn = lambda s, a: s.set_reg(a.reg_ref(1), a.reg(0))
            else:
                assert isinstance(args[0], AsmLiteral)
                eval_fn = lambda s, a: s.set_reg(a.reg_ref(1), Literal(a.imm_value(0)))
        elif mnemonic in ("mov.l", "mov.w"):
            assert len(args) == 2
            if isinstance(args[0], Register):
                assert isinstance(args[1], AsmAddressMode)
                inputs = [args[0], args[1].base]
                is_store = True
                if args[1].writeback is None:
                    eval_fn = lambda s, a: make_store(
                        a, Type.reg32(likely_float=False)
                    )
            else:
                assert isinstance(args[1], Register)
                if isinstance(args[0], AsmAddressMode):
                    inputs = [args[0].base]
                outputs = [args[1]]
                is_load = True
                if not (
                    isinstance(args[0], AsmAddressMode)
                    and args[0].writeback is not None
                ):
                    load_type = (
                        Type.s16()
                        if mnemonic == "mov.w"
                        else Type.reg32(likely_float=False)
                    )
                    eval_fn = lambda s, a: s.set_reg(
                        a.reg_ref(1),
                        handle_load(
                            replace(a, raw_args=[a.raw_arg(1), a.raw_arg(0)]),
                            type=load_type,
                        ),
                    )
        elif mnemonic in cls.instrs_arithmetic:
            assert len(args) == 2 and isinstance(args[1], Register)
            inputs = [args[1]]
            if isinstance(args[0], Register):
                inputs.insert(0, args[0])
            outputs = [args[1]]
            eval_fn = lambda s, a: s.set_reg(
                a.reg_ref(1), cls.instrs_arithmetic[mnemonic](a)
            )
        elif mnemonic == "clrt":
            assert len(args) == 0
            outputs = [Register("condition_bit")]
            eval_fn = lambda s, a: s.set_reg(Register("condition_bit"), Literal(0))
        elif mnemonic == "shll":
            assert len(args) == 1 and isinstance(args[0], Register)
            inputs = [args[0]]
            outputs = [args[0], Register("condition_bit")]

            def eval_fn(s: NodeState, a: InstrArgs) -> None:
                value = BinaryOp.intptr(a.reg(0), "+", a.reg(0))
                s.set_reg(Register("condition_bit"), CarryBit(value))
                s.set_reg(a.reg_ref(0), value)

        elif mnemonic in ("addc", "subc"):
            assert (
                len(args) == 2
                and isinstance(args[0], Register)
                and isinstance(args[1], Register)
            )
            inputs = [args[0], args[1], Register("condition_bit")]
            outputs = [args[1], Register("condition_bit")]

            def eval_fn(s: NodeState, a: InstrArgs) -> None:
                carry = a.regs[Register("condition_bit")]
                op = "+" if mnemonic == "addc" else "-"
                value = BinaryOp.intptr(a.reg(1), op, a.reg(0))
                value = BinaryOp.intptr(value, op, carry)
                s.set_reg(Register("condition_bit"), CarryBit(value))
                s.set_reg(a.reg_ref(1), value)
        elif mnemonic == "tst":
            assert (
                len(args) == 2
                and isinstance(args[0], Register)
                and isinstance(args[1], Register)
            )
            inputs = [args[0], args[1]]
            outputs = [Register("condition_bit")]
            same_reg = args[0] == args[1]

            def eval_fn(s: NodeState, a: InstrArgs) -> None:
                # tst does '&' but gcc uses it for 'if (x == 0)' as well.
                # so check if it's the same reg. e.g. 'tst r4, r4'
                value = (
                    a.reg(0) if same_reg else BinaryOp.intptr(a.reg(1), "&", a.reg(0))
                )
                s.set_reg(
                    Register("condition_bit"),
                    BinaryOp.icmp(value, "==", Literal(0)),
                )

        elif mnemonic == "bt.s":
            assert len(args) == 1
            inputs = [Register("condition_bit")]
            jump_target = get_jump_target(args[0])
            is_conditional = True
            has_delay_slot = True
            eval_fn = lambda s, a: s.set_branch_condition(
                condition_from_expr(a.regs[Register("condition_bit")])
            )
        elif mnemonic == "bra":
            assert len(args) == 1
            jump_target = get_jump_target(args[0])
            has_delay_slot = True
        else:
            raise DecompFailure(f"Unable to parse instruction: {mnemonic}")

        return Instruction(
            mnemonic=mnemonic,
            args=args,
            meta=meta,
            inputs=inputs,
            clobbers=clobbers,
            outputs=outputs,
            eval_fn=eval_fn,
            jump_target=jump_target,
            is_conditional=is_conditional,
            is_return=is_return,
            is_load=is_load,
            is_store=is_store,
            has_delay_slot=has_delay_slot,
        )

    instrs_arithmetic: InstrMap = {
        # sh2 format is src, dst
        # add handler is dest, left, right
        "add": lambda a: (
            handle_add
            if isinstance(a.raw_arg(0), Register)
            else handle_addi
        )(
            replace(a, raw_args=[a.raw_arg(1), a.raw_arg(1), a.raw_arg(0)])
        ),
        "sub": lambda a: handle_sub(a.reg(1), a.reg(0)),
    }

    def arg_name(self, loc: ArgLoc) -> str:
        if loc.offset is not None:
            return f"arg{loc.offset // 4 + 4}"
        assert loc.reg is not None
        reg_num = int(loc.reg.register_name[1:])
        return f"arg{reg_num - 4}"

    def function_abi(
        self,
        fn_sig: FunctionSignature,
        likely_regs: Dict[Register, bool],
        *,
        for_call: bool,
    ) -> Abi:
        known_slots: List[AbiArgSlot] = []
        candidate_slots: List[AbiArgSlot] = []
        possible_slots: List[AbiArgSlot] = []

        if fn_sig.params_known:
            if (
                fn_sig.return_type.is_struct()
                and fn_sig.return_type.get_parameter_size_align_bytes()[0] > 8
            ):
                known_slots.append(
                    AbiArgSlot(
                        ArgLoc(None, -1, Register("r2")),
                        Type.ptr(fn_sig.return_type),
                        name="__return__",
                        comment="return",
                    )
                )

            offset = 0
            for param in fn_sig.params:
                param_type = param.type.decay()
                size, align = param_type.get_parameter_size_align_bytes()
                # The GNU SH ABI aligns parameter words to at most 4 bytes,
                # including long long and double.
                align = min(align, 4)
                size = (size + 3) & ~3
                offset = (offset + align - 1) & -align
                for i in range(offset // 4, (offset + size) // 4):
                    part_offset = i * 4 - offset
                    reg = Register(f"r{i + 4}") if i < 4 else None
                    stack_offset = None if reg is not None else (i - 4) * 4
                    if size > 4:
                        name = (
                            f"{param.name}_unk{part_offset:X}" if param.name else None
                        )
                        slot_type = Type.any()
                        comment = f"{param_type}+{part_offset:#x}"
                    else:
                        name = param.name
                        slot_type = param_type
                        comment = None
                    known_slots.append(
                        AbiArgSlot(
                            ArgLoc(stack_offset, i, reg),
                            slot_type,
                            name=name,
                            comment=comment,
                        )
                    )
                offset += size

            if fn_sig.is_variadic:
                for i in range(offset // 4, 4):
                    candidate_slots.append(
                        AbiArgSlot(
                            ArgLoc(None, i, Register(f"r{i + 4}")), Type.any_reg()
                        )
                    )
        else:
            candidate_slots = [
                AbiArgSlot(ArgLoc(None, i, Register(f"r{i + 4}")), Type.intptr())
                for i in range(4)
            ]

        # argument registers are filled in order, so using a higher register implies
        # that the preceding registers may also contain arguments
        highest_used = -1
        for i, reg in enumerate(self.argument_regs):
            if likely_regs.get(reg, False):
                highest_used = i
        for i, slot in enumerate(candidate_slots):
            if i <= highest_used:
                possible_slots.append(slot)

        return Abi(
            arg_slots=known_slots,
            possible_slots=possible_slots,
        )

    @staticmethod
    def function_return(expr: Expression) -> Dict[Register, Expression]:
        return {
            Register("r0"): Cast(
                expr, reinterpret=True, silent=True, type=Type.intptr()
            ),
        }
