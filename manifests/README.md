
This installation step occurs after the K3s full setting on OMV (or other). Some parts of the installation process are automated (see `roles/openmediavault` for details), others are manual

## Prerequisits

### Client side
* [kubectl]()
* [helm 3]()

### Cluster side

A working **traefik** Ingress controler with its associated CRDs and a default **storage class**

## First deployment

### Import cluster root CA

From the node, **as root**, run

```shell
kubectl apply -f /etc/ssl/private/ca-omv-cluster.yml
```

> To renew the cluster CA, you will need to run `roles/openmediavault` to generate the yml and re-execute the command 

### Create the various .env

Generate the different `.env` files from the followings `.env.example`

```shell
find ./ -name "*.env.example"
```

### Deploy

**Inspect**

```shell
kubectl kustomize ./
```

**apply changes to cluster**

```shell
kubectl apply -k ./
```

## Disaster recovery

### saved  PVC 

Persistent volume claims handled by the `storageClass` **saved-local-path**. `k3s-archive-saved-pvc` (provisioned by ansible) should be used in a CRON job to save those PVC on a different volume. 

Encrypted archives can be decrypted + extracted using

```shell
openssl enc -pbkdf2 -d -aes256 -in name_of_the.tar.gz.aes  | tar -xz
```
to provide password from STDIN or with 

```shell
openssl enc -pbkdf2 -d -pass file:/path/to/.archive_password -aes256 -in name_of_the.tar.gz.aes  | tar -xz
```

