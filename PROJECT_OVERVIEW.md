# Project Overview: Wetenschap in Begrijpbare Taal

## Introduction
This project, "Wetenschap in Begrijpbare Taal" (Science in Understandable Language), provides a suite of AI-driven tools designed to process scientific text. It focuses on making scientific information more accessible through high-quality summarization, translation, and rigorous fact-checking.

The project utilizes an **agentic workflow** architecture, where multiple specialized Large Language Model (LLM) agents collaborate to perform complex reasoning and transformation tasks.

---

## Current Status
> **Note:** The project is undergoing a significant restructuring into a modular package (`wibt_tool`) to support WASM/Pyodide deployment.

- **Status**: Phase 2 (Refactoring & Cleanup) is currently **In Progress**.
- **Primary Usage (Main Workflows)**:
  - **Summarization**: Managed via `apps/cli/summary.py`.
  - **Translation**: Managed via `apps/cli/translation.py` (may also serve as a tool).
- **Tools (Refactored)**:
  - **Fact Extraction**: `apps/tools/extraction.py`.
  - **Fact Alignment**: `apps/tools/alignment.py`.
- **GUI**:
  - The Graphical User Interface (`apps/gui/`) is currently undergoing a full rewrite to be compatible with the new architecture and marimo/WASM.

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
- `AGENTS.md`: Documentation for LLM agent instructions.
- `LICENSE`: Project license.
- `README.md`: Basic project information.
- `TODO.md`: Project roadmap and task tracking.
- `pyproject.toml`: Python project configuration and dependencies (using `uv`).
- `prompts/`: Centralized repository for LLM prompt templates, organized by context.
  - `factuality_evaluation/`: Prompts for the fact-checking workflow.
  - `summary/`: Prompts for the summarization workflow.
  - `translation/`: Prompts for the translation workflow.

### Source Code (`src/wibt_tool/`)
The core logic is encapsulated in the `wibt_tool` package.
- **`agent_factory.py`**: The central factory for assembling agents, injecting configuration, prompts, and LLM connections.
- **`agents/`**: Implementation of specialized AI agents (e.g., `SummaryAgent`, `FactExtractorAgent`).
- **`pipelines/`**: Orchestration logic for complex workflows.
  - `summary_pipeline.py`: Iterative summarization loop.
  - `translation_pipeline.py`: Sequential translation pipeline.
- **`config.py`**: Configuration management using `dataclasses` and environment variables.
- **`factuality/`**: Core logic for factuality assessment and alignment.
- **`models/`**: Data models representing domain entities (e.g., `Argument`, `Judgement`, `KeyFact`).
- **`prompt_manager.py`: Logic for loading and managing prompt templates with support for context-specific fallbacks and WASM compatibility.
- **`utils/`: General-purpose utility functions (JSON handling, OpenAI client, etc.).

### Applications (`apps/`)
Client applications that utilize the `wibt_tool` library.
- **`cli/`**: Command-line interfaces for primary workflows (e.g., `summary.py`, `translation.py`).
- **`tools/`**: Utility tools for specific tasks (e.g., `alignment.py`, `extraction.py`).
- **`gui/`**: Graphical User Interface components (marimo/WASM target).

---

## Technical Architecture Notes

- **Agentic Design**: Instead of a single prompt, complex tasks are broken down into a sequence of specialized agents.
- **Prompt Decoupling**: Prompts are stored in external `.txt` files, allowing for rapid iteration without changing code. The `PromptManager` handles hierarchical loading.
- **Configuration-Driven**: The entire behavior of the system is managed through environment variables via `AppConfig`.
- **WASM Compatibility**: The architecture is designed to be portable, using `importlib.resources` for asset management and abstracting file I/O to support virtual filesystems.

---

## Dependency Trace: `apps/cli/summary.py`
`apps/cli/summary.py` is the primary entry point for the main summarization and translation workflow.

### 1. Pipeline & Flow Control
*   **`apps/cli/summary.py`**: The CLI entry point that parses arguments and starts the process.
*   **`src/wibt_tool/pipelines/summary_pipeline.py`**: An iterative pipeline that optimizes summary quality through a loop of generation, evaluation, and refinement.
*   **`src/wibt_tool/pipelines/translation_pipeline.py`**: (Conditional) A sequential pipeline that produces a polished translation through drafting, refinement, and proofreading.

### 2. Agent System
The pipelines rely on the `AgentFactory` to instantiate specialized agents defined in `src/wibt_tool/agents/`:
*   **Summarization Loop**:
    *   `SummaryAgent`, `ReadEvalAgent`, `RefinementAgent`.
*   **Factuality Loop**:
    *   `FactExtractorAgent`, `FactValidatorAgent`, `FactAlignmentAgent`, `ArgumentAgent` (Advocate/Skeptic), `AdjudicatorAgent`.
*   **Translation (Conditional)**:
    *   `TranslationPreDraftAgent`, `TranslationDraftAgent`, `TranslationRefineDraftAgent`, `TranslationProofreadAgent`, `TranslationDirectAgent`.

### 3. Data & Configuration
*   **`src/wibt_tool/models/`**: Data models passed between agents (e.g., `Argument`, `Judgement`).
*   **`src/wibt_tool/config.py`**: Loads environment variables and provides `AppConfig`.
*   **`src/wibt_tool/prompt_manager.py`**: Handles retrieval of prompt templates from `src/wibt_tool/prompts/`.

### 4. Infrastructure & Utilities
*   **`src/wibt_tool/agent_factory.py`**: The central assembly point for all agents.
*   **`src/wibt_tool/utils/openai_client.py`**: Low-level interface for LLM communication.
*   **`src/wibt_tool/utils/`**: General purpose helpers.
