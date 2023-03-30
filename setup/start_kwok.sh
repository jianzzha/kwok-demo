#!/bin/bash - 
#===============================================================================
#
#          FILE: start_kwok.sh
# 
#         USAGE: ./start_kwok.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Jianzhu Zhang (), jianzzha@redhat.com
#  ORGANIZATION: NFV Perf
#       CREATED: 03/25/2023 02:18:06 PM
#      REVISION:  ---
#===============================================================================

sudo podman run --rm -it -p 8080:8080 registry.k8s.io/kwok/cluster:v1.26.0

