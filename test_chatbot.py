"""Tests for chatbot.py. These never call AWS: a fake client stands in for Bedrock.

Run with:  uv run pytest
"""

import pytest
from botocore.exceptions import ClientError

from chatbot import Chat, explain, resolve_model


class FakeClient:
    """Pretends to be bedrock-runtime. Replies with a canned list of stream events."""

    def __init__(self, events=None, error=None):
        self.events = events or []
        self.error = error
        self.requests = []

    def converse_stream(self, **request):
        # Copy the list, because Chat keeps appending to the original.
        self.requests.append({**request, "messages": list(request["messages"])})
        if self.error:
            raise self.error
        return {"stream": self.events}


def reply_events(*chunks):
    events = [{"contentBlockDelta": {"delta": {"text": c}}} for c in chunks]
    events.append({"metadata": {"usage": {"inputTokens": 10, "outputTokens": 3}}})
    return events


def test_reply_is_streamed_and_assembled():
    chat = Chat(FakeClient(reply_events("Hel", "lo")), "some-model")
    seen = []
    assert chat.ask("Hi", on_text=seen.append) == "Hello"
    assert seen == ["Hel", "lo"]
    assert chat.usage == {"inputTokens": 10, "outputTokens": 3}


def test_whole_history_is_sent_every_turn():
    client = FakeClient(reply_events("ok"))
    chat = Chat(client, "some-model")
    chat.ask("first")
    chat.ask("second")

    second_request = client.requests[1]["messages"]
    assert [m["role"] for m in second_request] == ["user", "assistant", "user"]
    assert second_request[0]["content"] == [{"text": "first"}]


def test_reasoning_is_not_shown_or_saved():
    events = [{"contentBlockDelta": {"delta": {"reasoningContent": {"text": "hmm"}}}}]
    events += reply_events("Answer")
    chat = Chat(FakeClient(events), "some-model")
    assert chat.ask("Q") == "Answer"
    assert chat.messages[-1] == {"role": "assistant", "content": [{"text": "Answer"}]}


def test_failed_request_leaves_history_unchanged():
    error = ClientError({"Error": {"Code": "ThrottlingException", "Message": "slow down"}},
                        "ConverseStream")
    chat = Chat(FakeClient(error=error), "some-model")
    with pytest.raises(ClientError):
        chat.ask("Hi")
    assert chat.messages == []


def test_errors_are_explained():
    error = ClientError({"Error": {"Code": "AccessDeniedException", "Message": "no"}},
                        "ConverseStream")
    assert "IAM policy" in explain(error)


def test_think_adds_nova_reasoning_config():
    client = FakeClient(reply_events("ok"))
    Chat(client, "some-model", think="low").ask("Q")
    assert client.requests[0]["additionalModelRequestFields"] == {
        "reasoningConfig": {"type": "enabled", "maxReasoningEffort": "low"}
    }


def test_short_names_and_full_ids():
    assert resolve_model("micro") == "us.amazon.nova-micro-v1:0"
    # Any other Bedrock model ID passes straight through.
    assert resolve_model("global.anthropic.claude-haiku-5-5") == "global.anthropic.claude-haiku-5-5"
