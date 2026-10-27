import assert from "node:assert/strict";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";

import liveContextPolicy from "../../scripts/mac-mini/openclaw-plugins/openclaw-live-context-policy/dist/index.js";
import translationTool from "../../scripts/mac-mini/openclaw-plugins/openclaw-translation-tool/dist/index.js";
import weatherTool from "../../scripts/mac-mini/openclaw-plugins/openclaw-weather-tool/dist/index.js";

function makeJsonResponse(payload) {
  return {
    ok: true,
    status: 200,
    async json() {
      return payload;
    },
    async text() {
      return JSON.stringify(payload);
    }
  };
}

function makeTextResponse(payload) {
  return {
    ok: true,
    status: 200,
    async text() {
      return payload;
    }
  };
}

function installFetchStub() {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async (url) => {
    const target = String(url);
    if (target.includes("wikipedia.org/w/api.php?action=opensearch")) {
      return makeJsonResponse([
        "Нил Армстронг",
        ["Нил Армстронг"],
        ["Американский астронавт, первый человек на Луне."],
        ["https://ru.wikipedia.org/wiki/%D0%9D%D0%B8%D0%BB_%D0%90%D1%80%D0%BC%D1%81%D1%82%D1%80%D0%BE%D0%BD%D0%B3"]
      ]);
    }
    if (target.includes("wikipedia.org/api/rest_v1/page/summary")) {
      return makeJsonResponse({
        extract: "Нил Армстронг — американский астронавт и первый человек, ступивший на Луну.",
        content_urls: {
          desktop: {
            page: "https://ru.wikipedia.org/wiki/%D0%9D%D0%B8%D0%BB_%D0%90%D1%80%D0%BC%D1%81%D1%82%D1%80%D0%BE%D0%BD%D0%B3"
          }
        }
      });
    }
    if (target.startsWith("https://html.duckduckgo.com/html/?q=")) {
      return makeTextResponse(`
        <html><body>
          <a class="result__a" href="https://example.com/armstrong-biography">Neil Armstrong biography</a>
          <div class="result__snippet">Concise biography and Apollo 11 overview.</div>
          <a class="result__a" href="https://example.com/nasa-armstrong">NASA on Neil Armstrong</a>
          <div class="result__snippet">Official NASA profile and mission timeline.</div>
          <a class="result__a" href="https://example.com/moon-landing">Moon landing history</a>
          <div class="result__snippet">Background on the first Moon landing.</div>
        </body></html>
      `);
    }
    if (target === "https://example.com/armstrong-biography") {
      return makeTextResponse(`
        <html><body>
          <article>
            Neil Armstrong was an American astronaut, naval aviator, and the first person to walk on the Moon during Apollo 11.
          </article>
        </body></html>
      `);
    }
    if (target.startsWith("https://geocoding-api.open-meteo.com/v1/search")) {
      const decoded = decodeURIComponent(target);
      const name = decoded.includes("Saint Petersburg") ? "Санкт-Петербург" : decoded.includes("Tokyo") ? "Токио" : "Тестовый город";
      return makeJsonResponse({
        results: [{
          name,
          admin1: name === "Токио" ? "Токио" : name,
          country: name === "Токио" ? "Япония" : "Россия",
          latitude: name === "Токио" ? 35.6895 : 59.9386,
          longitude: name === "Токио" ? 139.6917 : 30.3141,
          timezone: name === "Токио" ? "Asia/Tokyo" : "Europe/Moscow"
        }]
      });
    }
    if (target.startsWith("https://api.open-meteo.com/v1/forecast")) {
      return makeJsonResponse({
        timezone: "Asia/Tokyo",
        current: {
          temperature_2m: 18,
          relative_humidity_2m: 70,
          apparent_temperature: 17,
          precipitation: 0.2,
          wind_speed_10m: 8,
          wind_direction_10m: 20,
          weather_code: 3
        },
        daily: {
          time: ["2026-05-20", "2026-05-21", "2026-05-22", "2026-05-23"],
          weather_code: [3, 61, 3, 2],
          temperature_2m_max: [19, 20, 16, 18],
          temperature_2m_min: [14, 14, 10, 11],
          precipitation_sum: [0.2, 12.5, 2.1, 0],
          precipitation_probability_max: [20, 90, 50, 10],
          wind_speed_10m_max: [12, 18, 20, 12]
        },
        hourly: {
          time: ["2026-05-20T12:00", "2026-05-21T12:00", "2026-05-22T12:00", "2026-05-23T12:00"],
          weather_code: [3, 61, 3, 2],
          temperature_2m: [18, 19, 13, 15],
          relative_humidity_2m: [70, 85, 80, 60],
          precipitation_probability: [20, 90, 50, 10],
          precipitation: [0.2, 3.2, 1.1, 0],
          wind_speed_10m: [8, 12, 10, 7],
          wind_direction_10m: [20, 30, 300, 250]
        }
      });
    }
    if (target.startsWith("https://air-quality-api.open-meteo.com/v1/air-quality")) {
      return makeJsonResponse({
        current: {
          european_aqi: 42,
          us_aqi: 68,
          pm2_5: 12.3,
          pm10: 18.4,
          nitrogen_dioxide: 8.5,
          ozone: 55.1
        }
      });
    }
    throw new Error(`Unexpected fetch URL in smoke test: ${target}`);
  };
  return () => {
    globalThis.fetch = originalFetch;
  };
}

