# Project TODO: WIBT-Tool Restructuring

This document tracks the roadmap for restructuring the project into a robust, WASM-compatible package while addressing technical debt and broken components.

## 🛠 Phase 1: Core Migration & Namespace Integrity (Immediate)
*Goal: Stabilize the project structure and fix the broken imports.*

- [ ] **Move Prompts to Package Resources**: Move `prompts/` to `src/wibt_tool/prompts/`.
- [ ] **Update PromptManager**: Refactor `PromptManager` to use `importlib.resources` instead of direct file paths (Critical for WASM/Pyodide compatibility).
- [ ] **Global Import Fix**: Perform a massive find-and-replace to update all imports to the new `wibt_tool` namespace:
    - `from agents` $\rightarrow$ `from wibt_tool.agents`
    - `from models` $\rightarrow$ `from wibt_tool.models`
    - `from utils` $\rightarrow$ `from wibt_tool.utils`
    - `from config` $\rightarrow$ `from wibt_tool.config`
    - `from prompt_manager` $\rightarrow$ `from wibt_tool.prompt_manager`
    - `from agent_factory` $\rightarrow$ `from wibt_tool.agent_factory`
    - `from summary_orchestrator` $\rightarrow$ `from wibt_tool.pipelines.summary_pipeline`
    - `from translation_orchestrator` $\rightarrow$ `from wibt_tool.pipelines.translation_pipeline`
- [ ] **Resolve Missing Dependencies**: 
    - Identify and report all files importing `open_webui.py` (Current list: `apps/cli/alignment.py`, `apps/cli/extraction.py`, `apps/cli/create_summary.py`, `apps/cli/create_translation.py`, `apps/gui/components/endpoint.py`, `apps/gui/summary.py`, and `apps/gui/translation.py`).
    - Remove `open_webui.py` and refactor all its references in the files listed above.


## 🧹 Phase 2: Refactoring & Cleanup
*Goal: Remove legacy code and finalize the "Hybrid" architecture.*

- [x] **Remove Legacy Entry Points**: Removed `apps/cli/create_summary.py` and `apps/cli/create_translation.py`.
- [x] **Consolidate CLI**: Centralized main workflows in `apps/cli/` and moved tools to `apps/tools/`.
- [ ] **Finalize Package Structure**: Ensure `pyproject.toml` is correctly configured to build `wibt_tool` as a proper library.

## 🚀 Phase 3: Feature Implementation & Stability
*Goal: Restore broken features and prepare for WASM deployment.*

- [ ] **Rewrite GUI**: Fully rebuild the `apps/gui/` component to be compatible with the new architecture.
- [ ] **Update Legacy CLI Tools**:
    - [ ] Refactor/Rewrite `apps/cli/alignment.py`.
    - [ ] Refactor/Rewrite `apps/cli/extraction.py`.
- [ ] **WASM/Notebook Readiness**: 
    - [ ] Test the core `wibt_tool` package in a `marimo` notebook environment.
    - [ ] Ensure all file I/O is abstracted to support virtual filesystems.

## ⚠️ Known Technical Debt & Deprecations
*   **GUI**: Currently completely broken and requires a total rewrite.
*   **CLI Tools**: `apps/cli/alignment.py` and `apps/cli/extraction.py` are outdated and need implementation updates.
*   **Environment Dependencies**: The current reliance on `os.environ` and local file paths must be fully abstracted to support GitHub Pages/WASM.
