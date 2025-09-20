#!/bin/bash

# Load and set SSL cert as openmediavault main certificate, apply changes
# to Nginx conf and restart Nginx
#

. /usr/share/openmediavault/scripts/helper-functions

cert="/etc/ssl/certs/omv-chain.crt"
key="/etc/ssl/private/omv.key"
uuid="757f842e-faf0-11e8-a284-3a6331353066"
subject=$(openssl x509 -inform PEM -in $cert -noout -subject -nameopt compat | sed 's/subject=//')
if [ "${subject}" == "" ]; then
    echo "Failed to extract subject from intermediary certificate $cert"
    exit 1
fi

if ! omv_isuuid "${uuid}"; then
    echo "Invalid uuid"
    exit 1
fi

if [ ! -f "${cert}" ]; then
    echo "Cert not found"
    exit 2
fi

if [ ! -f "${key}" ]; then
    echo "Key not found"
    exit 3
fi

echo "Cert file :: ${cert}"
echo "Key file :: ${key}"

xpath="/config/system/certificates/sslcertificate[uuid='${uuid}']"
echo "xpath :: ${xpath}"
echo

if ! omv_config_exists "${xpath}"; then
    echo "Config for ${uuid} does not exist: creating"
    cert_content=$(awk '{printf "%s\\n", $0}' $cert)
    key_content=$(awk '{printf "%s\\n", $0}' $key)

    omv_config_add_node_data "/config/system/certificates" "sslcertificate" \
        "<uuid>${uuid}</uuid><certificate>${cert_content}</certificate><privatekey>${key_content}</privatekey><comment>${subject}</comment>"
    echo "Config created successfully"
else
    echo "Updating certificate in database ..."
    omv_config_update "${xpath}/certificate" "$(cat ${cert})"

    echo "Updating private key in database ..."
    omv_config_update "${xpath}/privatekey" "$(cat ${key})"

    echo "Updating comment in database ..."
    omv_config_update "${xpath}/comment" "${subject}"
fi

echo "Setting TLS for webadmin interface"
omv_config_update "/config/webadmin/enablessl" 1
omv_config_update "/config/webadmin/sslcertificateref" "${uuid}"

echo "Updating certs and nginx..."
omv-salt deploy run certificates nginx

systemctl restart nginx

exit 0
