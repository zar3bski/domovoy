

Initial manifest generation from Helm chart

```shell
kustomize build -o external-secret-operator/build.yml --enable-helm ./external-secret-operator
```