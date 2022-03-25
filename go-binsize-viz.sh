#!/usr/bin/env bash

# general variables.
ESC="\x1b["
RESET=$ESC"39;49;00m"
RED=$ESC"31;01m"
GREEN=$ESC"32;01m"
YELLOW=$ESC"33;01m"
MAGENTA=$ESC"35;01m"

script_name=$0
binary=""
tmpdir=$(mktemp -d)

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
			printf "$(date "+%F %H:%M:%S") ${RED} %s${RESET}\n" "entered an invalid option"
			help
			exit 1
			;;
		:)
			printf "$(date "+%F %H:%M:%S") ${RED} %s${RESET}\n" "Option $OPTARG requires an argument"
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
	printf "$(date "+%F %H:%M:%S") ${GREEN} %s${RESET}\n" "running go tool on ${binary}"
	go tool nm -size "${binary}" | c++filt >${tmpdir}/symtab.txt 2>&1
	python3 ./tab2pydic.py ${tmpdir}/symtab.txt >${tmpdir}/out.py 2>&1
	python3 ./simplify.py ${tmpdir}/out.py >${tmpdir}/data.js 2>&1
}

copy_resources() {
	printf "$(date "+%F %H:%M:%S") ${GREEN} %s${RESET}\n" "copy resources to ${tmpdir}"
	cp -r ./js ${tmpdir}/app3.js
	cp -r ./app3.js ${tmpdir}/app3.js
}

check_and_exist() {
	local status=$1
	local message=$2

	if [ $status -ne 0 ]; then
		printf "$(date "+%F %H:%M:%S") ${RED} %s${RESET}\n" "status code $1 message: $message"
		exit $status
	fi
}

main_getopts "$@"

printf "$(date "+%F %H:%M:%S") ${GREEN} %s${RESET}\n" "using tmpdir $tmpdir"
#
generate_data_file
check_and_exist "$?" "could not generate data files"

copy_resources
check_and_exist "$?" "could not copy resource files"

{
	printf "$(date "+%F %H:%M:%S") ${GREEN} %s${RESET}\n" "starting http.server in ${tmpdir}"
	cd ${tmpdir}
	python3 -m http.server
}
