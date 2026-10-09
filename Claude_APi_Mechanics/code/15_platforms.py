# pip install -U "anthropic[bedrock]"   /   "anthropic[vertex]"   /   "anthropic[aws]"
from anthropic import Anthropic, AnthropicBedrock, AnthropicVertex

direct = Anthropic()                                   # Claude API
bedrock = AnthropicBedrock(aws_region="us-west-2")     # Amazon Bedrock
vertex = AnthropicVertex(project_id="my-gcp-project", region="global")  # Google Cloud

# Same Messages API shape everywhere - only the client and model ID change
for client, model in [
    (direct, "claude-haiku-4-5-20251001"),
    (bedrock, "global.anthropic.claude-haiku-4-5-20251001-v1:0"),
    (vertex, "claude-haiku-4-5@20251001"),
]:
    r = client.messages.create(model=model, max_tokens=50,
                               messages=[{"role": "user", "content": "Say hi"}])
    print(type(client).__name__, "->", r.content[0].text)
