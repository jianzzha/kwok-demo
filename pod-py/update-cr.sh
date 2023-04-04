#!/bin/bash - 
print_usage() {
    echo "Usage: $0 <num> [<interval>]"
}

if [[ "$#" -ne 2 ]] && [[ "$#" -ne 1 ]]; then
    print_usage
    exit 1
fi

if [[ "$#" -eq 2 ]]; then
    if ! [[ "$1" =~ ^[0-9]+$ ]] || ! [[ "$2" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
        print_usage
        exit 1
    fi
    interval="$2"
fi

if [[ "$#" -eq 1 ]]; then
    if ! [[ "$1" =~ ^[0-9]+$ ]]; then
	print_usage
	exit 1
    fi
    interval=0
fi

for (( i=1; i<=$1; i++ )); do
    oc patch mycustomresources.example.com my-custom-resource --type merge -p "{\"spec\":{\"data\":\"du$i\"}}"
    if [[ "${interval}" != "0" ]]; then
        sleep ${interval}
    fi
done
