# Nginx

Simple reverse proxy

```yaml
lan-server:
  vars:
    dns_zone: some.lan
  hosts:
    some.host.com:
        ssl_key: |
           <SSL KEY>
        ssl_cert: |
           <SSL CERT>
```

## Services exposition

:443