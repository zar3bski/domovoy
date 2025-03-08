
# OpenMediaVault

This is a two folds playbook. 

The ****install** part installs Openmediavault on a bare Debian instance detecting if keyring has already been imported. This entire section, used in ARM context (to this day, OMV does not provide an .iso for ARM architectures) can be commented if using the [Dedicated Drive]{https://docs.openmediavault.org/en/stable/installation/via_iso.html} variant.

The **configure** part sets a RAID volume up, installs a few plugins and sets a node exporter. However, the settings of volumes, services and users should be performed through the interface.

## Configuration

```yaml
some_host:
  raid5_devices: 
    - /dev/vdb 
    - /dev/vdc 
    - /dev/vdd
```

