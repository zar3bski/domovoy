## Compatible Systems

- Debian based
- Archlinux
- Fedora

## Configuration

Simply add 

```yaml
technitium-servers:
  hosts:
    some.host:
      monitor_btrfs: <true|false>
      prometheus_fetch_passwd: <password> # BASIC_AUTH password to be used by prometheus with user 'prom'
      
```
to your inventory


## Service exposition

This role exposes the following ports

- 9101
