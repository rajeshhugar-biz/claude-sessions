import os
from dotenv import load_dotenv
import anthropic

# Load environment variables from the .env file
load_dotenv()

# Get the API key and model from the environment
api_key = os.getenv("ANTHROPIC_API_KEY")
# Falls back to Sonnet 5.5 when CLAUDE_MODEL is not set in .env
model = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")

# Ensure the API key is present
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables. Please check your .env file.")

# Initialize the Anthropic client
client = anthropic.Anthropic(
    api_key=api_key,
)

def main():
    print(f"Using model: {model}")
    print("Sending request to Anthropic API...")
    
    try:
        # Define the message you want to send
        message = client.messages.create(
            model=model,
            max_tokens=1000,
            system="You are a helpful coding assistant.",
            messages=[
                {
                    "role": "user",
                    "content": "Write a short haiku about artificial intelligence."
                }
            ]
        )
        
        # Print the response from Claude
        print("\nClaude's Response:")
        print(message.content[0].text)
        
    except anthropic.APIError as e:
        print(f"\nAPI Error: {e}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
