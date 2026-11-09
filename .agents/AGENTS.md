# `vyapaar-examples` Agent Guidelines & Architecture Invariants

**Subsystem**: Examples (Numbered Learning Path)
**Language**: Python
**Primary Responsibility**: Canonical tutorials and runnable reference scripts for Indian equities, options, and factor models.

---

## 1. Role & Architectural Hints
* `vyapaar-examples` provides the official educational journey:
  - Step-by-step numbered scripts demonstrating data loading, indicator creation, order lifecycle, bracket orders, partial fills, and multi-symbol portfolios.
  - Every example script must remain runnable and covered by a corresponding test in `tests/unit/`.
* **Idea Inheritance**:
  - **Jesse**: Minimal boilerplate, clean logging, intuitive code paths for new quants.

---

## 2. Coding Guidelines (TDD)
* **Parallel Test Directory Rule (MANDATORY)**:
  - Every `examples/strategies/<num>_<name>.py` must have an automated regression test in `tests/unit/test_<num>_<name>.py` (or a `src/tests/` module directory).
  - **STRICTLY FORBIDDEN**: Inline `test_*` functions inside production source files.
* **Zero Floats Policy**: Exact decimal math in all examples.

---

## 3. Development & CI Workflow
* **Linting & Formatting**:
  ```bash
  ruff check .
  ruff format --check .
  ```
* **Testing**:
  ```bash
  pytest -q
  ```

---

## 4. Plan & Gap Discipline (binding)
* Binds to `.agents/rules/gap-tracking.md`:
  - If any hardcoded/stubbed/sample data is used when implementing a plan or gap, add a `docs/{plans,gaps}/XXXX-*.md` style document in the respective repo which is supposed to provide the functionality (gaps are individual features; plans are collections of gaps).
  - Cite dependencies in code and commits; when implemented, cleanup `docs/{plans,gaps}` of already implemented ones and update any index that references it.
