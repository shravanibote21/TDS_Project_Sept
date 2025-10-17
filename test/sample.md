# AI Pipe

AI Pipe lets you build web apps that can access LLM APIs (e.g. OpenRouter, OpenAI, Gemini etc.) without a back-end.

An instance is hosted at <https://aipipe.org/>. You can host your own on CloudFlare. Licensed under [MIT](LICENSE).

## User Guide

Visit these pages:

- **[aipipe.org](https://aipipe.org/)** to understand how it works.
- **[aipipe.org/login](https://aipipe.org/login)** with a Google Account to get your AI Pipe Token and track your usage.
- **[aipipe.org/playground](https://aipipe.org/playground)** to explore models and chat with them.

## AI Pipe Token

You can use the AI Pipe Token from **[aipipe.org/login](https://aipipe.org/login)** in any OpenAI API compatible application by setting:

- `OPENAI_API_KEY` as your AI Pipe Token
- `OPENAI_BASE_URL` as `https://aipipe.org/openai/v1`

For example:

```bash
export OPENAI_API_KEY=$AIPIPE_TOKEN
export OPENAI_BASE_URL=https://aipipe.org/openai/v1
```

Now you can run:

```bash
uvx openai api chat.completions.create -m gpt-4.1-nano -g user "Hello"
```

... or:

```bash
uvx llm 'Hello' -m gpt-4o-mini --key $AIPIPE_TOKEN
```

This will print something like `Hello! How can I assist you today?`

## Developer Guide

Paste this code into `index.html`, open it in a browser, and check your [DevTools Console](https://developer.chrome.com/docs/devtools/console)

```html
<script type="module">
  import { getProfile } from "https://aipipe.org/aipipe.js";

  const { token, email } = getProfile();
  if (!token) window.location = `https://aipipe.org/login?redirect=${window.location.href}`;

  const response = await fetch("https://aipipe.org/openrouter/v1/chat/completions", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "openai/gpt-4o-mini",
      messages: [{ role: "user", content: "What is 2 + 2?" }],
    }),
  }).then((r) => r.json());
  console.log(response);
</script>
```
