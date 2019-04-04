#!/usr/bin/env bash

# Colors
esc_seq="\x1b["
col_reset=$esc_seq"39;49;00m"
col_red=$esc_seq"31;01m"
col_green=$esc_seq"32;01m"
col_yellow=$esc_seq"33;01m"
col_blue=$esc_seq"34;01m"
col_magenta=$esc_seq"35;01m"
col_cyan=$esc_seq"36;01m"

# marks
check_mark="\xE2\x9C\x94"
error_mark="-"

script_name=$0
binary=""
tmpdir=$(mktemp -d)
# scripts

help() {
    cat <<EOF
usage: ${script_name} [-h] [-b]

  -b: binary

e.g:
${script_name} -b hello-world
EOF
}

main_getopts() {

    while getopts "b:h" opt; do
        case $opt in
        "b") binary=$OPTARG ;;
        "h")
            help
            exit 0
            ;;
        \?)
            echo -e "$col_red entered an invalid option $col_reset"
            help
            exit 1
            ;;
        :)
            echo -e "$col_red Option $OPTARG requires an argument $col_reset"
            help
            exit 1
            ;;
        esac
    done
    shift $((OPTIND - 1))

    if [ $OPTIND -eq 1 ]; then
        help
        exit 0
    fi

    [ -z "$binary" ] && echo "-b is mandatory" && help && exit 1
    [ ! -f "$binary" ] && echo "$binary is not a file" && help && exit 1

}

generate_data_file() {
    echo "tmpdir: ${tmpdir}"
    go tool nm -size ${binary} | c++filt >${tmpdir}/symtab.txt
    python3 /home/go-binsize-viz/lib/tab2pydic.py ${tmpdir}/symtab.txt >${tmpdir}/out.py
    python3 /home/go-binsize-viz/lib/simplify.py ${tmpdir}/out.py >${tmpdir}/data.js
}

copy_resources() {
    echo "copy resources to ${tmpdir}"
    cp -r /home/go-binsize-viz/templates/* ${tmpdir}
}

check_and_exist() {
    local status=$1
    local message=$2

    if [ $status -ne 0 ]; then
        echo "status code $1 message: $message"
        exit $status
    fi
}

main_getopts "$@"

generate_data_file
check_and_exist "$?" "could not generate data files"

copy_resources
check_and_exist "$?" "could not copy resource files"

{
    echo "starting http.server in ${tmpdir}"
    cd ${tmpdir}
    python3 -m http.server
}
