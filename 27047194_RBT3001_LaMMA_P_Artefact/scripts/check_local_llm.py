import argparse
import json
import os
import urllib.error
import urllib.request

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-test a local OpenAI-compatible LLM endpoint.")
    parser.add_argument("--base-url", default=os.getenv("LOCAL_LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL") or "http://localhost:11434/v1")
    parser.add_argument("--api-key", default=os.getenv("LOCAL_LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or "local-no-key-required")
    parser.add_argument("--model", default=os.getenv("LOCAL_LLM_MODEL") or "llama3.1:8b")
    args = parser.parse_args()

    if OpenAI is not None:
        client = OpenAI(base_url=args.base_url, api_key=args.api_key)
        response = client.chat.completions.create(
            model=args.model,
            messages=[
                {"role": "system", "content": "Reply with concise valid JSON only."},
                {"role": "user", "content": "Return {\"status\":\"ok\",\"use\":\"local robotics planning\"}."},
            ],
            temperature=0,
            max_tokens=80,
        )
        print(response.choices[0].message.content)
        return

    payload = {
        "model": args.model,
        "messages": [
            {"role": "system", "content": "Reply with concise valid JSON only."},
            {"role": "user", "content": "Return {\"status\":\"ok\",\"use\":\"local robotics planning\"}."},
        ],
        "temperature": 0,
        "max_tokens": 80,
    }
    request = urllib.request.Request(
        f"{args.base_url.rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {args.api_key}",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Local LLM HTTP error {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Local LLM connection failed: {exc.reason}") from exc

    content = body["choices"][0]["message"]["content"]
    print(content)


if __name__ == "__main__":
    main()
