#!/usr/bin/env bash
set -euo pipefail

# LearnFlow GKE Verification Script
# Usage: ./k8s/verify-gke.sh [KONG_IP]

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
fail() { echo -e "${RED}[FAIL]${NC} $*"; }

KONG_IP="${1:-}"

if [[ -z "$KONG_IP" ]]; then
    KONG_IP=$(kubectl get svc -n kong \
        -l app.kubernetes.io/component=proxy \
        -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}' 2>/dev/null || true)
fi

if [[ -z "$KONG_IP" || "$KONG_IP" == "null" ]]; then
    fail "Cannot determine Kong external IP."
    echo "  Try: kubectl get svc -n kong"
    echo "  Then: $0 <IP>"
    exit 1
fi

echo ""
echo "=== LearnFlow GKE Verification ==="
echo "Kong IP: $KONG_IP"
echo ""

# 1. Check pods
echo "--- Pod Status (learnflow namespace) ---"
kubectl get pods -n learnflow -o wide
echo ""

# 2. Check Dapr sidecars (should show 2/2 READY for backend pods)
echo "--- Dapr Sidecar Check ---"
BACKEND_PODS=$(kubectl get pods -n learnflow -l 'app in (triage-service,concepts-service,exercise-service,code-execution-service,debug-service,code-review-service,progress-service)' -o jsonpath='{range .items[*]}{.metadata.name} {.status.containerStatuses[*].ready}{"\n"}{end}' 2>/dev/null || true)
if [[ -n "$BACKEND_PODS" ]]; then
    echo "$BACKEND_PODS" | while read -r pod ready; do
        CONTAINERS=$(kubectl get pod "$pod" -n learnflow -o jsonpath='{.spec.containers[*].name}' 2>/dev/null)
        COUNT=$(echo "$CONTAINERS" | wc -w)
        if [[ $COUNT -ge 2 ]]; then
            log "$pod: $COUNT containers (Dapr sidecar injected)"
        else
            warn "$pod: $COUNT container (no Dapr sidecar?)"
        fi
    done
fi
echo ""

# 3. Check Kafka
echo "--- Kafka Status ---"
kubectl get kafka -n kafka 2>/dev/null || warn "No Kafka resources found"
kubectl get kafkatopic -n kafka 2>/dev/null || warn "No Kafka topics found"
echo ""

# 4. Health checks via Kong
echo "--- Service Health Checks (via Kong) ---"
SERVICES=("triage" "concepts" "exercises" "execute" "debug" "review" "progress")
PASS=0
FAIL_COUNT=0

for svc in "${SERVICES[@]}"; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://$KONG_IP/api/$svc/health" --max-time 10 2>/dev/null || echo "000")
    if [[ "$STATUS" == "200" ]]; then
        log "/api/$svc/health -> $STATUS"
        ((PASS++))
    else
        fail "/api/$svc/health -> $STATUS"
        ((FAIL_COUNT++))
    fi
done

# Frontend
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://$KONG_IP/" --max-time 10 2>/dev/null || echo "000")
if [[ "$STATUS" == "200" ]]; then
    log "/ (frontend) -> $STATUS"
    ((PASS++))
else
    fail "/ (frontend) -> $STATUS"
    ((FAIL_COUNT++))
fi

echo ""
echo "=== Results: $PASS passed, $FAIL_COUNT failed ==="

if [[ $FAIL_COUNT -eq 0 ]]; then
    echo ""
    log "LearnFlow is fully operational at http://$KONG_IP"
else
    echo ""
    warn "Some services are not healthy. Debug with:"
    echo "  kubectl logs -n learnflow deployment/<service-name> -c <service-name>"
    echo "  kubectl describe pod -n learnflow -l app=<service-name>"
fi
