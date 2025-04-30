#!/bin/bash
#
# generate and sign leaf SSL cert from intermediary certificate

## Extraction
intermediary_cert="/etc/ssl/certs/omv-intermediary.crt"
intermediary_key="/etc/ssl/private/omv-intermediary.key"

leaf_cert="/etc/ssl/certs/omv.crt"
leaf_key="/etc/ssl/private/omv.key"

generation=$(tr -dc 'a-zA-Z0-9' </dev/urandom | fold -w 16 | head -n 1)
csr_path="/tmp/${generation}.csr"
cnf_path="/tmp/${generation}_extfile.cnf"

subject=$(openssl x509 -inform PEM -in $intermediary_cert -noout -subject -nameopt compat | sed 's/subject=//')
if [ "${subject}" == "" ]; then
    echo "Failed to extract subject from intermediary certificate $intermediary_cert"
    exit 1
fi

CN=$(openssl x509 -in $intermediary_cert -noout -subject -nameopt multiline |
    grep commonName | awk '{ print $3 }')
if [ "${CN}" == "" ]; then
    echo "Failed to extract Common Name (CN) from intermediary certificate $intermediary_cert"
    exit 1
fi

## Generation

echo "Generating Key: $leaf_key"
rm -f $leaf_key
openssl genrsa -out $leaf_key 4096
chmod 400 $leaf_key

echo "Generating Certificate Signing Request for $leaf_cert"
rm -f $csr_path
openssl req -new -key $leaf_key -out $csr_path -subj "${subject}"

echo subjectAltName = DNS:$CN,DNS:*.$CN >$cnf_path

echo "Generating certificate: $leaf_cert signed with $intermediary_cert and $intermediary_key"
openssl x509 -req -in $csr_path -CA $intermediary_cert -CAkey $intermediary_key -CAcreateserial -out $leaf_cert -days 365 -extfile $cnf_path

exit 0
