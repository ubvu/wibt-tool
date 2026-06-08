# Project Overview: Wetenschap in Begrijpbare Taal

## Introduction
This project, "Wetenschap in Begrijpbare Taal" (Science in Understandable Language), provides a suite of AI-driven tools designed to process scientific text. It focuses on making scientific information more accessible through high-quality summarization, translation, and rigorous fact-checking.

The project utilizes an **agentic workflow** architecture, where multiple specialized Large Language Model (LLM) agents collaborate to perform complex reasoning and transformation tasks.

---

## Core Workflows

### 1. Summarization Workflow
Converts complex scientific text into a simplified, understandable version.
- **Process**: Summarization $\rightarrow$ Readability/Evaluation $\rightarrow$ Refinement.
- **Key Agents**: `SummaryAgent`, `ReadEvalAgent`, `RefinementAgent`.

### 2. Translation Workflow
Translates content while maintaining semantic accuracy and scientific nuance.
- **Process**: Pre-draft $\rightarrow$ Draft $\rightarrow$ Refine Draft $\rightarrow$ Proofread (or Direct Translation).
- **Key Agents**: `TranslationPreDraftAgent`, `TranslationDraftAgent`, `TranslationRefineDraftAgent`, `TranslationProofreadAgent`, `TranslationDirectAgent`.

### 3. Factuality Evaluation Workflow
A multi-step verification process to ensure that summaries and translations do not introduce inaccuracies.
- **Process**: Fact Extraction $\rightarrow$ Fact Validation $\rightarrow$ Fact Alignment (comparing source vs. target) $\rightarrow$ Adjudication (resolving conflicts).
- **Key Agents**: `FactExtractorAgent`, `FactValidatorAgent`, `FactAlignmentAgent`, `ArgumentAgent` (Advocate/Skeptic), `AdjudicatorAgent`.

---

## Project Structure

### Root Directory
- `LICENSE`: Project license.
- `README.md`: Basic project information.
- `pyproject.toml`: Python project configuration and dependencies.
- `prompts/`: Centralized repository for LLM prompt templates.
  - `factuality_evaluation/`: Prompts for the fact-checking workflow.
  - `summary/`: Prompts for the summarization workflow.
  - `translation/`: Prompts for the translation workflow.

### Source Code (`src/`)
- **`agent_factory.py`**: The central factory for assembling agents, injecting configuration, prompts, and LLM connections.
- **`agents/`**: Implementation of specialized AI agents.
  - `agent.py`: Base class defining common agent behavior.
  - `[name]_agent.py`: Specific agent implementations (e.g., `SummaryAgent`, `FactExtractorAgent`).
- **`cli/`**: Command-line interfaces for running workflows (alignment, extraction, summary, translation).
- **`config.py`**: Configuration management using `dataclasses` and environment variables.
- **`create_summary.py` / `create_translation.py`**: Entry-point scripts for common tasks.
- **`factuality/`**: Core logic for factuality assessment and alignment.
- **`gui/`**: Graphical User Interface components for interacting with the tools.
- **`models/`**: Data models representing domain entities (e.g., `Argument`, `Judgement`, `KeyFact`).
- **`prompt_manager.py`**: Logic for loading and managing prompt templates with support for context-specific fallbacks.
- **`summary_orchestrator.py`**: Orchestrates the sequence of agents for the summarization process.
- **`translation_orchestrator.py`**: Orchestrates the sequence of agents for the translation process.
- **`tools/`**: Utility scripts and batch processing tools (many are `.sh` scripts).
- **`utils/`**: General-purpose utility functions (JSON handling, OpenAI client, string manipulation).

---

## Technical Architecture Notes

- **Agentic Design**: Instead of a single prompt, complex tasks are broken down into a sequence of specialized agents.
- **Prompt Decoupling**: Prompts are stored in external `.txt` files, allowing for rapid iteration without changing code. The `PromptManager` handles hierarchical loading (context-specific vs. default).
- **Configuration-Driven**: The entire behavior of the system (which models to use, temperatures, API settings) is managed through environment variables via `AppConfig`.
- **Data Modeling**: Strong typing is used via Python `dataclasses` to represent complex states like arguments and judgments.
