![Ansible](https://img.shields.io/badge/ansible-%231A1918.svg?style=for-the-badge&logo=ansible&logoColor=white)

# Domovoy
Home infrastructure for nerds envisioning to live off grid. Most daily services internalized.

## Usage

### Create a virtual environment and activate it

```shell
python -m venv --copies .ASI_VENV
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

### Create vault.yml and its .vault_pass

You might not want some sensitive values to live in clear format in your inventory. For these variable, simply populate a `vault.yml` with the following command

```shell
ansible-vault create vault.yml
```

write the password you choose in `.vault_pass`

```shell
echo '<your password>' > .vault_pass
chmod 600 .vault_pass
```

### Generate server's SSL cert based on a local CA

```shell
./scripts/generate_ssl_cert.sh some_domain.lan
```

certs and keys will appear in `.certs`

### Architectural choices

- All firewalling is handled with `nftables` to avoid frontend disparities (e.g. ufw VS firewalld) across the different distributions
- Distros assumed to use SE-Linux: **Fedora**
- Distros assumed to use AppArmor: **Debian** (and derivatives), Arch Linux

## Users across the infra

|  PID | name         | Description                                 |
| ---: | :----------- | :------------------------------------------ |
| 62001| metrics      | account used for every prometheus exporters |
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

> all technical users running the various services are limited to a restricted shell (a.k.a. `/bin/rbash`) except for **gh-runner**. Some roles only support **Debian based systems** while others also work on other distributions (mainly **Archlinux**). Please refer to the roles' `README` to check for compatibility.

### Nginx 

see [roles/nginx/README.md](roles/nginx/README.md) for details

### Github runner

see [roles/gh-runner/README.md](roles/gh-runner/README.md) for details

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

This playbook handles knocking using `roles/common/knocking.yml`. This involves to add it as **pre_tasks** and to disable `gather_facts`, for it is performed at module initialization

```yaml
  gather_facts: false
  pre_tasks:
    - name: Import pre_tasks
      ansible.builtin.import_tasks: 'roles/common/knocking.yml'
```