function makeEmbeddedResult(text) {
  return { payloads: [{ text }] };
}

function createFakeApi(homeDir) {
  const tools = new Map();
  const hooks = new Map();
  const agentToolResultMiddlewares = [];

  return {
    tools,
    hooks,
    agentToolResultMiddlewares,
    logger: {
      info() {},
      warn() {},
      error() {}
    },
    config: {
      agents: {
        defaults: {
          workspace: process.cwd(),
          model: {
            primary: "openrouter/test-router"
          }
        }
      }
    },
    registerTool(definition) {
      tools.set(definition.name, definition);
    },
    registerAgentToolResultMiddleware(handler, options) {
      agentToolResultMiddlewares.push({ handler, options });
    },
    on(eventName, handler) {
      hooks.set(eventName, handler);
    },
    runtime: {
      agent: {
        async runEmbeddedPiAgent({ prompt }) {
          const text = String(prompt || "");
          if (text.includes("You are a routing classifier for an assistant.")) {
            return makeEmbeddedResult(JSON.stringify({
              intent: "general_chat",
              confidence: 0.52,
              needs_live_web: false,
              needs_live_datetime: false,
              needs_memory: false,
              needs_location: false,
              resolved_city: null,
              resolved_country: null,
              followup_required: false,
              followup_question: null
            }));
          }
          if (text.includes("You are a tool selection model for an assistant orchestrator.")) {
            return makeEmbeddedResult(JSON.stringify({
              top_tools: ["search_wikipedia", "web_search", "web_fetch"],
              intent: "research",
              notes: "Use complementary evidence types."
            }));
          }
          if (text.includes("You are an answer evaluator for an assistant orchestrator.")) {
            return makeEmbeddedResult(JSON.stringify({
              mode: "fusion",
              best_tool: "web_search",
              supporting_tools: ["search_wikipedia", "web_fetch"],
              final_answer: "Нил Армстронг — американский астронавт, первый человек на Луне. Вики дает краткую справку, а веб-источники добавляют контекст про Apollo 11 и профиль NASA."
            }));
          }
          if (text.includes("You are a translation engine.")) {
            return makeEmbeddedResult(JSON.stringify({
              translated_text: "привет мир",
              pronunciation: "privet mir",
              source_language: "en",
              target_language: "ru"
            }));
          }
          throw new Error(`Unexpected embedded prompt in smoke test.\n${text}`);
        }
      }
    },
    homeDir
  };
}

