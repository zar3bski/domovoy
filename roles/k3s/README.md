## Compatible Systems

- Ubuntu
- Alpine

```yaml
  hosts:
    some.host.lan:
      cluster_ca_key: <intermediary key to be used as Cluster CA> # Must be CA:True
      cluster_ca_cert: <intermediary cert to be used as Cluster CA> # Must be CA:True
```
