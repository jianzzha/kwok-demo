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

pods=`oc get pods | awk '/Running/{print $1;}'`
for (( i=1; i<=$1; i++ )); do
    bool="false"
    if [[ $((i%2)) -eq 0 ]]; then
        bool="true"
    fi
    for pod in ${pods}; do
        oc annotate --overwrite pod ${pod} redhat.com/add-pod-name-label=${bool}
    done
    if [[ "${interval}" != "0" ]]; then
        sleep ${interval}
    fi
done
