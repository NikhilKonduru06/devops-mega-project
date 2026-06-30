# DevOps To-Do App — End-to-End CI/CD on AWS EKS with GitOps

A simple Flask To-Do application used as a vehicle to demonstrate a complete, production-style DevOps workflow: containerization, infrastructure as code, CI/CD automation, and GitOps-based deployment to Kubernetes on AWS.

## Architecture

```
Developer Push → GitHub Actions (CI) → Docker Hub → Git Manifest Update → ArgoCD (CD) → AWS EKS
```

1. Code is pushed to GitHub.
2. GitHub Actions runs tests, builds a Docker image, and pushes it to Docker Hub.
3. GitHub Actions updates the image tag in the Kubernetes manifest and commits it back to the repo.
4. ArgoCD detects the Git change and automatically syncs the new version into the EKS cluster (GitOps).
5. The AWS Load Balancer Controller exposes the app via an Application Load Balancer (Ingress).

## Tech Stack

| Layer                  | Tool                          |
|-------------------------|-------------------------------|
| Application             | Python (Flask)                 |
| Containerization         | Docker                         |
| Infrastructure as Code   | Terraform (VPC + EKS)          |
| Configuration Management | Ansible (optional, see `scripts/`) |
| CI                       | GitHub Actions                 |
| CD / GitOps              | ArgoCD                          |
| Orchestration             | Kubernetes (AWS EKS)            |
| Scripting                 | Bash                            |

## Repository Structure

```
.
├── app/                    # Flask application source code
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── templates/
├── k8s/                    # Kubernetes manifests (watched by ArgoCD)
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── hpa.yaml
├── terraform/              # AWS infra: VPC + EKS cluster
│   ├── provider.tf
│   ├── variables.tf
│   ├── vpc.tf
│   ├── eks.tf
│   └── outputs.tf
├── argocd/
│   └── application.yaml    # ArgoCD Application definition (GitOps)
├── .github/workflows/
│   └── ci-cd.yaml          # CI/CD pipeline
├── scripts/
│   ├── install-argocd.sh
│   └── deploy-all.sh
└── docker-compose.yml      # For local testing
```

## Getting Started

### 1. Run locally first

```bash
docker-compose up --build
# Visit http://localhost:5000
```

### 2. Provision AWS infrastructure

Requires AWS CLI configured (`aws configure`) and Terraform installed.

```bash
cd terraform
terraform init
terraform apply
```

This creates a VPC and an EKS cluster (takes ~15 minutes).

### 3. Connect kubectl to the cluster

```bash
aws eks update-kubeconfig --region us-east-1 --name devops-todo-cluster
```

### 4. Install ArgoCD and deploy the app

```bash
bash scripts/install-argocd.sh
kubectl apply -f argocd/application.yaml
```

Or run everything in one go:

```bash
bash scripts/deploy-all.sh
```

### 5. Set up CI/CD

In your GitHub repo settings, add these secrets:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

Every push to `main` (under `app/`) will now build, push, and trigger a GitOps deployment automatically.

## What This Project Demonstrates

- Writing a Dockerfile and containerizing an application
- Provisioning cloud infrastructure with Terraform (VPC, EKS, IAM)
- Building a CI/CD pipeline with GitHub Actions
- Implementing GitOps with ArgoCD (declarative, Git-as-source-of-truth deployments)
- Writing Kubernetes manifests (Deployment, Service, Ingress, HPA)
- Configuring autoscaling and health checks for resiliency
- Automating operational tasks with Bash scripting

## Future Improvements

- Add Prometheus + Grafana for monitoring
- Add Helm chart instead of raw manifests
- Add Ansible playbook for bastion host configuration
- Add Slack/email notifications on pipeline failure
