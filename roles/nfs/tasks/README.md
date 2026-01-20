## Compatible Systems

- Fedora

```yaml
hosts:
    some.host.lan:
      nfs:
        volume: volume1      # Volume in /srv
        shared_ro:           # folders at the root of /srv/volume1 to be exposed in read only mode
          - music
          - videos
          - readings
          - softwares
```