async function makeFakeHome() {
  const homeDir = await fs.mkdtemp(path.join(os.tmpdir(), "openclaw-smoke-home-"));
  const workspaceDir = path.join(homeDir, ".openclaw", "workspace");
  await fs.mkdir(workspaceDir, { recursive: true });
  await fs.writeFile(
    path.join(workspaceDir, "USER.md"),
    [
      "**Timezone:** Europe/Istanbul",
      "**City:** Istanbul",
      "**Country:** Turkey",
      "",
      "Пользователь предпочитает русский язык."
    ].join("\n"),
    "utf8"
  );
  await fs.writeFile(path.join(workspaceDir, "MEMORY.md"), "Слава prefers Russian.\n", "utf8");
  return homeDir;
}

async function testTranslationDefaultTarget() {
  const fakeHome = await makeFakeHome();
  const previousHome = process.env.HOME;
  process.env.HOME = fakeHome;
  try {
    const api = createFakeApi(fakeHome);
    translationTool.register(api);
    const tool = api.tools.get("translate_text");
    assert.ok(tool, "translate_text should be registered");

    const result = await tool.execute("tool-1", { text: "hello world" });
    assert.equal(result.details.provider, "internal-llm");
    assert.equal(result.details.target_language, "ru");
    assert.equal(result.details.translated_text, "привет мир");
    assert.equal(result.details.pronunciation, "privet mir");
  } finally {
    process.env.HOME = previousHome;
    await fs.rm(fakeHome, { recursive: true, force: true });
  }
}

async function testParallelSearchOrchestration() {
  const fakeHome = await makeFakeHome();
  const previousHome = process.env.HOME;
  process.env.HOME = fakeHome;
  const restoreFetch = installFetchStub();
  try {
    const api = createFakeApi(fakeHome);
    liveContextPolicy.register(api);
    const beforePromptBuild = api.hooks.get("before_prompt_build");
    const beforeToolCall = api.hooks.get("before_tool_call");
    const afterToolCall = api.hooks.get("after_tool_call");
    const beforeMessageWrite = api.hooks.get("before_message_write");
    const parallelSearch = api.tools.get("parallel_search");

    assert.ok(beforePromptBuild, "before_prompt_build hook should be registered");
    assert.ok(beforeToolCall, "before_tool_call hook should be registered");
    assert.ok(afterToolCall, "after_tool_call hook should be registered");
    assert.ok(beforeMessageWrite, "before_message_write hook should be registered");
    assert.ok(parallelSearch, "parallel_search tool should be registered");

    const ctx = { trigger: "user", sessionKey: "search-session", sessionId: "search-session-id" };
    const promptResult = await beforePromptBuild({
      prompt: "Кто такой Нил Армстронг?",
      messages: []
    }, ctx);

    assert.ok(promptResult?.prependSystemContext?.includes('TURN_TOOL_ALLOWLIST: ["parallel_search"]'));
    assert.ok(promptResult?.prependSystemContext?.includes('"execution_mode":"deterministic_parallel_search"'));
    assert.ok(promptResult?.prependSystemContext?.includes('"name":"search_wikipedia"'));

    const blocked = await beforeToolCall({
      toolName: "web_search",
      params: { query: "Кто такой Нил Армстронг?" }
    }, ctx);
    assert.equal(blocked?.block, true);

    const rewritten = await beforeToolCall({
      toolName: "parallel_search",
      params: {}
    }, ctx);
    assert.equal(rewritten?.params?.query, "Кто такой Нил Армстронг?");
    assert.equal(rewritten?.params?.selected_tools, undefined);

    const toolResult = await parallelSearch.execute("parallel-1", rewritten.params);
    assert.equal(toolResult.details.status, "ok");
    assert.equal(toolResult.details.envelopes.length, 3);
    assert.deepEqual(toolResult.details.selected_tools, ["search_wikipedia", "web_search", "web_fetch"]);
    assert.equal(toolResult.details.evaluation.mode, "fusion");
    assert.equal(toolResult.details.evaluation.bestTool, "web_search");
    assert.match(toolResult.content[0].text, /Нил Армстронг/u);

    await afterToolCall({
      toolName: "parallel_search",
      result: toolResult
    }, ctx);

    const messagePatch = await beforeMessageWrite({
      message: {
        role: "assistant",
        content: [{ type: "text", text: "черновик" }]
      }
    }, ctx);

    const finalText = messagePatch.message.content.find((block) => block?.type === "text")?.text || "";
    assert.equal(finalText, toolResult.content[0].text);
    assert.ok(!messagePatch?.message?.content?.some((block) => block?.type === "thinking"));

    const postToolPrompt = await beforePromptBuild({
      prompt: "Кто такой Нил Армстронг?",
      messages: [
        { role: "user", content: [{ type: "text", text: "Кто такой Нил Армстронг?" }] },
        { role: "toolResult", content: [{ type: "text", text: toolResult.content[0].text }] }
      ]
    }, { ...ctx, trigger: "tool_result" });

    assert.ok(postToolPrompt?.prependSystemContext?.includes("TURN_ALREADY_RESOLVED"));
    assert.ok(postToolPrompt?.prependSystemContext?.includes("Do not call parallel_search"));
  } finally {
    restoreFetch();
    process.env.HOME = previousHome;
    await fs.rm(fakeHome, { recursive: true, force: true });
  }
}

