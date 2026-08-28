#!/bin/sh
set -eu

optimization=${1:-O1}
case "$optimization" in
    O0) optimize=0 ;;
    O1) optimize=1 ;;
    *)
        echo "unsupported optimization level: $optimization (SHC has -optimize=0 and =1)" >&2
        exit 2
        ;;
esac

test -f /work/input.c

rm -rf /tmp/shc-compile
mkdir -p /tmp/shc-compile
cp -a /opt/shc/bin/. /tmp/shc-compile/
sed -e 's/\r$//' -e 's/$/\r/' /work/input.c > /tmp/shc-compile/input.c

cd /tmp/shc-compile

SHC_LIB=. SHC_TMP=. wibo ./shc.exe input.c \
    -comment=nonest \
    -cpu=sh4 \
    -division=cpu \
    -endian=little \
    -fpu=single \
    -macsave=0 \
    -sjis \
    -string=const \
    "-optimize=$optimize" \
    -speed \
    -aggressive=2 \
    -code=asmcode

test -s input.src || {
    echo "shc produced no assembly" >&2
    exit 1
}

sed 's/\r$//' input.src > /work/output.src
