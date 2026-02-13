#!/usr/bin/env bash
set -euo pipefail

# LearnFlow GKE Autopilot Deployment Script
# Usage: ./k8s/deploy-gke.sh
#
# Required env vars:
#   OPENAI_API_KEY  - OpenAI API key for AI services
#   DATABASE_URL    - Neon PostgreSQL connection string
#   AUTH_SECRET     - Better Auth secret key
#
# Optional env vars:
#   GCP_PROJECT     - GCP project ID (default: project-030bbae1-06bc-44ee-bbe)
#   GCP_REGION      - GCP region (default: us-central1)
#   CLUSTER_NAME    - GKE cluster name (default: learnflow-cluster)

GCP_PROJECT="${GCP_PROJECT:-project-030bbae1-06bc-44ee-bbe}"
GCP_REGION="${GCP_REGION:-us-central1}"
CLUSTER_NAME="${CLUSTER_NAME:-learnflow-cluster}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()   { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# -------------------------------------------------------------------
# Pre-flight checks
# -------------------------------------------------------------------
preflight() {
    log "Pre-flight checks..."

    for cmd in gcloud kubectl helm dapr; do
        command -v "$cmd" &>/dev/null || error "$cmd not found. Install it first."
    done

    [[ -z "${OPENAI_API_KEY:-}" ]] && error "OPENAI_API_KEY env var is required"
    [[ -z "${DATABASE_URL:-}" ]]   && error "DATABASE_URL env var is required"
    [[ -z "${AUTH_SECRET:-}" ]]    && error "AUTH_SECRET env var is required"

    log "All pre-flight checks passed."
}

# -------------------------------------------------------------------
# Phase 0: GKE Cluster
# -------------------------------------------------------------------
phase0_cluster() {
    log "=== Phase 0: GKE Cluster ==="

    gcloud config set project "$GCP_PROJECT"

    # Enable required APIs
    log "Enabling container.googleapis.com..."
    gcloud services enable container.googleapis.com

    # Check if cluster already exists
    if gcloud container clusters describe "$CLUSTER_NAME" --region="$GCP_REGION" &>/dev/null; then
        log "Cluster $CLUSTER_NAME already exists, fetching credentials..."
    else
        log "Creating Autopilot cluster $CLUSTER_NAME (this takes ~10 min)..."
        gcloud container clusters create-auto "$CLUSTER_NAME" --region="$GCP_REGION"
    fi

    gcloud container clusters get-credentials "$CLUSTER_NAME" --region="$GCP_REGION"
    log "Cluster ready. Context: $(kubectl config current-context)"
}

# -------------------------------------------------------------------
# Phase 1: Cluster Operators
# -------------------------------------------------------------------
phase1_operators() {
    log "=== Phase 1: Cluster Operators ==="

    # 1.1 Namespaces
    log "Creating namespaces..."
    kubectl apply -f "$SCRIPT_DIR/namespaces.yaml"
    kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -

    # 1.2 Strimzi Kafka Operator
    log "Installing Strimzi Kafka Operator..."
    kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka 2>/dev/null || \
        kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
    log "Waiting for Strimzi operator..."
    kubectl wait deployment/strimzi-cluster-operator -n kafka \
        --for=condition=Available --timeout=300s

    # 1.3 Dapr
    log "Installing Dapr..."
    dapr init --kubernetes --wait || warn "Dapr may already be installed"

    # 1.4 Kong Ingress Controller
    log "Installing Kong Ingress Controller..."
    helm repo add kong https://charts.konghq.com 2>/dev/null || true
    helm repo update
    if helm status kong -n kong &>/dev/null; then
        log "Kong already installed, upgrading..."
        helm upgrade kong kong/ingress -n kong
    else
        helm install kong kong/ingress -n kong --create-namespace
    fi

    log "Phase 1 complete: all operators installed."
}

# -------------------------------------------------------------------
# Phase 2: Secrets
# -------------------------------------------------------------------
phase2_secrets() {
    log "=== Phase 2: K8s Secrets ==="

    kubectl create secret generic openai-credentials -n learnflow \
        --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
        --dry-run=client -o yaml | kubectl apply -f -

    kubectl create secret generic postgres-credentials -n learnflow \
        --from-literal=DATABASE_URL="$DATABASE_URL" \
        --dry-run=client -o yaml | kubectl apply -f -

    kubectl create secret generic auth-secrets -n learnflow \
        --from-literal=AUTH_SECRET="$AUTH_SECRET" \
        --dry-run=client -o yaml | kubectl apply -f -

    log "Phase 2 complete: secrets created."
}

