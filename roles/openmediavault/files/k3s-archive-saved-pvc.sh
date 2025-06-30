#!/bin/sh

# archive all Persistent Volume Claims handled by the storageClass "saved-local-path"
# presupposes that PVCs live in /var/lib/rancher/k3s/saved_storage (i.e storageClass
# should be configured accordingly). Relies on a password stored in /root/.archive_password
#
# decrypt archives with openssl enc -pbkdf2 -d -aes256 -in <archive>.tar.gz.aes | tar xz -C ./


SAVED_PVC_FOLDER=/var/lib/rancher/k3s/saved_storage
DESTINATION=$1

if [ -z "${DESTINATION}" ]; then
    printf "usage: \n
    k3s-archive-saved-pcv.sh <destination_folder>\n"
    exit 1
fi

# get execution date
today=$(date +'%Y-%m-%d')
# find all PVC handled by the storageClassName 'saved-local-path'
saved_pvcs=$(
    kubectl get pvc -A -o json | jq '.items[] | 
 select (.spec.storageClassName == "saved-local-path") | 
 .spec.volumeName+"_"+.metadata.namespace+"_"+.metadata.name' -r
)

cd $SAVED_PVC_FOLDER

for pvc in $saved_pvcs; do
    echo "$(date +"%Y-%m-%dT%T") archiving" $pvc
    tar -cz $pvc | openssl enc -pbkdf2 -e -aes256 -pass file:/root/.archive_password -out $DESTINATION/$today-$pvc.tar.gz.aes
    echo "$(date +"%Y-%m-%dT%T")" $pvc: DONE
done
