# DevOps To-Do App — End-to-End CI/CD on AWS EKS with GitOps

A simple Flask To-Do application that demonstrates a complete, production-style DevOps workflow — containerization, infrastructure as code, CI/CD automation, Redis-backed shared storage, and GitOps-based deployment to Kubernetes on AWS.

> **Built by [NikhilKonduru06](https://github.com/NikhilKonduru06)** — fork this repo and follow the guide below to deploy it yourself.

---

## Architecture

```
Developer Push
      │
      ▼
GitHub Actions (CI)
  ├── Run tests (with Redis service container)
  ├── Build Docker image
  ├── Push to Docker Hub
  └── Update image tag in k8s/deployment.yaml
      │
      ▼
Git Repo (source of truth)
      │
      ▼
ArgoCD (CD / GitOps)
  └── Auto-syncs changes into AWS EKS cluster
      │
      ▼
AWS EKS Cluster
  ├── todo-app pods (2 replicas)
  ├── Redis pod (shared task storage)
  └── AWS ALB Ingress (public URL)
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Application | Python 3.12 + Flask |
| Shared Storage | Redis |
| Containerization | Docker + Docker Compose |
| Infrastructure as Code | Terraform (VPC + EKS) |
| CI Pipeline | GitHub Actions |
| CD / GitOps | ArgoCD |
| Orchestration | Kubernetes on AWS EKS |
| Load Balancing | AWS ALB Ingress Controller |
| Scripting | Bash |

---

## Repository Structure

```
.
├── app/                        # Flask application
│   ├── app.py                  # App logic (Redis-backed tasks)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── templates/index.html
├── k8s/                        # Kubernetes manifests (watched by ArgoCD)
│   ├── namespace.yaml
│   ├── deployment.yaml         # todo-app deployment (image tag auto-updated by CI)
│   ├── service.yaml
│   ├── ingress.yaml            # AWS ALB Ingress
│   ├── hpa.yaml                # Horizontal Pod Autoscaler
│   └── redis.yaml              # Redis deployment + service
├── terraform/                  # AWS infrastructure (VPC + EKS)
│   ├── provider.tf
│   ├── variables.tf
│   ├── vpc.tf
│   ├── eks.tf
│   └── outputs.tf
├── argocd/
│   └── application.yaml        # ArgoCD app definition
├── .github/workflows/
│   └── ci-cd.yaml              # Full CI/CD pipeline
├── scripts/
│   ├── install-argocd.sh
│   └── deploy-all.sh
└── docker-compose.yml
```

---

## Prerequisites

Before starting, make sure you have the following installed:

| Tool | Purpose | Install |
|---|---|---|
| Git | Version control | [git-scm.com](https://git-scm.com) |
| Docker Desktop | Local container runtime | [docker.com](https://docker.com) |
| AWS CLI | Talk to AWS from terminal | [docs.aws.amazon.com/cli](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) |
| Terraform | Provision AWS infrastructure | [terraform.io](https://developer.hashicorp.com/terraform/install) |
| kubectl | Manage Kubernetes cluster | [kubernetes.io](https://kubernetes.io/docs/tasks/tools/) |
| eksctl | EKS helper CLI | [eksctl.io](https://eksctl.io/installation/) |
| Helm | Install Kubernetes packages | [helm.sh](https://helm.sh/docs/intro/install/) |

You also need:
- An **AWS account** with billing enabled
- A **Docker Hub account**
- A **GitHub account**

> ⚠️ **Cost Warning:** Running this project on AWS costs roughly $0.50–$1.00/hour (EKS control plane + 2x t3.medium EC2 nodes + NAT Gateway). Always run `terraform destroy` when you're done to avoid unexpected charges.

---

## Step-by-Step Deployment Guide

### Step 1 — Fork and clone this repo

1. Click **Fork** at the top right of this page
2. Clone your fork locally:

```bash
git clone https://github.com/<YOUR_GITHUB_USERNAME>/devops-mega-project.git
cd devops-mega-project
```

---

### Step 2 — Run the app locally first

Make sure Docker Desktop is running, then:

```bash
docker compose up --build
```

Open your browser at `http://localhost:5000` — you should see the To-Do app. Add and delete a task to confirm it works.

Press `Ctrl+C` to stop when done.

---

### Step 3 — Set up GitHub Actions secrets

The CI pipeline needs credentials to push images to Docker Hub.

**Generate a Docker Hub access token:**
1. Log in to [hub.docker.com](https://hub.docker.com)
2. Click your profile → **Account Settings** → **Personal access tokens**
3. Click **Generate new token** → name it `github-actions` → permissions: **Read & Write**
4. Copy the token (shown only once)

**Add secrets to your GitHub repo:**
1. Go to your forked repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add:
   - Name: `DOCKERHUB_USERNAME` → Value: your Docker Hub username
   - Name: `DOCKERHUB_TOKEN` → Value: the token you just generated

**Allow GitHub Actions to write back to your repo:**
1. Go to **Settings** → **Actions** → **General**
2. Under **Workflow permissions** → select **Read and write permissions**
3. Click **Save**

---

### Step 4 — Update the ArgoCD application manifest

Open `argocd/application.yaml` and replace the `repoURL` with your own fork:

```yaml
repoURL: https://github.com/<YOUR_GITHUB_USERNAME>/devops-mega-project.git
```

Commit and push:

```bash
git add argocd/application.yaml
git commit -m "fix: set my repo URL for ArgoCD"
git push
```

This will trigger your first CI/CD pipeline run — go check the **Actions** tab on GitHub to watch it.

---

### Step 5 — Configure AWS credentials

**Create an IAM user with access keys:**
1. Log in to the [AWS Console](https://console.aws.amazon.com)
2. Go to **IAM** → **Users** → **Create user**
3. Name it `devops-cli-user` → attach **AdministratorAccess** policy
4. After creating, go to the user → **Security credentials** → **Create access key** → choose **CLI**
5. Copy the **Access Key ID** and **Secret Access Key**

**Configure the AWS CLI:**

```bash
aws configure
# Enter your Access Key ID
# Enter your Secret Access Key
# Default region: us-east-1
# Default output format: json
```

**Verify it works:**

```bash
aws sts get-caller-identity
```

You should see your account ID and user ARN printed.

---

### Step 6 — Provision the AWS infrastructure with Terraform

```bash
cd terraform
terraform init
terraform plan    # Preview what will be created (should show ~54 resources)
terraform apply   # Type 'yes' when prompted
```

This takes **12–15 minutes**. It creates:
- A VPC with public and private subnets across 2 availability zones
- A NAT Gateway for private subnet internet access
- An EKS cluster (Kubernetes 1.31) with 2x t3.medium worker nodes
- All required IAM roles and security groups

Once complete, note the outputs — especially `cluster_name` and `configure_kubectl`.

---

### Step 7 — Connect kubectl to your cluster

```bash
aws eks update-kubeconfig --region us-east-1 --name devops-todo-cluster
```

Verify your nodes are ready:

```bash
kubectl get nodes
```

You should see 2 nodes with status `Ready`.

---

### Step 8 — Install the AWS Load Balancer Controller

This is required to provision an AWS ALB when you apply the Ingress manifest.

```bash
# Step 8a: Associate OIDC provider
eksctl utils associate-iam-oidc-provider \
  --cluster devops-todo-cluster \
  --region us-east-1 \
  --approve

# Step 8b: Download and create the IAM policy
curl -O https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json

aws iam create-policy \
  --policy-name AWSLoadBalancerControllerIAMPolicy \
  --policy-document file://iam_policy.json

# Step 8c: Create the IAM service account (replace ACCOUNT_ID with your AWS account ID)
eksctl create iamserviceaccount \
  --cluster=devops-todo-cluster \
  --region=us-east-1 \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --attach-policy-arn=arn:aws:iam::<YOUR_AWS_ACCOUNT_ID>:policy/AWSLoadBalancerControllerIAMPolicy \
  --override-existing-serviceaccounts \
  --approve

# Step 8d: Get your VPC ID
aws eks describe-cluster \
  --name devops-todo-cluster \
  --region us-east-1 \
  --query "cluster.resourcesVpcConfig.vpcId" \
  --output text

# Step 8e: Install the controller via Helm (replace VPC_ID with output from above)
helm repo add eks https://aws.github.io/eks-charts
helm repo update

helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=devops-todo-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller \
  --set region=us-east-1 \
  --set vpcId=<YOUR_VPC_ID>
```

Verify the controller is running:

```bash
kubectl get pods -n kube-system | grep aws-load-balancer
```

You should see 2 pods with `Running` status.

---

### Step 9 — Install ArgoCD

```bash
bash scripts/install-argocd.sh
```

Verify all ArgoCD pods are running:

```bash
kubectl get pods -n argocd
```

---

### Step 10 — Deploy Redis and apply ArgoCD Application

First, deploy Redis directly (it's infrastructure, not managed by the app CI pipeline):

```bash
kubectl apply -f k8s/redis.yaml
```

Then register your app with ArgoCD:

```bash
kubectl apply -f argocd/application.yaml
```

Verify ArgoCD picked it up:

```bash
kubectl get applications -n argocd
```

You should see `devops-todo-app` with status `Synced` and `Healthy`.

---

### Step 11 — Access the app

Check for the public URL:

```bash
kubectl get ingress -n devops-project
```

Wait 2–3 minutes for the `ADDRESS` field to populate (AWS is provisioning the ALB behind the scenes). Once it shows a URL like `k8s-xxxx.us-east-1.elb.amazonaws.com`, open it in your browser.

---

### Step 12 — Access the ArgoCD UI (optional)

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Open `https://localhost:8080` in your browser (click through the certificate warning).

Get the admin password:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath='{.data.password}' | base64 -d; echo
```

Login with username `admin` and the password above. You'll see a visual graph of your entire deployment.

---

## How the GitOps Flow Works

Once everything is set up, the full automated flow is:

1. You push code changes to `app/` on the `main` branch
2. GitHub Actions runs tests (with a live Redis service container)
3. On success, it builds and pushes a new Docker image to Docker Hub
4. It updates the image tag in `k8s/deployment.yaml` and commits it back to the repo
5. ArgoCD detects the change in Git and automatically syncs the new version to your EKS cluster
6. Zero manual deployment steps needed

---

## Teardown — Stop AWS Billing

When you're done, tear everything down to stop charges:

```bash
# Step 1: Remove the Ingress from Git so ArgoCD doesn't recreate the ALB
git rm k8s/ingress.yaml
git commit -m "chore: remove ingress for teardown"
git push

# Step 2: Wait for ArgoCD to prune the ALB (about 90 seconds)
sleep 90

# Step 3: Confirm the load balancer is gone
aws elbv2 describe-load-balancers \
  --region us-east-1 \
  --query "LoadBalancers[*].LoadBalancerName" \
  --output table

# Step 4: Destroy all AWS infrastructure
cd terraform
terraform destroy   # Type 'yes' when prompted — takes 10-15 minutes

# Step 5: Confirm everything is gone
aws eks list-clusters --region us-east-1
```

You can spin everything back up anytime with `terraform apply`.

---

## What This Project Demonstrates

- Containerizing a Python web app with Docker
- Multi-replica Kubernetes deployment with shared Redis state (solving a real stateless-app consistency problem)
- Provisioning production-grade AWS infrastructure (VPC, EKS, IAM) with Terraform
- End-to-end CI/CD with GitHub Actions (test → build → push → manifest update)
- GitOps deployment pattern with ArgoCD (Git as the single source of truth)
- AWS Load Balancer Controller and ALB Ingress setup
- Horizontal Pod Autoscaling
- Bash scripting for operational automation

---

## Common Issues

**`terraform apply` fails with "unsupported Kubernetes version"**
Update `cluster_version` in `terraform/variables.tf` to a currently supported version (e.g. `1.31`).

**GitHub Actions fails with "Username and password required"**
Your Docker Hub secrets aren't set correctly. Go to repo Settings → Secrets → Actions and verify `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` are both present with correct values.

**GitHub Actions fails with "Permission denied" on git push**
Go to repo Settings → Actions → General → Workflow permissions → select "Read and write permissions".

**Ingress ADDRESS stays empty**
The AWS Load Balancer Controller may not be installed or running. Check with `kubectl get pods -n kube-system | grep aws-load-balancer`.

**Tasks disappear after adding them**
This happens if Redis isn't running. Check with `kubectl get pods -n devops-project` — the `redis` pod should be `Running`.

---

## Future Improvements

- Add Prometheus + Grafana for cluster and app monitoring
- Package Kubernetes manifests as a Helm chart
- Add SSL/TLS certificate with AWS ACM
- Add Slack notifications on pipeline failure
- Add Ansible playbook for bastion host configuration

---

## Author

Built by [NikhilKonduru06](https://github.com/NikhilKonduru06) as a DevOps portfolio project.  
Feel free to fork, use, and improve it!
