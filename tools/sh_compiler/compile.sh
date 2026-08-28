#!/bin/sh
set -eu

optimization=${1:-O0}
case "$optimization" in
    O0|O1|O2|O3) ;;
    *)
        echo "unsupported optimization level: $optimization" >&2
        exit 2
        ;;
esac

input=${2:-input.c}
case "$input" in
    input.c|input.i) ;;
    *)
        echo "unsupported input filename: $input" >&2
        exit 2
        ;;
esac

test -f "/work/$input"
rm -rf /tmp/sh-compile
mkdir -p /tmp/sh-compile/.dosemu
cp -a /opt/gccsh/. /tmp/sh-compile/
cp "/work/$input" "/tmp/sh-compile/$input"

cat > /tmp/sh-compile/dosemurc <<'EOF'
$_cpu_vm = "emulated"
$_cpu_vm_dpmi = "emulated"
$_sound = (off)
$_hogthreshold = (0)
$_pci = (off)
$_rdtsc = (off)
$_term_color = (off)
$_ipxsupport = (off)
$_pktdriver = (off)
EOF

cd /tmp/sh-compile
if [ "$input" = input.i ]; then
    compiler_command="GCC.EXE -S -${optimization} -m2 -dp -fsigned-char input.i -o output.s"
else
    compiler_command="GCC.EXE -S -${optimization} -m2 -dp -fsigned-char input.c -o output.s"
fi
HOME=/tmp/sh-compile dosemu -quiet -dumb -f ./dosemurc -K . \
    -E "$compiler_command"

if [ -s output.s ]; then
    compiler_output=output.s
elif [ -s OUTPUT.S ]; then
    compiler_output=OUTPUT.S
else
    echo "$input compiler path did not produce output.s" >&2
    exit 1
fi

sed 's/[[:space:]]*;#.*$//' "$compiler_output" > /work/output.s
