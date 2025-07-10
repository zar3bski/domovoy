
## Github runner

```yaml
dmz-servers:
  hosts:
    cook:
      gh_runners:
        - name: <some_name>
          url: https://github.com/<some_repo>
          token: <token>
          labels: AMR64,Linux,self-hosted
        - name: <some_other_name>
          url: https://github.com/<some_other_repo>
          token: <token>
          labels: AMR64,Linux,self-hosted
```