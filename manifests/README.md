
This installation step occurs after the K3s full setting on OMV (or other). Some parts of the installation process are automated (see `roles/openmediavault` for details), others are manual

## Prerequisits

### Client side
* [kubectl]()
* [helm 3]()

### Cluster side

A working **traefik** Ingress controler with its associated CRDs and a default **storage class**

## First deployment

### Deploy cert-manager

> This step presuppose that ca-cluster.yml & ca-cluster-internal.yml have been applied by the k3s playbook. If not, apply manually

```shell
kubectl apply -k base/cert-manager
```

> Because this module also install CRDS, you might get an error about `base/cert-manager/clusterissuer-ca.yml`. Wait a while, re-run the command and it should be OK

Make sure that the cluster issuer is available 

```shell
kubectl describe clusterissuer ca-clusterissuer -n cert-manager
```

### Deploy custom storage class 

```shell
kubectl apply -k ./base/storage
```

### Deploy traefik

```shell
kubectl apply -k base/network
```

### Deploy Openbao

Set `manifests/overlays/<env>/openbao/secret.env`. In case of restoration from a previous deployment, `static_seal_key` should be the same as the one used previously.

```yaml
kubectl apply -k overlays/<env>/openbao
```

> if necessary, restore the volume from a previous deployment


### Set the External Secret Manager up

```shell
kubectl apply -k overlays/<env>/external-secret-operator
```

### Create the various .env

Generate the different `.env` files from the followings `.env.example`

```shell
find ./ -name "*.env.example"
```

### Deploy

**Inspect**

```shell
kubectl kustomize ./overlays/<env>
```

**apply changes to cluster**

```shell
kubectl apply -k ./overlays/<env>
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

