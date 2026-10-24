# Contributing

This project is a teaching demo, so the main rule is: **keep it easy to read.**
A change that adds a feature but makes `chatbot.py` harder to follow is
usually not worth it. A clearer comment or a better exercise usually is.

## Setup

```bash
uv sync           # installs boto3 and pytest into .venv
uv run pytest     # offline tests, no AWS calls
```

## Guidelines

- Keep everything in `chatbot.py`, in its numbered sections.
- Explain *why* in comments, not just *what*. Assume the reader is new to Bedrock.
- If you change behaviour, update the README's "Things to try" and the tests.
- Model IDs go out of date. When updating them, check the
  [model catalog](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards.html)
  and run the chatbot against each model before opening a pull request.
