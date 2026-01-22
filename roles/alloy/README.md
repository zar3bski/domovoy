# Alloy

## Compatible Systems

- Debian based
- RedHat based

## Configuration

Parse local logs to be sent to a Loki instance 

```yaml
lan-server:
  hosts:
    some.host.lan:
        loki_url: https://url.to.loki.instance
        loki_pass: <password_of_user_"loki"> # Basic auth
```