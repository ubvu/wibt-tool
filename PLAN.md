# WIBT-Tool Roadmap: Path to WASM Deployment

This document outlines the strategic plan to transform `wibt-tool` from a collection of scripts into a robust, modular Python package optimized for browser-based (WASM/Pyodide) deployment.

## Core Architecture Principles
- **Hybrid Model**: `src/wibt_tool` (Core Logic) vs `apps/` (Client Applications).
- **Resource Decoupling**: No direct `open()` calls for internal assets; use `importlib.resources`.
- **Environment Agnosticism**: Core logic must not assume a local filesystem or specific environment variables.

---

## Phase 1: Core Library Hardening (In Progress)
*Goal: Ensure the core package is a single, portable unit.*

- [x] **Namespace Integrity**: Refactor all imports to use `wibt_tool.*`.
- [x] **Resource Management**: Implement `importlib.resources` for prompt management.
- [ ] **Configuration Abstraction**: Ensure `AppConfig` can be initialized from a dictionary (for WASM) rather than just environment variables.
- [ ] **Dependency Audit**: Minimize external dependencies in the core to reduce the WASM bundle size.

## Phase 2: Package & Build System (Immediate Priority)
*Goal: Standardize the package for distribution and installation.*

- [ ] **Finalize `pyproject.toml`**: Configure for `src`-layout build system (e.g., using `setuptools`, `hatch`, or `flit`).
- [ ] **Dependency Management**: Standardize `uv` or `poetry` usage for reproducible environments.
- [ ] **Build Verification**: Validate that `pip install .` results in a functional, correctly namespaced package.

## Phase 3: Interface Development (WASM/Notebook Focus)
*Goal: Create high-quality user interfaces that run in the browser.*

- [x] **Marimo Prototype**: Create `apps/gui/summarize_notebook.py` as a blueprint for WASM UI.
- [ ] **UI Refinement**: Improve the Marimo notebook with better error handling and progress indicators.
- [ ] **Client-Side I/O**: Implement logic in the UI to handle browser-native file uploads and downloads (avoiding `os.path` issues).

## Phase 4: WASM Readiness & Deployment
*Goal: Prove the concept in a browser environment.*

- [ ] **Pyodide/JupyterLite Testing**: Run the full summarization-to-translation pipeline in a simulated WASM environment.
- [ ] **Bundle Optimization**: Monitor and minimize the footprint of the `wibt_tool` package for faster browser loading.
- [ ] **Deployment Pipeline**: Set up GitHub Pages deployment for the Marimo/WASM notebook.

## Phase 5: Maintenance & Documentation
*Goal: Ensure long-term usability and project health.*

- [ ] **Technical Documentation**: Update `ARCHITECTURE.md` to reflect the modular design.
- [ ] **CI/CD**: Implement automated tests (pytest) that run in both local and WASM-compatible environments.
- [ ] **Usage Guides**: Create clear instructions for both developers (installing the package) and users (using the WASM notebook).
