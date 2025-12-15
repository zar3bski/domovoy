
# OpenMediaVault

This is a two folds playbook. 

The **install** part installs Openmediavault on a bare Debian (sandworm) instance detecting if keyring has already been imported. This entire section, used in ARM context (to this day, OMV does not provide an .iso for ARM architectures) can be commented if using the [Dedicated Drive]{https://docs.openmediavault.org/en/stable/installation/via_iso.html} variant.

The **configure** part sets a RAID volume up, installs a few plugins and sets a node exporter. However, the settings of volumes, services and users should be performed through the interface.

## Compatible Systems

- Debian based

## Configuration

```yaml
some_host:
  webhook_url: https://url/of/your/discord/webhook # optional
  ca_cert: |
    -----BEGIN CERTIFICATE-----
  ssl_intermediary_key: |
     -----BEGIN PRIVATE KEY-----
  ssl_intermediary_cert: |
     -----BEGIN CERTIFICATE-----
  archive_password: some_pass # password to be used for PVC archive encryption
  raid5_devices: 
    - /dev/vdb 
    - /dev/vdc 
    - /dev/vdd
```

> NB: for Nginx to accept to use the cert generated with`ssl_intermediary_key`, the certificate must be signed by the one added to the trust store through `ca_cert`

## Installation

**first execution** (`./tasks/install.yml`) of the playbook will install openmediavault. The installation will override the existing users. For this reason, after the installation, you should log into OMV web interface and set 
1. the ssh keys of your ansible user
2. and link her to the `_ssh` group 

before running the playbook again

## Configuration

On the **second execution** (`./tasks/configure.yml`) is executed

## Decrypt archives 

```shell
decrypt archives with openssl enc -pbkdf2 -d -aes256 -in <archive>.tar.gz.aes | tar xz -C ./
```
