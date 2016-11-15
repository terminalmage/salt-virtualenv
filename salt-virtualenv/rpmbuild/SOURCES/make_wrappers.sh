#!/usr/bin/env sh

function _usage {
    echo "USAGE: make_wrappers.sh -b bindir -v virtualenv -w 'wrapper1 wrapper2 wrapper3...' [-p py_version] [-m mode]" 1>&2
    exit 1
}

# Defaults
py_version=2.7
mode="0755"

while getopts b:v:w:p:m: opt; do
    case "$opt" in
        b) bindir=$OPTARG ;;
        v) virtualenv_path=$OPTARG ;;
        w) wrappers=$OPTARG ;;
        p) py_version=$OPTARG ;;
        m) mode=$OPTARG ;;
        *) _usage
    esac
done

test -z "$bindir" && _usage
test -z "$virtualenv_path" && _usage

echo -n "making ${bindir}... "
mkdir -p "$bindir" || exit 1
echo done

for wrapper in $wrappers; do
    full_path="${bindir}/${wrapper}"
    echo -n "making ${full_path}... "
    cat <<@EOF >"$full_path"
#!/bin/sh

export PYTHONPATH=${virtualenv_path}/lib/python${py_version}/site-packages:/usr/lib/python${py_version}/site-packages:/usr/lib64/python${py_version}/site-packages

${virtualenv_path}/bin/python ${virtualenv_path}/bin/$wrapper "\$@"

exit \$?
@EOF
    test "$?" -eq 0 || exit 1
    echo done
    chmod $mode "$full_path" || exit 1
done
