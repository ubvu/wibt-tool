# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

wibt-tool is the multi-agent pipeline for the "Wetenschap in Begrijpelijke Taal" research project. It takes a scientific paper and produces a Dutch, plain-language summary, tailored to one of three audiences (general public, GZ-psychologists, or Tweede Kamer information specialists), evaluated along the way for readability and factual accuracy.

## Commands

Requires Python >= 3.14. Dependencies are declared in `pyproject.toml` (no committed lockfile — `uv.lock` is gitignored); install with `uv sync` or `pip install -e .`.

No test suite exists yet, despite `pytest`/`pytest-cov` being declared as dev dependencies in `pyproject.toml`.

Configuration is read entirely from environment variables via `.env` (see `src/config.py`). Required:
- `OPEN_AI_TOKEN`, `OPEN_AI_URL` — the OpenAI-compatible endpoint (VU Nebula, SURF AI-hub/WiLLMa, or a custom endpoint)
- `DEFAULT_CONTEXT` — fallback prompt context (`general`, `psychology`, or `tweede-kamer`)
- `PROMPT_ROOT_DIR` — defaults to `prompts` in the working directory
- Per-agent model + temperature, one pair per agent: `DEFAULT_<PREFIX>_MODEL` / `DEFAULT_<PREFIX>_MODEL_TEMP`, where `<PREFIX>` is one of `SUMMARY`, `REFINEMENT`, `READ_EVAL`, `PREDRAFT`, `DRAFT`, `REFINE_DRAFT`, `PROOFREAD`, `DIRECT_TRANSLATION`, `FACT_EXTRACTION`, `ALIGNMENT`, `ADVOCATE`, `SKEPTIC`, `ADJUDICATOR`
- `DEFAULT_FACT_VALIDATION_MODEL` / `DEFAULT_FACT_VALIDATION_MODEL_TEMP` — comma-separated, one entry per fact-validator (three are used)

Run `python src/config.py` to check that a `.env` file loads correctly.

**GUI (Marimo notebooks, the interactive demo):**
```
marimo run src/gui/summary.py       # summarization + evaluation demo
marimo run src/gui/translation.py   # translation-only demo
```
Use `marimo edit` instead of `run` to open them in the editable notebook view.

**CLI (batch/scripted use):** `src/cli/summary.py`, `src/cli/translation.py`, `src/cli/extraction.py`, `src/cli/alignment.py`. Example:
```
python src/cli/summary.py -sc general -fc general -tc general -it 5 -i paper.pdf -st refine
```
Run any CLI script with `--help` for its full flag list (context selection, iteration count, input/output paths, `-st refine|static` search mode, `-pf` to reuse pre-extracted facts).

## Architecture

**Config → Factory → Orchestrators.** `AppConfig.from_env()` (`src/config.py`) loads every model/temperature setting and prompt directory path. `AgentFactory` (`src/agent_factory.py`) is the only place that constructs agents — it wires each `Agent` subclass to its model settings (from config) and its prompt text (from `PromptManager`). Orchestrators never construct agents directly; they call the factory.

**Prompts are file-based and context-aware, not hardcoded.** `PromptManager` (`src/prompt_manager.py`) loads prompt text from `prompts/{summary,translation,factuality_evaluation}/<context>/*.txt`, where `<context>` is `general`, `psychology`, or `tweede-kamer`. If a file is missing for the requested context, it silently falls back to `prompts/<task>/<DEFAULT_CONTEXT>/...` and logs a warning. To add or change agent behavior for one audience, edit the prompt `.txt` file — the Python code is audience-agnostic.

**Agent base class.** `agents/agent.py` defines `Agent`: a thin wrapper around an LLM endpoint that tracks message history (with a configurable window, `-1` = unbounded), and `send_messages_structured()`, which retries a call until the response parses as JSON and validates against a given Pydantic model — every agent that needs structured output (scores, key-fact lists, judgements) goes through this retry loop rather than trusting the model's JSON on the first try.

**Two orchestration pipelines, run in sequence:**

1. `SummaryOrchestrator` (`src/summary_orchestrator.py`) generates and scores candidate English summaries:
   - Summary generation and key-fact extraction run concurrently (`ThreadPoolExecutor`) unless `provide_facts` reuses already-extracted facts.
   - Key facts go through 3 validator agents; only facts every validator accepts survive (`_filter_by_veto_vote` — a single "no" vote drops the fact; `_filter_by_majority_vote` exists but is unused by the veto path).
   - Each candidate summary is scored on readability (`read_eval_agent`, one prompt covering syntactic clarity/jargon/information density/structural cohesion), faithfulness (Advocate + Skeptic argue per sentence, in parallel, then an Adjudicator rules — score = fraction of sentences judged faithful, floored to a 1-5 scale), and completeness (an alignment agent checks which validated key facts appear in the summary).
   - If `search_method="refine"`, a `RefinementAgent` rewrites the summary's system prompt based on the current best candidate's scores and the loop tries again, up to `iterations` times or until every score reaches 4+ (`_is_sufficient_score`). If `search_method="static"`, the same prompt is reused each iteration.
   - Candidates are ranked lexicographically by `(faithfulness, completeness, syntactic_clarity, jargon, information_density, structural_cohesion)` — faithfulness dominates the ranking.

2. `TranslationOrchestrator` (`src/translation_orchestrator.py`) takes the winning summary and produces the Dutch version through a fixed agent chain (no scoring/looping here): a direct-translation agent (TranslateGemma-based) produces a baseline translation used as a reference → pre-draft agent flags translation difficulties → draft agent produces a first draft (seeded with the pre-draft agent's conversation history via `set_messages`) → refine-draft agent polishes it → proofread agent makes final small edits.

**GUI vs. CLI are two thin front ends over the same orchestrators** — `src/gui/*.py` are Marimo notebook apps (interactive, single-run) with reusable components in `src/gui/components/` (model/endpoint selection, file input); `src/cli/*.py` are argparse scripts for batch/scripted runs. Neither contains pipeline logic itself.
