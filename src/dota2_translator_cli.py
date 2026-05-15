# -*- coding: utf-8 -*-
"""
Command-line Dota 2 translator with global hotkeys and Ollama backend.
"""

import argparse
import ctypes
import hashlib
import importlib.util
import json
import os
import re
import threading
import time
from typing import Dict, List

import requests


def load_glossary_module():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(current_dir, name)
        for name in os.listdir(current_dir)
        if name.endswith(".py") and name != os.path.basename(__file__)
    ]
    if not candidates:
        raise RuntimeError(f"Failed to find glossary module in: {current_dir}")
    glossary_path = candidates[0]
    spec = importlib.util.spec_from_file_location("dota2_glossary", glossary_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load glossary module: {glossary_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_glossary_module = load_glossary_module()
ZH_TO_EN = _glossary_module.ZH_TO_EN
EN_TO_ZH = _glossary_module.EN_TO_ZH


class Config:
    DEFAULT_CONFIG = {
        "backend": {
            "provider": "ollama",
        },
        "hotkeys": {
            "trigger": "f6",
            "toggle": "ctrl+alt+t",
        },
        "translation": {
            "cooldown": 0.2,
            "source_lang": "zh-CN",
            "target_lang": "en",
            "mode": 1,
        },
        "window_filter": {
            "enabled": False,
            "title_keywords": ["dota 2"],
        },
        "ollama": {
            "host": "127.0.0.1",
            "port": 11434,
            "endpoint": "/api/generate",
            "model": "qwen2.5:7b",
            "timeout": 30,
            "think": False,
            "options": {
                "temperature": 0.1,
            },
        },
        "llamacpp": {
            "host": "127.0.0.1",
            "port": 8080,
            "endpoint": "/completion",
            "api_format": "completion",
            "model": "",
            "timeout": 30,
            "think": False,
            "headers": {},
            "options": {
                "temperature": 0.8,
                "n_predict": 128,
            },
        },
        "prompt": {
            "file": "prompts/zh_to_en_prompt.txt",
            "user_text_placeholder": "{{text}}",
        },
    }

    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        self.base_dir = os.path.dirname(self.path)
        self.data = json.loads(json.dumps(self.DEFAULT_CONFIG))
        self.load()

    def _deep_merge(self, target: dict, source: dict) -> None:
        for key, value in source.items():
            if isinstance(value, dict) and isinstance(target.get(key), dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value

    def load(self) -> None:
        if not os.path.exists(self.path):
            self.save()
            return

        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                file_config = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Failed to load config file: {self.path}") from exc

        if not isinstance(file_config, dict):
            raise RuntimeError(f"Config file must contain a JSON object: {self.path}")

        self._deep_merge(self.data, file_config)

    def save(self) -> None:
        os.makedirs(self.base_dir, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(self.data, handle, indent=2, ensure_ascii=False)

    def get(self, *keys, default=None):
        value = self.data
        for key in keys:
            if not isinstance(value, dict) or key not in value:
                return default
            value = value[key]
        return value

    def resolve_path(self, path_value: str) -> str:
        if os.path.isabs(path_value):
            return path_value
        return os.path.abspath(os.path.join(self.base_dir, path_value))


class PromptTemplate:
    def __init__(self, file_path: str, placeholder: str):
        self.file_path = file_path
        self.placeholder = placeholder
        self.template = self._load()

    def _load(self) -> str:
        try:
            with open(self.file_path, "r", encoding="utf-8") as handle:
                return handle.read().strip()
        except OSError as exc:
            raise RuntimeError(f"Failed to load prompt file: {self.file_path}") from exc

    def render(self, text: str) -> str:
        if self.placeholder in self.template:
            return self.template.replace(self.placeholder, text)
        return f"{self.template}\n\n{text}"


class TranslationEngine:
    PROTECTED_TAG = "dota2word"

    def __init__(
        self,
        backend_url: str,
        model: str,
        timeout: float,
        think: bool,
        request_options: Dict[str, object],
        prompt_template: PromptTemplate,
        mode: int = 1,
        provider: str = "ollama",
        headers: Dict[str, str] | None = None,
        api_format: str = "completion",
        verify_ssl: bool | str = True,
    ):
        self.cache: Dict[str, str] = {}
        self.session = requests.Session()
        self.mode = mode
        self.backend_url = backend_url
        self.model = model
        self.timeout = timeout
        self.think = think
        self.request_options = request_options
        self.prompt_template = prompt_template
        self.provider = provider.lower()
        self.headers = headers or {}
        self.api_format = api_format.lower()
        self.verify_ssl = verify_ssl
        self.terms = ZH_TO_EN if mode == 1 else EN_TO_ZH
        self._sorted_terms = sorted(self.terms.keys(), key=len, reverse=True)
        self._tag_pattern = re.compile(
            rf"<{self.PROTECTED_TAG}>.*?</{self.PROTECTED_TAG}>",
            flags=re.IGNORECASE | re.DOTALL,
        )
        self._english_phrase_pattern = re.compile(r"[A-Za-z][A-Za-z0-9'_-]*(?:\s+[A-Za-z0-9'_-]+)*")

    def _split_tagged_segments(self, text: str) -> List[str]:
        return re.split(
            rf"(<{self.PROTECTED_TAG}>.*?</{self.PROTECTED_TAG}>)",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )

    def _is_tagged_segment(self, segment: str) -> bool:
        return bool(segment) and self._tag_pattern.fullmatch(segment) is not None

    def _wrap_protected_text(self, text: str) -> str:
        return f"<{self.PROTECTED_TAG}>{text}</{self.PROTECTED_TAG}>"

    def protect_existing_english(self, text: str) -> str:
        protected_segments: List[str] = []

        for segment in self._split_tagged_segments(text):
            if self._is_tagged_segment(segment):
                protected_segments.append(segment)
                continue

            protected_segments.append(
                self._english_phrase_pattern.sub(
                    lambda match: self._wrap_protected_text(match.group(0)),
                    segment,
                )
            )

        return "".join(protected_segments)

    def replace_terms(self, text: str) -> str:
        replaced = text
        for source_term in self._sorted_terms:
            updated_segments: List[str] = []
            for segment in self._split_tagged_segments(replaced):
                if self._is_tagged_segment(segment):
                    updated_segments.append(segment)
                    continue

                mapped_term = self.terms[source_term]
                updated_segments.append(
                    segment.replace(source_term, self._wrap_protected_text(mapped_term))
                )
            replaced = "".join(updated_segments)

        return re.sub(r"\s+", " ", replaced).strip()

    def restore_protected_terms(self, text: str) -> str:
        restored = re.sub(
            rf"</?{self.PROTECTED_TAG}>",
            "",
            text,
            flags=re.IGNORECASE,
        )
        return re.sub(r"\s+", " ", restored).strip()

    def restore_dota_terms(self, text: str) -> str:
        text = re.sub(r"\beye\b", "ward", text, flags=re.IGNORECASE)
        text = re.sub(r"\beyes\b", "ward", text, flags=re.IGNORECASE)
        text = re.sub(r"\bfog\b", "smoke", text, flags=re.IGNORECASE)
        return text

    def _extract_response_text(self, data: Dict[str, object], provider_name: str) -> str:
        if isinstance(data.get("response"), str):
            return data["response"].strip()

        if isinstance(data.get("content"), str):
            return data["content"].strip()

        if isinstance(data.get("completion"), str):
            return data["completion"].strip()

        message = data.get("message")
        if isinstance(message, dict) and isinstance(message.get("content"), str):
            return message["content"].strip()

        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                if isinstance(first.get("text"), str):
                    return first["text"].strip()

                choice_message = first.get("message")
                if isinstance(choice_message, dict) and isinstance(choice_message.get("content"), str):
                    return choice_message["content"].strip()

        raise ValueError(f"Unsupported {provider_name} response format.")

    def _call_ollama(self, text: str) -> str:
        payload = {
            "model": self.model,
            "prompt": self.prompt_template.render(text),
            "stream": False,
            "think": self.think,
        }
        if self.request_options:
            payload["options"] = self.request_options

        response = self.session.post(
            self.backend_url,
            json=payload,
            timeout=self.timeout,
            verify=self.verify_ssl,
        )
        response.raise_for_status()
        return self._extract_response_text(response.json(), "Ollama")

    def _call_llamacpp(self, text: str) -> str:
        rendered_prompt = self.prompt_template.render(text)
        if self.api_format == "chat_completions":
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": rendered_prompt,
                    }
                ],
                "stream": False,
                "think": self.think,
            }
        else:
            payload = {
                "prompt": rendered_prompt,
                "stream": False,
                "think": self.think,
            }

        if self.model:
            payload["model"] = self.model

        if not self.think and "qwen3.6" in self.model.lower():
            payload["chat_template_kwargs"] = {"enable_thinking": False}

        payload.update(self.request_options)

        response = self.session.post(
            self.backend_url,
            json=payload,
            headers=self.headers,
            timeout=self.timeout,
            verify=self.verify_ssl,
        )
        response.raise_for_status()
        return self._extract_response_text(response.json(), "llama.cpp")

    def _call_backend(self, text: str) -> str:
        if self.provider == "llamacpp":
            return self._call_llamacpp(text)
        return self._call_ollama(text)

    def translate(self, text: str) -> str:
        if not text.strip():
            return text

        if self.mode == 1 and re.search(r"[\u4e00-\u9fff]", text) is None:
            return text

        if self.mode != 1 and re.search(r"[a-zA-Z]", text) is None:
            return text

        cache_key = hashlib.md5(f"{self.mode}:{text}".encode("utf-8")).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]

        protected_text = self.protect_existing_english(text)
        text_with_protected_terms = self.replace_terms(protected_text)
        translated = self._call_backend(text_with_protected_terms)
        translated = self.restore_protected_terms(translated)

        if self.mode == 1:
            translated = self.restore_dota_terms(translated)

        self.cache[cache_key] = translated
        return translated


