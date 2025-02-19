
> This stack is not supposed to be exposed publicly


> These 3 services can only live on the same node because they share a docker network

```yaml
prometheus-servers:
  hosts:
    some.host.com:
      alert_webhook_url: https://discordapp.com/ # Discord webhook
      grafana_admin: <some_password>  # admin password
      dashboards: # dashboard to be installed
        - https://grafana.com/api/dashboards/1860/revisions/37/download
```

Services exposition

Grafana: Host port 3000

