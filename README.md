# playbooks
Ansible playbooks

## Services

- [nym-node]()

## Usage

Create your **inventory.yml** according to `site.yml` , for example

```yaml
nym-servers:
  hosts:
    somehost.lan
```

and

```shell
ansible-playbook -i inventory.yml site.yml
```

- Debian based servers
- rely on [UFW](https://github.com/jbq/ufw)
