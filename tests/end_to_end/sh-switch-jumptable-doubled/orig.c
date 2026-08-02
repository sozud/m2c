int test(short *values, int result) {
    int highest = 0;
    int i;

    for (i = 1; i < 4; i++) {
        if (values[i] > values[highest]) {
            highest = i;
        }
    }

    values[highest] = result;
    switch (highest) {
    case 0:
        result += 3;
        break;
    case 1:
        result += 5;
        break;
    case 2:
        result += 7;
        break;
    case 3:
        result += 11;
        break;
    }
    return result;
}
