## Compatible Systems

- Debian based
- Archlinux

## Configuration

Simply add 

```yaml
technitium-servers:
  hosts:
    magellan:
      admin_password: <your admin password>
```
to your inventory


## Service exposition

This role exposes the following ports

- 5380: Technitium Administration interface
- 53: DNS service