class HotkeyTranslatorCLI:
    def __init__(self, config_path: str):
        self.config = Config(config_path)
        self.keyboard = None
        self.pyautogui = None
        self.pyperclip = None
        self.enabled = True
        self.is_translating = False
        self.last_time = 0.0

        prompt_file = self.config.resolve_path(self.config.get("prompt", "file"))
        prompt_placeholder = self.config.get("prompt", "user_text_placeholder", default="{{text}}")
        prompt_template = PromptTemplate(prompt_file, prompt_placeholder)

        backend_provider = str(self.config.get("backend", "provider", default="ollama")).lower()
        backend_section = "llamacpp" if backend_provider == "llamacpp" else "ollama"

        host = self.config.get(backend_section, "host")
        port = self.config.get(backend_section, "port")
        endpoint = self.config.get(backend_section, "endpoint")
        backend_url = self._build_ollama_url(host, port, endpoint)

        self.engine = TranslationEngine(
            backend_url=backend_url,
            model=self.config.get(backend_section, "model", default=""),
            timeout=float(self.config.get(backend_section, "timeout", default=30)),
            think=bool(self.config.get(backend_section, "think", default=False)),
            request_options=self.config.get(backend_section, "options", default={}) or {},
            prompt_template=prompt_template,
            mode=int(self.config.get("translation", "mode", default=1)),
            provider=backend_provider,
            headers=self.config.get(backend_section, "headers", default={}) or {},
            api_format=self.config.get(backend_section, "api_format", default="completion"),
            verify_ssl=self._resolve_verify_ssl(backend_section),
        )

    def _build_ollama_url(self, host: str, port: int, endpoint: str) -> str:
        endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        host = str(host).rstrip("/")
        if host.startswith(("http://", "https://")):
            return f"{host}:{port}{endpoint}"
        return f"http://{host}:{port}{endpoint}"

    def _resolve_verify_ssl(self, backend_section: str) -> bool | str:
        value = self.config.get(backend_section, "verify_ssl", default=True)
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"false", "0", "no", "off"}:
                return False
            if normalized in {"true", "1", "yes", "on"}:
                return True
            return self.config.resolve_path(value)
        return bool(value)

    def _load_runtime_dependencies(self) -> None:
        try:
            import keyboard as keyboard_module
            import pyautogui as pyautogui_module
            import pyperclip as pyperclip_module
        except ModuleNotFoundError as exc:
            missing = exc.name or "required dependency"
            raise RuntimeError(
                f"Missing dependency: {missing}. Activate the conda env and install requirements first."
            ) from exc

        self.keyboard = keyboard_module
        self.pyautogui = pyautogui_module
        self.pyperclip = pyperclip_module

    def log(self, message: str) -> None:
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}", flush=True)

    def get_foreground_window_title(self) -> str:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return ""

        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return ""

        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        return buffer.value

    def should_translate_in_current_window(self) -> bool:
        if not self.config.get("window_filter", "enabled", default=False):
            return True

        title = self.get_foreground_window_title().lower()
        keywords: List[str] = self.config.get("window_filter", "title_keywords", default=[]) or []
        return any(keyword.lower() in title for keyword in keywords)

    def toggle_translation(self) -> None:
        self.enabled = not self.enabled
        state = "enabled" if self.enabled else "disabled"
        self.log(f"Translation {state}.")

    def on_trigger(self) -> None:
        if not self.enabled or self.is_translating:
            return

        if not self.should_translate_in_current_window():
            return

        current_time = time.time()
        cooldown = float(self.config.get("translation", "cooldown", default=0.2))
        if current_time - self.last_time <= cooldown:
            return

        self.last_time = current_time
        threading.Thread(target=self.do_translate, daemon=True).start()

    def do_translate(self) -> None:
        try:
            self.is_translating = True
            self.pyautogui.hotkey("ctrl", "a")
            time.sleep(0.03)
            self.pyautogui.hotkey("ctrl", "c")
            time.sleep(0.05)

            text = self.pyperclip.paste()
            if not text or re.search(r"[\u4e00-\u9fff]", text) is None:
                return

            self.log(f"Captured: {text}")
            translated = self.engine.translate(text)

            if translated and translated != text:
                self.pyperclip.copy(translated)
                time.sleep(0.02)
                self.pyautogui.hotkey("ctrl", "v")
                # time.sleep(0.02)
                # self.pyautogui.press("enter")
                self.log(f"Sent: {translated}")
        except Exception as exc:
            self.log(f"Error: {exc}")
        finally:
            self.is_translating = False

    def run(self) -> None:
        self._load_runtime_dependencies()

        trigger_key = self.config.get("hotkeys", "trigger")
        toggle_hotkey = self.config.get("hotkeys", "toggle")

        backend_provider = str(self.config.get("backend", "provider", default="ollama")).lower()
        backend_section = "llamacpp" if backend_provider == "llamacpp" else "ollama"

        self.log("CLI translator started.")
        self.log(f"Config file: {self.config.path}")
        self.log(f"Trigger key: {trigger_key}")
        self.log(f"Toggle hotkey: {toggle_hotkey}")
        self.log(f"Backend provider: {backend_provider}")
        self.log(f"Backend model: {self.config.get(backend_section, 'model', default='') or '(not required)'}")
        self.log(
            f"Backend endpoint: {self._build_ollama_url(self.config.get(backend_section, 'host'), self.config.get(backend_section, 'port'), self.config.get(backend_section, 'endpoint'))}"
        )
        self.log(f"Window filter enabled: {self.config.get('window_filter', 'enabled', default=False)}")
        self.log("Press Ctrl+C to exit.")

        self.keyboard.add_hotkey(trigger_key, self.on_trigger)
        self.keyboard.add_hotkey(toggle_hotkey, self.toggle_translation)

        try:
            self.keyboard.wait()
        except KeyboardInterrupt:
            self.log("Stopping translator.")
        finally:
            self.keyboard.unhook_all()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dota 2 team-chat translator with external config and prompt files."
    )
    parser.add_argument("--config", default="config.json", help="Path to the runtime JSON config.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    HotkeyTranslatorCLI(args.config).run()
