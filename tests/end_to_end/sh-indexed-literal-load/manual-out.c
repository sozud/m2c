? base();                                           /* static */
? base_negative();                                  /* static */
? offset();                                         /* static */
? offset_negative();                                /* static */

s8 test(void) {
    return *(s8 *)0x06001010;
}

s8 test_negative(void) {
    return *(s8 *)0x06001010;
}

s8 test_dynamic(s8 *base, s32 offset) {
    return base[offset];
}
