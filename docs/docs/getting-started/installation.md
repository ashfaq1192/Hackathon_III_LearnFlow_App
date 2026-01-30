# Installation

## System Requirements

- **CPU**: 4 cores minimum (8 recommended)
- **Memory**: 8GB minimum (16GB recommended)
- **Storage**: 20GB available disk space
- **OS**: Linux, macOS, or Windows with WSL2

## Required Tools

### Kubernetes

Install one of the following:

**Minikube (Recommended for development)**
```bash
# macOS
brew install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Start cluster
minikube start --cpus=4 --memory=8192
```

### kubectl

```bash
# macOS
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl
```

### Helm 3

```bash
# macOS
brew install helm

# Linux
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Docker

Required for building container images:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Node.js 18+

Required for frontend development:
```bash
# Using nvm (recommended)
nvm install 18
nvm use 18
```

### Python 3.9+

Required for backend services:
```bash
# Verify installation
python3 --version
```

## Optional Tools

### Dapr CLI

```bash
# macOS/Linux
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | /bin/bash
```

### Claude Code

For AI-assisted deployment:
```bash
npm install -g @anthropic-ai/claude-code
```

## Environment Variables

Create a `.env` file with:

```bash
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:pass@host/db

# OpenAI (for AI services)
OPENAI_API_KEY=sk-...

# Auth (Better Auth)
AUTH_SECRET=<generate-with-openssl-rand-base64-32>

# OAuth (optional)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
```

## Verify Installation

```bash
# Check all tools installed
kubectl version --client
helm version
docker --version
node --version
python3 --version
dapr --version
```
