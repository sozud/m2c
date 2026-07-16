? LC0();                                            /* static */

s64 _test(s32 value) {
    s32 temp_r4;

    temp_r4 = value + value;
    return ((temp_r4 - temp_r4) - M2C_CARRY((value + value))) + 1 + M2C_CARRY((value + 0x23456789 + 0));
}
