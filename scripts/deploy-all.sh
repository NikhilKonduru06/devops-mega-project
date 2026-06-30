#!/bin/bash
set -e

echo "==> Step 1: Provisioning AWS infrastructure with Terraform"
cd terraform
terraform init
terraform apply -auto-approve
cd ..

echo "==> Step 2: Configuring kubectl to talk to the new EKS cluster"
CLUSTER_NAME=$(cd terraform && terraform output -raw cluster_name)
AWS_REGION=$(cd terraform && terraform output -raw region)
aws eks update-kubeconfig --region "$AWS_REGION" --name "$CLUSTER_NAME"

echo "==> Step 3: Installing ArgoCD"
bash scripts/install-argocd.sh

echo "==> Step 4: Applying the ArgoCD Application (this triggers GitOps sync)"
kubectl apply -f argocd/application.yaml

echo "==> Done! ArgoCD will now sync your app from Git into the cluster automatically."
echo "==> Check status with: kubectl get pods -n devops-project"
