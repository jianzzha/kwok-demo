#!/bin/bash - 
#===============================================================================
#
#          FILE: nodes.sh
# 
#         USAGE: ./nodes.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Jianzhu Zhang (), jianzzha@redhat.com
#  ORGANIZATION: NFV Perf
#       CREATED: 03/25/2023 01:19:55 PM
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

print_usage() {
    echo "Usage: $0 <create|delete> <num_start> <num_end>"
}

if [[ "$#" -ne 3 ]]; then
    print_usage
    exit 1
fi

action=$1
num_start=$2
num_end=$3

if [[ "$action" != "create" && "$action" != "delete" ]]; then
    print_usage
    exit 1
fi

if ! [[ "$num_start" =~ ^[0-9]+$  && "${num_end}" =~ ^[0-9]+$ ]]; then
    print_usage
    exit 1
fi

for (( i=num_start; i<=num_end; i++ )); do
    if [[ ${action} == "create" ]];  then
         NODE=$i CPU=$i envsubst < nodes.yaml | kubectl apply -f -
    elif [[ ${action} == "delete" ]]; then
	 NODE=$i CPU=$i envsubst < nodes.yaml | kubectl delete -f -
    fi
done