async function testWeatherIntentRouting() {
  const fakeHome = await makeFakeHome();
  const previousHome = process.env.HOME;
  process.env.HOME = fakeHome;
  try {
    const api = createFakeApi(fakeHome);
    liveContextPolicy.register(api);
    const beforePromptBuild = api.hooks.get("before_prompt_build");
    const beforeToolCall = api.hooks.get("before_tool_call");
    const beforeMessageWrite = api.hooks.get("before_message_write");
    assert.ok(api.agentToolResultMiddlewares.length > 0, "weather terminal tool-result middleware should be registered");
    const ctx = { trigger: "user", sessionKey: "weather-session", sessionId: "weather-session-id" };
    const promptResult = await beforePromptBuild({
      prompt: "Какая погода завтра в Токио?",
      messages: [{ role: "user", content: [{ type: "text", text: "Какая погода завтра в Токио?" }] }]
    }, ctx);
    assert.ok(promptResult?.prependSystemContext?.includes('TURN_TOOL_ALLOWLIST: ["get_weather"]'));
    assert.ok(promptResult?.prependSystemContext?.includes('"intent":"weather"'));
    assert.ok(promptResult?.prependSystemContext?.includes('"execution_mode":"guided_weather"'));
    assert.ok(promptResult?.prependSystemContext?.includes('"resolved_city":null'));

    const rewritten = await beforeToolCall({
      toolName: "get_weather",
      params: {}
    }, ctx);
    assert.equal(rewritten?.params?.city, undefined, "weather routing must not inject owner default city");

    const messagePatch = await beforeMessageWrite({
      message: {
        role: "assistant",
        content: [{ type: "text", text: "черновик" }]
      }
    }, ctx);
    assert.equal(
      messagePatch.message.content.some((block) => block?.type === "toolCall" && block?.name === "get_weather"),
      false,
      "weather routing must not synthesize get_weather calls"
    );
    assert.equal(
      messagePatch.message.content.find((block) => block?.type === "text")?.text,
      "черновик",
      "weather routing must not replace the answer with fallback weather"
    );

    const afterWeatherToolCall = await api.hooks.get("after_tool_call")({
      toolName: "get_weather",
      params: { location: "Tokyo", day_offset: 1 },
      result: {
        content: [{ type: "text", text: "2026-05-21 в Токио: 14…20°C, сильный дождь." }],
        details: {
          status: "ok",
          resolvedLocation: { name: "Tokyo", displayName: "Tokyo, Japan" },
          startOffset: 1,
          requestedDays: 1
        }
      }
    }, ctx);
    assert.equal(afterWeatherToolCall?.terminate, true, "successful weather after_tool_call should terminate the pi agent loop");
    assert.match(afterWeatherToolCall?.content?.[0]?.text || "", /Токио/, "weather after_tool_call should preserve the tool result text");

    const middlewareResult = await api.agentToolResultMiddlewares[0].handler({
      toolName: "get_weather",
      isError: false,
      result: {
        content: [{ type: "text", text: "2026-05-21 в Токио: 14…20°C, сильный дождь." }],
        details: { status: "ok" }
      }
    }, ctx);
    assert.equal(middlewareResult?.result?.terminate, true, "successful weather tool result should terminate the pi agent loop");

    const duplicate = await beforeToolCall({
      toolName: "get_weather",
      params: { location: "Tokyo", day_offset: 1 }
    }, ctx);
    assert.equal(duplicate?.block, true, "exact duplicate weather lookup should be blocked after a successful result");

    await api.hooks.get("tool_result_persist")({
      toolName: "get_weather",
      message: {
        content: [{ type: "text", text: "This exact weather lookup already succeeded for this turn." }],
        details: { status: "blocked" }
      }
    }, ctx);

    const duplicateAfterBlockedResult = await beforeToolCall({
      toolName: "get_weather",
      params: { location: "Tokyo", day_offset: 1 }
    }, ctx);
    assert.equal(
      duplicateAfterBlockedResult?.block,
      true,
      "blocked duplicate result must not erase the previous successful weather state"
    );

    const finalPatch = await beforeMessageWrite({
      message: {
        role: "assistant",
        stopReason: "toolUse",
        content: [
          { type: "toolCall", name: "get_weather", arguments: { location: "Tokyo", day_offset: 1 } },
          { type: "text", text: "" }
        ]
      }
    }, ctx);
    assert.equal(
      finalPatch.message.content.some((block) => block?.type === "toolCall"),
      false,
      "successful weather result should suppress another weather tool call"
    );
    assert.match(
      finalPatch.message.content.find((block) => block?.type === "text")?.text || "",
      /Токио/u,
      "successful weather result should be used as final weather answer"
    );
    assert.equal(
      finalPatch.message.stopReason,
      "stop",
      "successful weather result should finalize the assistant turn instead of continuing toolUse loop"
    );
  } finally {
    process.env.HOME = previousHome;
    await fs.rm(fakeHome, { recursive: true, force: true });
  }
}

