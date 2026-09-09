# WIBT tool

The multi-agent pipeline behind [Wetenschap in begrijpelijke taal](https://ubvu.github.io/wibt/) (WIBT), a research project by the KB Nationale Bibliotheek, the VU University Library, and the VU Computer Science department.

Give it a scientific paper (PDF) and it generates a Dutch, plain-language summary, tailored to one of three audiences — general public, GZ-psychologists, or information specialists at the Dutch parliament (Tweede Kamer) — while scoring the result on readability and factual accuracy against the source paper.

Project background, evaluation results, and publications: **[ubvu.github.io/wibt](https://ubvu.github.io/wibt/)**.

## How it works

1. The pipeline generates several candidate English summaries of the paper.
2. Each candidate is scored on readability (syntactic clarity, jargon, information density, structural cohesion) and factuality — faithfulness (does every sentence follow from the paper?) and completeness (does the summary cover the paper's key facts?).
3. The highest-scoring summary is translated into Dutch through a chain of drafting, refinement, and proofreading agents.

Prompts are organized per audience (`general`, `psychology`, `tweede-kamer`) under `prompts/`, so tuning the tone or jargon rules for one audience doesn't require touching any code. See [CLAUDE.md](CLAUDE.md) for the full pipeline architecture.

## Getting started

Requires Python 3.14+.

```bash
uv sync                # or: pip install -e .
cp .env.example .env   # then fill in your endpoint credentials and model settings
```

There's no `.env.example` in the repository yet — see `AppConfig.from_env()` in [`src/config.py`](src/config.py) for the full list of required variables (API endpoint, default prompt context, and a model + temperature pair per agent).

**Try the interactive demo** (Marimo notebook):

```bash
marimo run src/gui/summary.py
```

**Or run it from the command line:**

```bash
python src/cli/summary.py -sc general -fc general -tc general -it 5 -i paper.pdf -st refine
```

Run any script in `src/cli/` with `--help` for its full set of options.

## Models

Built and evaluated with open models — gpt-oss-120b, Gemma3-12b, and TranslateGemma-12b — served via the VU Nebula AI infrastructure and the SURF AI-hub (WiLLMa). Any OpenAI-compatible endpoint works; set it through `OPEN_AI_URL` and `OPEN_AI_TOKEN`.

## License

MIT — see [LICENSE](LICENSE). Copyright University Library, Vrije Universiteit Amsterdam.
