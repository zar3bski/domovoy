

Initial manifest generation from Helm chart

```shell
kustomize build -o external-secret-operator/build.yml --enable-helm ./external-secret-operator
```

```shell
kubectl apply -k ./base/external-secret-operator --server-side
```

> Because of the size of the CRD and metadata length validation, this application has to be applied `--server-side` [source](https://github.com/external-secrets/external-secrets/releases/tag/v0.19.0) 
