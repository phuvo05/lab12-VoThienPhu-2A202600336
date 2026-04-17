#!/bin/bash

# Test script for Lab 06 AI Agent
echo "🧪 Testing Production AI Agent"
echo "================================"

BASE_URL="http://localhost:8000"
API_KEY="test-api-key-12345"
ADMIN_KEY="admin-key-67890"

echo ""
echo "1️⃣ Testing Health Check..."
curl -s $BASE_URL/health | jq '.'

echo ""
echo "2️⃣ Testing Readiness Check..."
curl -s $BASE_URL/readiness | jq '.'

echo ""
echo "3️⃣ Testing Authentication (should fail)..."
curl -s -X POST $BASE_URL/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}' \
  -w "\nStatus: %{http_code}\n"

echo ""
echo "4️⃣ Testing Chat with API Key (should succeed)..."
curl -s -X POST $BASE_URL/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"message": "Hello, how are you?"}' | jq '.'

echo ""
echo "5️⃣ Testing Usage Endpoint..."
curl -s $BASE_URL/usage/$API_KEY \
  -H "X-API-Key: $API_KEY" | jq '.'

echo ""
echo "6️⃣ Testing Rate Limit (sending 11 requests)..."
for i in {1..11}; do
  echo -n "Request $i: "
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/chat \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"message": "Test"}')
  echo "Status $STATUS"
  if [ "$STATUS" == "429" ]; then
    echo "✅ Rate limit working!"
    break
  fi
  sleep 0.5
done

echo ""
echo "7️⃣ Testing Metrics (admin only)..."
curl -s $BASE_URL/metrics \
  -H "X-API-Key: $ADMIN_KEY" | jq '.'

echo ""
echo "✅ All tests completed!"
