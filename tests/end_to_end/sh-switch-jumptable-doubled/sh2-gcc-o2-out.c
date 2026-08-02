s16 test(s32 arg0, s16 arg1) {
    s16 var_r6;
    s32 var_r3;
    s32 var_r5;
    s32 var_r7;
    u32 temp_r2;

    var_r6 = arg1;
    var_r5 = 0;
    var_r3 = 1;
    var_r7 = 2;
    do {
        if (*(arg0 + var_r7) > *(arg0 + (var_r5 * 2))) {
            var_r5 = var_r3;
        }
        var_r3 += 1;
        var_r7 += 2;
    } while (var_r3 <= 3);
    temp_r2 = var_r5 * 2;
    *(arg0 + temp_r2) = var_r6;
    if ((u32) var_r5 <= 3U) {
        switch (temp_r2 >> 1U) {
        case 0:
            var_r6 += 3;
            break;
        case 1:
            var_r6 += 5;
            break;
        case 2:
            var_r6 += 7;
            break;
        case 3:
            var_r6 += 0xB;
            break;
        }
    }
    return var_r6;
}
