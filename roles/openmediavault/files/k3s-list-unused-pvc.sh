#!/bin/bash

# Identify used and unused PVC in the current folder
#
# usage:
#     ./k3s-list-unused-pvc.sh

Green='\033[0;32m'  # Green
Yellow='\033[0;33m' # Yellow

pvcs=$(
    kubectl get pvc -A -o json | jq '.items[] | 
 .spec.volumeName+"_"+.metadata.namespace+"_"+.metadata.name' -r
)

for d in $(ls ./); do
    USED=0
    for pvc in $pvcs; do
        if [ $pvc == $d ]; then
            USED=1
        fi
    done
    if [ $USED == 1 ]; then
        printf "$Green Used  PVC: $d\n"
    else
        printf "$Yellow Unsed PVC: $d\n"
    fi
done
