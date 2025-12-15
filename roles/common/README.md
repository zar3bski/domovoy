## Compatible Systems

- Debian based
- Archlinux

> On Arch linux, for Apparmor activation after the first playbook execution, you will need to restart the server after the task **Check that apparmor is running** fails before running the playbook again

```yml
    some.host.lan:
      nics:  # Set permanent network interface names
        - name: eth0 
          mac: 2c:cf:67:26:cd:e4
```