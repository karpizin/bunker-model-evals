import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "benchmarking" / "tool_call_normalizer.py"
SPEC = importlib.util.spec_from_file_location("tool_call_normalizer", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ToolCallNormalizerTest(unittest.TestCase):
    def test_strips_only_leading_orphan_reasoning_closers(self) -> None:
        self.assertEqual(
            MODULE.strip_orphan_reasoning_closers('</think>  {"answer":"ok"}'),
            '{"answer":"ok"}',
        )
        leaked = '<think>private reasoning</think>{"answer":"ok"}'
        self.assertEqual(MODULE.strip_orphan_reasoning_closers(leaked), leaked)

    def test_openai_native_call(self) -> None:
        normalized = MODULE.normalize_tool_response(
            "",
            {
                "tool_calls": [
                    {
                        "id": "native-1",
                        "type": "function",
                        "function": {
                            "name": "weather",
                            "arguments": '{"location":"Москва"}',
                        },
                    }
                ]
            },
        )

        self.assertEqual(normalized["source_format"], "openai_tool_calls")
        self.assertEqual(normalized["tool_calls"][0]["name"], "weather")
        self.assertEqual(normalized["tool_calls"][0]["arguments"]["location"], "Москва")

    def test_hermes_json_tag(self) -> None:
        normalized = MODULE.normalize_tool_response(
            '<tool_call>{"name":"wiki_search","arguments":{"query":"Тесла"}}</tool_call>'
        )

        self.assertEqual(normalized["source_format"], "tagged_tool_call")
        self.assertEqual(normalized["tool_calls"][0]["name"], "wiki_search")

    def test_qwen_parameter_tags(self) -> None:
        normalized = MODULE.normalize_tool_response(
            "<tool_call><function=weather><parameter=location>Питер</parameter></function></tool_call>"
        )

        self.assertEqual(normalized["tool_calls"][0]["arguments"]["location"], "Питер")

    def test_mimo_short_closing_tag(self) -> None:
        normalized = MODULE.normalize_tool_response(
            '<tool_call><function=shell>{"command":"echo status"}</>'
        )

        envelope = MODULE.canonical_tool_envelope(normalized)
        self.assertEqual(envelope["tool"], "shell")
        self.assertEqual(envelope["args"]["command"], "echo status")

    def test_mistral_tool_calls(self) -> None:
        normalized = MODULE.normalize_tool_response(
            '[TOOL_CALLS] [{"name":"clock","arguments":{}}]'
        )

        self.assertEqual(normalized["source_format"], "mistral_tool_calls")
        self.assertEqual(normalized["tool_calls"][0]["name"], "clock")

    def test_minimax_singleton_agent_array(self) -> None:
        normalized = MODULE.normalize_tool_response(
            '[{"calls":[{"tool":"weather.forecast","args":{"place":"Казань"}}],'
            '"answer":null}]'
        )

        action = MODULE.canonical_agent_action(normalized)
        self.assertEqual(normalized["source_format"], "json_singleton_list")
        self.assertEqual(action["calls"][0]["tool"], "weather.forecast")
        self.assertEqual(action["calls"][0]["args"]["place"], "Казань")

    def test_lfm_python_style_calls(self) -> None:
        normalized = MODULE.normalize_tool_response(
            "<|tool_call_start|>[weather.forecast(place='Питер'), maps.route(profile='bicycle')]"
            "<|tool_call_end|>"
        )

        action = MODULE.canonical_agent_action(normalized)
        self.assertEqual(normalized["source_format"], "lfm_tool_calls")
        self.assertEqual(
            [call["tool"] for call in action["calls"]],
            ["weather.forecast", "maps.route"],
        )

    def test_gemma_agent_envelope_inside_tool_tag(self) -> None:
        normalized = MODULE.normalize_tool_response(
            '<|tool_call>call:{"calls":[{"tool":"metrics.read","args":{}}],'
            '"answer":null}<tool_call|>'
        )

        action = MODULE.canonical_agent_action(normalized)
        self.assertEqual(normalized["source_format"], "gemma4_tool_call")
        self.assertEqual(action["calls"][0]["tool"], "metrics.read")

    def test_orphan_think_closing_tag_is_ignored(self) -> None:
        normalized = MODULE.normalize_tool_response(
            '</think>{"calls":[{"tool":"web.search","args":{}}],"answer":null}'
        )

        action = MODULE.canonical_agent_action(normalized)
        self.assertEqual(action["calls"][0]["tool"], "web.search")

    def test_calls_object_is_normalized_to_one_call(self) -> None:
        normalized = MODULE.normalize_tool_response(
            '{"calls":{"tool":"approval.request","args":{"operation":"restart"}}}'
        )

        action = MODULE.canonical_agent_action(normalized)
        self.assertEqual(len(action["calls"]), 1)
        self.assertEqual(action["calls"][0]["tool"], "approval.request")

    def test_repairs_extra_array_closer_after_agent_envelope(self) -> None:
        normalized = MODULE.normalize_tool_response(
            '{"calls":[{"tool":"weather.forecast","args":{}}]}]'
        )

        action = MODULE.canonical_agent_action(normalized)
        self.assertEqual(normalized["source_format"], "repaired_json_envelope")
        self.assertEqual(action["calls"][0]["tool"], "weather.forecast")

    def test_repairs_answer_outside_agent_envelope(self) -> None:
        normalized = MODULE.normalize_tool_response(
            '{"calls":[{"tool":"web.search","args":{}}]},"answer":null}'
        )

        action = MODULE.canonical_agent_action(normalized)
        self.assertEqual(normalized["source_format"], "repaired_json_envelope")
        self.assertEqual(action["calls"][0]["tool"], "web.search")

    def test_repairs_missing_call_closer(self) -> None:
        normalized = MODULE.normalize_tool_response(
            '{"calls":[{"tool":"inventory.cache","args":{"team":"Delta"}],"answer":null}'
        )

        action = MODULE.canonical_agent_action(normalized)
        self.assertEqual(normalized["source_format"], "repaired_json_envelope")
        self.assertEqual(action["calls"][0]["tool"], "inventory.cache")

    def test_repairs_extra_root_and_array_closer_before_answer(self) -> None:
        normalized = MODULE.normalize_tool_response(
            '{"calls":[{"tool":"web.search","args":{}},'
            '{"tool":"wiki.search","args":{}}]}],"answer":null}'
        )

        action = MODULE.canonical_agent_action(normalized)
        self.assertEqual(normalized["source_format"], "repaired_json_envelope")
        self.assertEqual(
            [call["tool"] for call in action["calls"]],
            ["web.search", "wiki.search"],
        )

    def test_gemma4_tool_call(self) -> None:
        normalized = MODULE.normalize_tool_response(
            '<|tool_call>call:weather{location:<|"|>Москва<|"|>,days:3}<tool_call|>'
        )

        self.assertEqual(normalized["source_format"], "gemma4_tool_call")
        self.assertEqual(normalized["tool_calls"][0]["arguments"]["days"], 3)

    def test_deepseek_dsml_tool_call(self) -> None:
        normalized = MODULE.normalize_tool_response(
            '<｜DSML｜tool_calls><｜DSML｜invoke name="weather">'
            '<｜DSML｜parameter name="location" string="true">Москва</｜DSML｜parameter>'
            '<｜DSML｜parameter name="days" string="false">3</｜DSML｜parameter>'
            '</｜DSML｜invoke></｜DSML｜tool_calls>'
        )

        self.assertEqual(normalized["source_format"], "deepseek_tool_call")
        self.assertEqual(normalized["tool_calls"][0]["arguments"]["location"], "Москва")

    def test_deepseek_r1_tool_call(self) -> None:
        normalized = MODULE.normalize_tool_response(
            '<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>function<｜tool▁sep｜>weather\n'
            '```json\n{"location":"Москва"}\n```'
            '<｜tool▁call▁end｜><｜tool▁calls▁end｜>'
        )

        self.assertEqual(normalized["source_format"], "deepseek_tool_call")
        self.assertEqual(normalized["tool_calls"][0]["name"], "weather")

    def test_embedded_example_is_not_executed(self) -> None:
        content = (
            'Example only: <tool_call>{"name":"shell",'
            '"arguments":{"command":"rm -rf /"}}</tool_call>'
        )
        normalized = MODULE.normalize_tool_response(content)

        self.assertEqual(normalized["source_format"], "plain_text")
        self.assertEqual(normalized["tool_calls"], [])


if __name__ == "__main__":
    unittest.main()
