#!/bin/sh

# Generates and intermediary CA bundle for internal cluster communication
# signed with the server CA. 
# Produces a ready to use secret at /etc/ssl/private/ca-cluster-internal.yml, 
# ready to be loaded into the cluster

TMP_FOLDER=/tmp/$(openssl rand -hex 8)
CA_CRT_LOCATION=/var/lib/rancher/k3s/server/tls/server-ca.crt
CA_KEY_LOCATION=/var/lib/rancher/k3s/server/tls/server-ca.key
DESTINATION=$1

if [ -z "${DESTINATION}" ]; then
    printf "usage: \n
    k3s-generate-internal-tls-bundle <destination_file>\n"
    exit 1
fi

umask 027

mkdir $TMP_FOLDER
cd $TMP_FOLDER

openssl genrsa -out intermediary.key 4096
openssl req -new -key intermediary.key -out intermediary.csr -subj "/CN=k3s-ca-internal/O=CCC"
openssl x509 -req -in intermediary.csr -CA $CA_CRT_LOCATION \
 -CAkey $CA_KEY_LOCATION -CAcreateserial -out intermediary.crt -days 3650 -extensions v3_ca \
 -extfile <(printf "[v3_ca]\nbasicConstraints=critical,CA:TRUE,pathlen:0\nkeyUsage=critical,keyCertSign,cRLSign\nsubjectKeyIdentifier=hash\nauthorityKeyIdentifier=keyid:always")

CA_B64=$(cat $CA_CRT_LOCATION | base64 -w0)
KEY_B64=$(cat intermediary.key | base64 -w0)
CRT_B64=$(cat intermediary.crt | base64 -w0)

cat >$DESTINATION <<EOL
apiVersion: v1
kind: Secret
metadata:
  name: ca-cluster-internal
  namespace: kube-system
data:
  ca.crt: ${CA_B64}
  tls.key: ${KEY_B64}
  tls.crt: ${CRT_B64}
EOL

cd /
rm -r $TMP_FOLDER

exit 0
