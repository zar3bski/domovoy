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

if [[ $# -lt 0 ]]; then
  printf "usage:\n generate_ssl_cert.sh <target server FQDN> [intermediate]\n"
  exit 1
fi

# Check that script runs with the right privileges

if [ $UID != 0 ]; then
  echo "Script should run as root"
  exit 1
fi

# Check that CA keys and cert are present on the system

if [ ! -e "$CA_KEY" ]; then
  echo "CA key could not be found $CA_KEY"
  exit 1
fi

# Check that CA keys and cert are present on the system

if [ ! -e "$CA_CERT" ]; then
  echo "CA cert could not be found at $CA_CERT"
  exit 1
fi

#

mkdir -p .certs
cd .certs

echo "Generating Key for $1"
openssl genrsa -out $1.key 4096

echo "Generating Certificate Signing Request for $1"
openssl req -new -key $1.key -out $1.csr

if [ $2 == "intermediate" ]; then
  echo "Generating intermediate certificate (3650j)"
  rm ia.ext || echo "setting basicConstraints=CA:TRUE"
  echo "basicConstraints=CA:TRUE" >ia.ext
  openssl x509 -req -sha256 -days 3650 -in $1.csr -CA $CA_CERT -CAkey $CA_KEY -set_serial 01 -out $1.crt -extfile ia.ext
  rm ia.ext
  cat $1.crt $CA_CERT >$1-chain.crt
else
  echo "Generating leaf certificate (365j)"
  echo subjectAltName = DNS:$1,DNS:*.$1,DNS:$1:8080,DNS:*.$1:8080,DNS:$1:4443,DNS:*.$1:4443,DNS:$1:8443,DNS:*.$1:8443 >extfile.cnf
  openssl x509 -req -in $1.csr -CA $CA_CERT -CAkey $CA_KEY -CAcreateserial -out $1.crt -days 365 -extfile extfile.cnf
  cat $1.crt $CA_CERT >$1-chain.crt
fi
