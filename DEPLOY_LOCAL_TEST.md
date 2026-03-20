# Local Manual Deploy Test

1. Build/push image
```bash
./scripts/ecr_push.sh
```

2. Create service env secret from .env
```bash
kubectl -n stagelog create secret generic <SECRET_NAME> \
  --from-file=.env=.env \
  --dry-run=client -o yaml | kubectl apply -f -
```

3. Apply manifests
```bash
kubectl apply -f deploy/k8s/
```

4. Rollout check
```bash
kubectl -n stagelog get deploy,svc,pods
kubectl -n stagelog rollout status deploy/<DEPLOYMENT_NAME>
kubectl -n stagelog logs deploy/<DEPLOYMENT_NAME> --tail=200
```
