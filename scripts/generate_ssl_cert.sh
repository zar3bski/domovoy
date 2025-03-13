#!/bin/bash
# 
# Generate server SSL cert and key signed by pre-existing local CA
# The subjectAltName is determined by the provided domain name
# usage:
#   generate_ssl_cert.sh <target server FQDN>
#
#


CA_KEY=/etc/ssl/private/sin-ca-key.pem
CA_CERT=/etc/ssl/certs/sin-ca-cert.pem

# Check that target server FQDN was provided

if [[ $# -gt 0 ]] 
then
    echo "Generating cert and key for $1"
else
    printf "usage:\n generate_ssl_cert.sh <target server FQDN>\n"
    exit 1;
fi  

# Check that script runs with the right privileges

if [ $UID != 0 ] 
then
  echo "Script should run as root";
  exit 1;
fi  

# Check that CA keys and cert are present on the system

if [ ! -e "$CA_KEY" ] 
then
  echo "CA key could not be found $CA_KEY";
  exit 1;
fi  

# Check that CA keys and cert are present on the system

if [ ! -e "$CA_CERT" ] 
then
  echo "CA cert could not be found at $CA_CERT";
  exit 1;
fi  

# 

mkdir -p .certs
cd .certs

openssl genrsa -out $1-key.pem 2048
openssl req -new -key $1-key.pem -out $1.csr
echo subjectAltName = DNS:$1,DNS:*.$1 > extfile.cnf


openssl x509 -req -in $1.csr -CA $CA_CERT -CAkey $CA_KEY -CAcreateserial -out $1-cert.pem -days 365 -extfile extfile.cnf

cat $1-cert.pem $1-key.pem > $1.pem