# -------------------------------------------------------------------
# Phase 3: Infrastructure (Kafka + Dapr components)
# -------------------------------------------------------------------
phase3_infrastructure() {
    log "=== Phase 3: Infrastructure ==="

    # Kafka cluster
    log "Deploying Kafka cluster..."
    kubectl apply -f "$SCRIPT_DIR/kafka/kafka-cluster.yaml"
    log "Waiting for Kafka to be ready (up to 10 min)..."
    kubectl wait kafka/learnflow-kafka -n kafka \
        --for=condition=Ready --timeout=600s

    # Kafka topics
    log "Creating Kafka topics..."
    kubectl apply -f "$SCRIPT_DIR/kafka/kafka-topics.yaml"

    # Dapr components
    log "Deploying Dapr components..."
    kubectl apply -f "$SCRIPT_DIR/dapr/components.yaml"

    log "Phase 3 complete: Kafka + Dapr ready."
}

# -------------------------------------------------------------------
# Phase 4: Deploy Services
# -------------------------------------------------------------------
phase4_services() {
    log "=== Phase 4: Deploy Services ==="

    kubectl apply -f "$SCRIPT_DIR/services/"
    log "Waiting for all deployments (up to 5 min)..."
    kubectl wait deployment --all -n learnflow \
        --for=condition=Available --timeout=300s

    log "Phase 4 complete: all services deployed."
}

# -------------------------------------------------------------------
# Phase 5: Kong Ingress
# -------------------------------------------------------------------
phase5_ingress() {
    log "=== Phase 5: Kong Ingress ==="

    kubectl apply -f "$SCRIPT_DIR/kong/ingress.yaml"

    # Wait for Kong external IP
    log "Waiting for Kong LoadBalancer IP (up to 5 min)..."
    for i in $(seq 1 60); do
        KONG_IP=$(kubectl get svc -n kong \
            -l app.kubernetes.io/component=proxy \
            -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}' 2>/dev/null || true)
        if [[ -n "$KONG_IP" && "$KONG_IP" != "null" ]]; then
            break
        fi
        sleep 5
    done

    if [[ -z "$KONG_IP" || "$KONG_IP" == "null" ]]; then
        warn "Kong IP not available yet. Run: kubectl get svc -n kong"
        warn "Then manually: kubectl set env deployment/learnflow-frontend BETTER_AUTH_URL=http://<IP> -n learnflow"
        return
    fi

    log "Kong external IP: $KONG_IP"

    # Update frontend auth URL
    kubectl set env deployment/learnflow-frontend \
        BETTER_AUTH_URL="http://$KONG_IP" -n learnflow
    kubectl rollout restart deployment/learnflow-frontend -n learnflow
    kubectl rollout status deployment/learnflow-frontend -n learnflow --timeout=120s

    log "Phase 5 complete: ingress configured, frontend updated."
}

# -------------------------------------------------------------------
# Phase 6: Verification
# -------------------------------------------------------------------
phase6_verify() {
    log "=== Phase 6: Verification ==="

    KONG_IP=$(kubectl get svc -n kong \
        -l app.kubernetes.io/component=proxy \
        -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}' 2>/dev/null || true)

    if [[ -z "$KONG_IP" || "$KONG_IP" == "null" ]]; then
        warn "Kong IP not available, skipping HTTP checks."
        kubectl get pods -n learnflow
        return
    fi

    log "Running health checks against http://$KONG_IP ..."

    SERVICES=("triage" "concepts" "exercises" "execute" "debug" "review" "progress")
    PASS=0
    FAIL=0

    for svc in "${SERVICES[@]}"; do
        STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://$KONG_IP/api/$svc/health" --max-time 10 || echo "000")
        if [[ "$STATUS" == "200" ]]; then
            log "  $svc: OK ($STATUS)"
            ((PASS++))
        else
            warn "  $svc: FAIL ($STATUS)"
            ((FAIL++))
        fi
    done

    # Frontend
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://$KONG_IP/" --max-time 10 || echo "000")
    if [[ "$STATUS" == "200" ]]; then
        log "  frontend: OK ($STATUS)"
        ((PASS++))
    else
        warn "  frontend: FAIL ($STATUS)"
        ((FAIL++))
    fi

    log ""
    log "Health check results: $PASS passed, $FAIL failed"
    log "Dapr sidecars:"
    kubectl get pods -n learnflow -o wide
    log ""
    log "Kafka topics:"
    kubectl get kafkatopic -n kafka
    log ""
    log "==========================================="
    log " LearnFlow is live at: http://$KONG_IP"
    log "==========================================="
}

# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
main() {
    log "LearnFlow GKE Autopilot Deployment"
    log "Project: $GCP_PROJECT | Region: $GCP_REGION | Cluster: $CLUSTER_NAME"
    echo ""

    preflight
    phase0_cluster
    phase1_operators
    phase2_secrets
    phase3_infrastructure
    phase4_services
    phase5_ingress
    phase6_verify

    log "Deployment complete!"
}

# Allow running individual phases: ./deploy-gke.sh phase3_infrastructure
if [[ $# -gt 0 ]]; then
    "$@"
else
    main
fi
