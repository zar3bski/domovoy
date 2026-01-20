## Storage

Additional cold storage / volumes

```yaml
    some.host.lan:
      storage:
        btrfs:
          - name: volume1 # mount point in /srv
            uuid: 7dfc0a29-4dea-4dc7-a911-986ee7f35be6
            ssd: false
            power_setting: 127 # optional
            timeout: 180 # optional
```

Identify btrfs volume UUID with

```shell
sudo btrfs filesystem show
Label: none  uuid: 7dfc0a29-4dea-4dc7-a911-986ee7f35be6 # UUID
    Total devices 2 FS bytes used 4.36TiB
    devid    1 size 10.91TiB used 4.72TiB path /dev/sda
    devid    2 size 10.91TiB used 4.72TiB path /dev/sdb
```
