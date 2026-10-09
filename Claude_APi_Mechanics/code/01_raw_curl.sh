curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-5-5",
    "max_tokens": 512,
    "system": "You are a concise tutor.",
    "messages": [
      {"role": "user", "content": "What is an HTTP header?"}
    ]
  }'