async function testWeatherDeterministicDispatchHook() {
  const fakeHome = await makeFakeHome();
  const previousHome = process.env.HOME;
  process.env.HOME = fakeHome;
  const restoreFetch = installFetchStub();
  try {
    const api = createFakeApi(fakeHome);
    weatherTool.register(api);
    const beforeDispatch = api.hooks.get("before_dispatch");
    assert.ok(beforeDispatch, "weather before_dispatch hook should be registered");

    const tokyo = await beforeDispatch({
      body: "Какая погода завтра в Токио?"
    }, { sessionKey: "weather-dispatch-tokyo" });
    assert.equal(tokyo?.handled, true, "weather hook should claim a clear weather turn");
    assert.match(tokyo?.text || "", /Токио/u, "weather hook should return a user-facing weather reply");
    assert.match(tokyo?.text || "", /2026-05-21|Завтра/u, "weather hook should preserve tomorrow semantics");
    assert.doesNotMatch(tokyo?.text || "", /null/u, "weather hook must not leak null Open-Meteo fields");

    const piter = await beforeDispatch({
      body: "А в Питере на следующие 3 дня?"
    }, { sessionKey: "weather-dispatch-piter" });
    assert.equal(piter?.handled, true, "weather hook should normalize colloquial city names");
    assert.match(piter?.text || "", /Санкт-Петербург/u, "weather hook should normalize Питер to Saint Petersburg");
    assert.match(piter?.text || "", /3 дн/u, "weather hook should preserve multi-day semantics");

    const unrelated = await beforeDispatch({
      body: "Кто такой Нил Армстронг?"
    }, { sessionKey: "weather-dispatch-unrelated" });
    assert.equal(unrelated, undefined, "weather hook must not claim unrelated turns");
  } finally {
    restoreFetch();
    process.env.HOME = previousHome;
    await fs.rm(fakeHome, { recursive: true, force: true });
  }
}

async function main() {
  await testTranslationDefaultTarget();
  await testWeatherDeterministicDispatchHook();
  await testWeatherIntentRouting();
  await testParallelSearchOrchestration();
  console.log("openclaw orchestrator local smoke: ok");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
