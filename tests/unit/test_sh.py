import unittest

from m2c.arch_sh import Sh2Arch
from m2c.asm_instruction import Register
from m2c.types import FunctionParam, FunctionSignature, Type


class TestShAbi(unittest.TestCase):
    def test_fifth_argument_is_on_stack(self) -> None:
        signature = FunctionSignature(
            return_type=Type.s32(),
            params=[
                FunctionParam(Type.s32(), name)
                for name in ("a", "b", "c", "d", "e")
            ],
            params_known=True,
        )

        abi = Sh2Arch().function_abi(signature, {}, for_call=False)

        self.assertEqual(
            [(slot.loc.reg, slot.loc.offset) for slot in abi.arg_slots],
            [
                (Register("r4"), None),
                (Register("r5"), None),
                (Register("r6"), None),
                (Register("r7"), None),
                (None, 0),
            ],
        )

    def test_wide_argument_splits_between_r7_and_stack(self) -> None:
        signature = FunctionSignature(
            return_type=Type.s32(),
            params=[
                FunctionParam(Type.s32(), "a"),
                FunctionParam(Type.s32(), "b"),
                FunctionParam(Type.s32(), "c"),
                FunctionParam(Type.s64(), "value"),
            ],
            params_known=True,
        )

        abi = Sh2Arch().function_abi(signature, {}, for_call=False)

        self.assertEqual(
            [(slot.loc.reg, slot.loc.offset) for slot in abi.arg_slots],
            [
                (Register("r4"), None),
                (Register("r5"), None),
                (Register("r6"), None),
                (Register("r7"), None),
                (None, 0),
            ],
        )
