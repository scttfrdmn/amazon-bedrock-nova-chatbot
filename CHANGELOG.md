# Changelog

## 0.1.0 (2026-10-23)

First versioned release: a rewrite of the original demo.

- Focus on Amazon Nova: Nova 2 Lite (default), Nova Micro and Nova Pro. The
  retired Claude 3.x models and the separate Claude code path are removed; other
  Bedrock models can still be used by passing their ID.
- Use the Converse API, streamed with `converse_stream`, and show token usage
  after each reply.
- Add `--think` to turn on Nova 2 Lite's extended thinking.
- Add `--model`, `--region`, `--system` and `--list` options, and the `/model`,
  `/history`, `/clear` and `/quit` commands.
- Explain common AWS errors, and keep the conversation valid when a request fails.
- Support Bedrock API keys (`AWS_BEARER_TOKEN_BEDROCK`).
- Rewrite the code as a commented walkthrough; add a README with learning
  goals, things to try and exercises.
- Add offline tests, `pyproject.toml` for uv, and a LICENSE file. Require Python 3.12+.
