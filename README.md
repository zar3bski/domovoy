![Ansible](https://img.shields.io/badge/ansible-%231A1918.svg?style=for-the-badge&logo=ansible&logoColor=white)

# Domovoy
Home infrastructure for nerds envisioning to live off grid. Most daily services internalized.

## Usage

### Create a virtual environment and activate it

```shell
python -m venv .ASI_VENV
source ./.ASI_VENV/bin/activate
```

### Install dependencies

```shell
pip3 install -r requirements.txt
```

### Create your **inventory.yml** according to `site.yml` , for example

```yaml
nym-servers:
  hosts:
    somehost.lan
```

and

```shell
ansible-playbook -i inventory.yml site.yml
```

### Generate server's SSL cert based on a local CA

```shell
./scripts/generate_ssl_cert.sh some_domain.lan
```

certs and keys will appear in `.certs`

### Limitations

- Designed for Debian based servers
- rely on [UFW](https://github.com/jbq/ufw)

## Users accros the infra

|  PID | name         | Description                                 |
| ---: | :----------- | :------------------------------------------ |
| 1001 | metrics      | account used for every prometheus exporters |
| 1002 | grafana      |                                             |
| 1003 | prometheus   |                                             |
| 1004 | nym          | runs all Nym service                        |
| 1005 | gh-runner    | Github runner service account               |
| 1006 | alertmanager | Prometheus altermanager                     |


## Inventory Data Model

```yaml
<Role name>:
  hosts:
    <host name>:
      knock_ports: opt. list[int] # port sequence to set port knocking 
      ssh_keys: opt. list[str] # additional ssh keys to be happened to sudoer's authorized_keys
```


## Services

> all technical users running the various services are limited to a restricted shell (a.k.a. `/bin/rbash`) exept for **gh-runner**

### Nginx 

see [roles/nginx/README.md](roles/nginx/README.md) for details

### Github runner

see [roles/gh-runner/README.md](roles/gh-runner/README.md) for details

### Open Media Vault

see [roles/openmediavault/README.md](roles/openmediavault/README.md) for details

### Technitium

see [roles/technitium/README.md](roles/technitium/README.md) for details

### Wireguard

see [roles/wireguard/README.md](roles/technitium/README.md) for details

### Prometheus + Grafana + Alertmanager

see [roles/prometheus/README.md](roles/prometheus/README.md) for details

### Nym node

See [this doc](https://nymtech.net/) for details

### Port Knocking

This playbook allow the user to secure any host's sshd service using [knockd](https://github.com/jvinet/knock). To set a series of ports, simply add a `knock_ports` for this host in the **inventory.yml**

```yaml
nym-servers:
  hosts:
    some.host.com:
      knock_ports: 
        - 1
        - 2 
        - 3 
```

When set, ssh service is no longer visible

```shell
@ nmap some.host.com -Pn                             
    Starting Nmap 7.93 ( https://nmap.org ) at 2024-08-09 15:24 CEST
    Nmap scan report for some.host.com (192.168.1.59)
    Host is up (0.00032s latency).
    Not shown: 997 filtered tcp ports (no-response)
    PORT     STATE  SERVICE
    8080/tcp open   http-proxy
...
```

Except after providing the right sequence

```shell
@ knock some.host.com 1 2 3
@ nmap some.host.com -Pn                             
    Starting Nmap 7.93 ( https://nmap.org ) at 2024-08-09 15:24 CEST
    Nmap scan report for some.host.com (192.168.1.59)
    Host is up (0.00032s latency).
    Not shown: 997 filtered tcp ports (no-response)
    PORT     STATE  SERVICE
    22/tcp   open   ssh
    8080/tcp open   http-proxy
...
```

This playbook handles knocking using `roles/common/knocking.yml`. This involves to had it as **pre_tasks** and to disable `gather_facts`, for it is performed at module initialization

```yaml
  gather_facts: false
  pre_tasks:
    - name: Import pre_tasks
      ansible.builtin.import_tasks: 'roles/common/knocking.yml'
```

