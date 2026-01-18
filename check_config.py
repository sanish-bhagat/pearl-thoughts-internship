"""Quick script to check what model is being loaded."""

from config.settings import settings
import os

print("=" * 60)
print("Current Configuration Check")
print("=" * 60)
print(f"\nModel from settings: {settings.LLM_MODEL}")
print(f"API Key set: {'Yes' if settings.OPENROUTER_API_KEY else 'No'}")
print(f"API Key length: {len(settings.OPENROUTER_API_KEY) if settings.OPENROUTER_API_KEY else 0}")

# Check environment directly
print(f"\nDirect env check:")
print(f"  LLM_MODEL env var: {os.getenv('LLM_MODEL', 'NOT SET')}")
print(f"  OPENROUTER_API_KEY env var: {'SET' if os.getenv('OPENROUTER_API_KEY') else 'NOT SET'}")

print("\n" + "=" * 60)
print("If you see 'meta-llama/llama-3.1-8b-instruct:free' above,")
print("update your .env file to use: LLM_MODEL=google/gemini-flash-1.5")
print("=" * 60)
