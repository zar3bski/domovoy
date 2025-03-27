Use an existing key pair or generate one following the [documentation](https://www.wireguard.com/quickstart/). You can add `peers` directly in the inventory. 

```yaml
wireguard-servers:
  hosts:
    magellan:
      wireguard:
        - interface: wg0  # Interface conf for server
          IP: 10.10.10.1/24
          PublicKey: <key> # wireguard
          PrivateKey: <key>
          WG_PORT: 5119
          peers: 
            - name: some_dude
              PublicKey: <key>
              AllowedIPs: 10.10.10.2/32
        - interface: wg1 # Interface conf for client
          IP: 69.69.69.2/24
          PrivateKey: <key>
          PublicKey: <key>
          peers:
            - name: some_WANserver
              PublicKey: <key>
              AllowedIPs: 69.69.69.1/24
              Endpoint: 88.88.88.88:9149
```

This role can set multiples interfaces up. Depending on the presence of `WG_PORT`, the configured interface will act as a server or a client.  

In server mode, packets forwarding is set between `eth0` and `wg?` both ways and relies on **MASQUERADE**. See `roles/wireguard/templates/add-nat-routing.sh.j2` and `roles/wireguard/templates/remote-nat-routing.sh.j2` for details. 