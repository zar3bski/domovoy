Use an existing key pair or generate one following the [documentation](https://www.wireguard.com/quickstart/). You can add `peers` directly in the inventory. 

```yaml
wireguard-servers:
  hosts:
    magellan:
      PublicKey: <key>
      PrivateKey: <key>
      WG_PORT: 4119
      peers: 
        - name: some_client
          PublicKey: <key>
          AllowedIPs: 10.10.10.2/32
```

This set up forwards packets from `eth0` `wg0` both ways and relies on **MASQUERADE**. See `roles/wireguard/templates/add-nat-routing.sh.j2` and `roles/wireguard/templates/remote-nat-routing.sh.j2` for details. 