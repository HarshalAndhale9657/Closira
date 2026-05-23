"""
OpenAI GPT-4o API client wrapper.

Provides a clean interface for sending messages to the OpenAI API
with support for JSON mode, error handling, and token tracking.
"""

import json
import sys
from openai import OpenAI, APIError, RateLimitError, APIConnectionError
from src.config import OPENAI_API_KEY, MODEL_NAME, MODEL_TEMPERATURE, MAX_TOKENS


# ── Initialize client ────────────────────────────────────────────────────
_client: OpenAI | None = None


def get_client() -> OpenAI:
    """Get or create the OpenAI client (lazy initialization)."""
    global _client
    if _client is None:
        if not OPENAI_API_KEY:
            print(
                "\n❌ Error: OPENAI_API_KEY is not set.\n"
                "   Please create a .env file with your API key.\n"
                "   See .env.example for the expected format.\n"
            )
            sys.exit(1)
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


# ── Token usage tracking ─────────────────────────────────────────────────
_total_tokens_used = {"prompt": 0, "completion": 0, "total": 0}


def get_token_usage() -> dict:
    """Return cumulative token usage for the session."""
    return _total_tokens_used.copy()


# ── Core API call ────────────────────────────────────────────────────────
def send_message(
    system_prompt: str,
    messages: list[dict],
    json_mode: bool = False,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """
    Send a message to the OpenAI API and return the response content.

    Args:
        system_prompt: The system prompt to set context and instructions.
        messages: List of message dicts with 'role' and 'content' keys.
        json_mode: If True, enables JSON response format for structured output.
        temperature: Override default temperature (0.2).
        max_tokens: Override default max tokens.

    Returns:
        The assistant's response content as a string.

    Raises:
        RuntimeError: If the API call fails after retries.
    """
    client = get_client()

    # Build the full message list with system prompt
    full_messages = [{"role": "system", "content": system_prompt}] + messages

    # Request parameters
    params = {
        "model": MODEL_NAME,
        "messages": full_messages,
        "temperature": temperature if temperature is not None else MODEL_TEMPERATURE,
        "max_tokens": max_tokens or MAX_TOKENS,
    }

    # Enable JSON mode for structured outputs
    if json_mode:
        params["response_format"] = {"type": "json_object"}

    # Retry logic for transient errors
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(**params)

            # Track token usage
            if response.usage:
                _total_tokens_used["prompt"] += response.usage.prompt_tokens
                _total_tokens_used["completion"] += response.usage.completion_tokens
                _total_tokens_used["total"] += response.usage.total_tokens

            return response.choices[0].message.content or ""

        except RateLimitError:
            if attempt < max_retries - 1:
                import time
                wait = 2 ** (attempt + 1)
                print(f"  ⏳ Rate limited, retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise RuntimeError("API rate limit exceeded after retries.")

        except APIConnectionError:
            if attempt < max_retries - 1:
                import time
                time.sleep(2)
            else:
                raise RuntimeError(
                    "Could not connect to OpenAI API. Check your internet connection."
                )

        except APIError as e:
            raise RuntimeError(f"OpenAI API error: {e}")


def send_json_message(
    system_prompt: str,
    messages: list[dict],
    temperature: float | None = None,
) -> dict:
    """
    Send a message and parse the JSON response.

    Convenience wrapper that enables JSON mode and parses the result.

    Returns:
        Parsed JSON response as a dictionary.

    Raises:
        RuntimeError: If the response cannot be parsed as JSON.
    """
    raw = send_message(
        system_prompt=system_prompt,
        messages=messages,
        json_mode=True,
        temperature=temperature,
    )

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Attempt to extract JSON from a wrapped response
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(raw[start:end])
            except json.JSONDecodeError:
                pass
        raise RuntimeError(
            f"Failed to parse JSON from API response:\n{raw[:500]}"
        )
