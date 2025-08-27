import json
from typing import Any, Dict, List, Optional

import requests
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


class LLMService:
    def __init__(
        self,
        llm: Optional[ChatOpenAI],
        use_llm_studio: bool,
        base_url: str,
        model: str,
    ) -> None:
        self.llm = llm
        self.use_llm_studio = use_llm_studio
        self.base_url = base_url.rstrip("/")
        self.model = model

    def convert_messages(
        self, messages: List[SystemMessage | HumanMessage | AIMessage]
    ) -> List[Dict[str, str]]:
        converted: List[Dict[str, str]] = []
        for m in messages:
            role = "user"
            if isinstance(m, SystemMessage):
                role = "system"
            elif isinstance(m, HumanMessage):
                role = "user"
            elif isinstance(m, AIMessage):
                role = "assistant"
            content = m.content if isinstance(m.content, str) else str(m.content)
            converted.append({"role": role, "content": content})
        return converted

    def stream_completion(
        self,
        messages: List[SystemMessage | HumanMessage | AIMessage],
        temperature: float,
    ):
        """Yield delta strings from either OpenAI client or LLM Studio server."""
        if not self.use_llm_studio:
            assert self.llm is not None
            for chunk in self.llm.stream(messages):
                delta = getattr(chunk, "content", None)
                if isinstance(delta, list):
                    delta = "".join(str(part) for part in delta)
                if not isinstance(delta, str):
                    delta = str(delta) if delta is not None else ""
                yield delta
            return

        url = f"{self.base_url}/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": self.convert_messages(messages),
            "temperature": temperature,
            "max_tokens": -1,
            "stream": True,
        }
        with requests.post(url, json=payload, stream=True) as r:
            r.raise_for_status()
            for raw_line in r.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue
                line = raw_line.strip()
                if not line.startswith("data:"):
                    continue
                data_str = line[5:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    obj = json.loads(data_str)
                    choices = obj.get("choices", [])
                    if choices:
                        delta_obj = choices[0].get("delta", {}) or choices[0].get(
                            "message", {}
                        )
                        piece = delta_obj.get("content", "")
                        if piece:
                            yield piece
                except Exception:
                    continue

    def invoke_completion(
        self,
        messages: List[SystemMessage | HumanMessage | AIMessage],
        temperature: float,
    ) -> str:
        if not self.use_llm_studio:
            llm = self.llm
            assert llm is not None
            resp = llm.invoke(messages)
            rc_any: Any = resp.content if hasattr(resp, "content") else str(resp)
            if isinstance(rc_any, str):
                return rc_any
            if isinstance(rc_any, list):
                return str(rc_any[0]) if rc_any else ""

            return str(rc_any)

        url = f"{self.base_url}/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": self.convert_messages(messages),
            "temperature": temperature,
            "max_tokens": -1,
            "stream": False,
        }
        http_response: requests.Response = requests.post(url, json=payload)
        http_response.raise_for_status()
        parsed: Dict[str, Any] = http_response.json()
        choices: List[Any] = parsed.get("choices", [])
        if choices:
            msg = choices[0].get("message", {})
            content = msg.get("content", "")
            return content if isinstance(content, str) else str(content)
        return ""
