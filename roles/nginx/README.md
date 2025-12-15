# Nginx

Simple reverse proxy

## Compatible Systems

- Debian based
- Archlinux

## Configuration

```yaml
lan-server:
  hosts:
    some.host.lan:
        ssl_key: |
           <SSL KEY>
        ssl_cert: |
           <SSL CERT>
        reverse_proxy: # http services listening on localhost 'port' will be exposed through <service_name>.<inventory_hostname>  
          - service_name: grafana
            port: 3000
          - service_name: technitium
            port: 5380
```

## Services exposition

:443