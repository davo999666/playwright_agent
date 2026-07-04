# utils/debug_writer.py
import asyncio
import inspect
import json
import os
import traceback
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Optional


class DebugWriter:
    def __init__(self, log_dir: str = "debug_logs", filename: str = "debug.txt"):
        self.log_dir = log_dir
        self.filepath = os.path.join(log_dir, filename)
        os.makedirs(log_dir, exist_ok=True)
         # Clear old debug file on every app start
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write("")

    def _get_timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _format_message(self, message: Any) -> Any:
        if hasattr(message, "__dict__"):
            return {
                "type": type(message).__name__,
                "content": getattr(message, "content", str(message)),
                "tool_calls": getattr(message, "tool_calls", None),
                "additional_kwargs": getattr(message, "additional_kwargs", {}),
            }
        return str(message)

    def _format_state(self, state: Dict[str, Any]) -> str:
        formatted = {}

        for key, value in state.items():
            if key == "messages" and isinstance(value, list):
                formatted[key] = [self._format_message(msg) for msg in value]
            else:
                formatted[key] = value

        return json.dumps(formatted, indent=2, default=str, ensure_ascii=False)

    def _extract_llm_response(self, output: Dict[str, Any]) -> Optional[str]:
        messages = output.get("messages", [])
        if not messages:
            return None

        last_msg = messages[-1]
        return getattr(last_msg, "content", str(last_msg))

    def _extract_tool_calls(self, output: Dict[str, Any]) -> Optional[list]:
        messages = output.get("messages", [])
        if not messages:
            return None

        last_msg = messages[-1]
        return getattr(last_msg, "tool_calls", None)

    def write_log(
        self,
        node_name: str,
        input_state: Dict[str, Any],
        output_state: Optional[Dict[str, Any]] = None,
        llm_response: Optional[str] = None,
        tool_calls: Optional[list] = None,
        error: Optional[Exception] = None,
    ) -> None:
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"NODE: {node_name}\n")
            f.write(f"TIME: {self._get_timestamp()}\n")
            f.write("=" * 80 + "\n\n")

            f.write("--- INPUT STATE ---\n")
            f.write(self._format_state(input_state) + "\n\n")

            if llm_response:
                f.write("--- LLM RESPONSE ---\n")
                f.write(str(llm_response) + "\n\n")

            if tool_calls:
                f.write("--- TOOL CALLS ---\n")
                f.write(json.dumps(tool_calls, indent=2, default=str, ensure_ascii=False))
                f.write("\n\n")

            if output_state is not None:
                f.write("--- OUTPUT STATE ---\n")
                f.write(self._format_state(output_state) + "\n\n")

            if error:
                f.write("--- ERROR ---\n")
                f.write(f"Type: {type(error).__name__}\n")
                f.write(f"Message: {str(error)}\n")
                f.write(traceback.format_exc())
                f.write("\n")

    def debug_wrapper(self, node_name: str) -> Callable:
        def decorator(func: Callable) -> Callable:
            if asyncio.iscoroutinefunction(func) or inspect.isasyncgenfunction(func):

                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    input_state = args[0] if args else kwargs.get("state", {})

                    try:
                        output_state = await func(*args, **kwargs)

                        self.write_log(
                            node_name=node_name,
                            input_state=input_state,
                            output_state=output_state,
                            llm_response=self._extract_llm_response(output_state),
                            tool_calls=self._extract_tool_calls(output_state),
                        )

                        return output_state

                    except Exception as e:
                        self.write_log(
                            node_name=node_name,
                            input_state=input_state,
                            error=e,
                        )
                        raise

                return async_wrapper

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                input_state = args[0] if args else kwargs.get("state", {})

                try:
                    output_state = func(*args, **kwargs)

                    self.write_log(
                        node_name=node_name,
                        input_state=input_state,
                        output_state=output_state,
                        llm_response=self._extract_llm_response(output_state),
                        tool_calls=self._extract_tool_calls(output_state),
                    )

                    return output_state

                except Exception as e:
                    self.write_log(
                        node_name=node_name,
                        input_state=input_state,
                        error=e,
                    )
                    raise

            return sync_wrapper

        return decorator


debug_writer = DebugWriter()