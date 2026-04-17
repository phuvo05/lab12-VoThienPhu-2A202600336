#!/bin/bash

# Deployment Verification Script
# Tests all endpoints of the deployed AI agent

BASE_URL="https://conversational-ai-agent-z3q1.onrender.com"
API_KEY="YOUR_API_KEY_HERE"  # Replace with your actual API key

echo "🧪 Verifying Deployment: $BASE_URL"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=$3
    local method=${4:-GET}
    local headers=$5
    local data=$6
    
    echo -n "Testing $name... "
    
    if [ "$method" = "POST" ]; then
        if [ -n "$data" ]; then
            response=$(curl -s -w "\n%{http_code}" -X POST "$url" $headers -d "$data")
        else
            response=$(curl -s -w "\n%{http_code}" -X POST "$url" $headers)
        fi
    else
        response=$(curl -s -w "\n%{http_code}" "$url" $headers)
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} (Status: $status_code)"
        ((PASSED++))
        if [ -n "$body" ]; then
            echo "   Response: $(echo $body | head -c 100)..."
        fi
    else
        echo -e "${RED}❌ FAIL${NC} (Expected: $expected_status, Got: $status_code)"
        ((FAILED++))
        if [ -n "$body" ]; then
            echo "   Response: $body"
        fi
    fi
    echo ""
}

# Test 1: Health Check
test_endpoint "Health Check" "$BASE_URL/health" "200"

# Test 2: Readiness Check
test_endpoint "Readiness Check" "$BASE_URL/readiness" "200"

# Test 3: Root Endpoint (Web UI)
test_endpoint "Web UI" "$BASE_URL/" "200"

# Test 4: Authentication - No API Key (should fail)
test_endpoint "Auth - No Key" "$BASE_URL/chat" "401" "POST" \
    "-H 'Content-Type: application/json'" \
    '{"message":"Hello"}'

# Test 5: Authentication - With API Key (should succeed)
test_endpoint "Auth - With Key" "$BASE_URL/chat" "200" "POST" \
    "-H 'Content-Type: application/json' -H 'X-API-Key: $API_KEY'" \
    '{"message":"Hello"}'

# Test 6: Rate Limiting (send multiple requests)
echo "Testing Rate Limiting (sending 11 requests)..."
rate_limit_hit=false
for i in {1..11}; do
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/chat" \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY" \
        -d '{"message":"test"}')
    status_code=$(echo "$response" | tail -n1)
    
    if [ "$status_code" = "429" ]; then
        echo -e "${GREEN}✅ PASS${NC} - Rate limit triggered at request $i"
        rate_limit_hit=true
        ((PASSED++))
        break
    fi
    sleep 0.5
done

if [ "$rate_limit_hit" = false ]; then
    echo -e "${RED}❌ FAIL${NC} - Rate limit not triggered after 11 requests"
    ((FAILED++))
fi
echo ""

# Test 7: Usage Endpoint
test_endpoint "Usage Statistics" "$BASE_URL/usage/$API_KEY" "200" "GET" \
    "-H 'X-API-Key: $API_KEY'"

# Summary
echo "=================================================="
echo "Test Summary:"
echo -e "  ${GREEN}Passed: $PASSED${NC}"
echo -e "  ${RED}Failed: $FAILED${NC}"
echo "=================================================="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed! Deployment is working correctly.${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please check the deployment.${NC}"
    exit 1
fi
