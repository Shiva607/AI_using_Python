# 🚀 Legacy Code Modernizer

### Schema-Driven, AI-Assisted Legacy Code Modernization Platform (POC)

## 📌 **Overview**

The **Legacy Code Modernizer** is a Proof of Concept (POC) platform designed to **analyze legacy source code**, convert it into a **language-agnostic Intermediate Representation (IR)**, and then use that IR to generate:

- ✅ Modern, production-ready source code
- ✅ Enterprise-grade technical documentation

The system is built using **schema-first design**, **strict validation**, and **deterministic processing**, ensuring predictable and auditable modernization results.

---

## 🎯 Problem Statement

Legacy codebases written in **Python, Java, JavaScript, and C/C++** are difficult to:

- Maintain
- Document
- Migrate safely

Manual modernization efforts are:

- Time-consuming
- Error-prone
- Inconsistent across teams

As systems evolve, legacy code becomes a **business risk**, slowing innovation and increasing maintenance costs.

This project aims to **automatically analyze**, **document**, and **modernize** legacy code in a **repeatable, reliable, and transparent way**.

---

## 🧪 Proof of Concept (POC) Goals

The POC validates the following capabilities:

- Convert legacy code into a **structured Intermediate Representation (IR)**
- Generate **human-readable documentation** from IR
- Generate **modern, production-ready code**
- Ensure **deterministic behavior** (works even without LLMs)
- Improve quality when **LLMs (OpenRouter / Azure-like)** are available
- Preserve **folder structure and filenames**
- Provide **transparent outputs** (IR JSON, modern code, documentation)

---

## 🧠 Core Concept – Intermediate Representation (IR)

```
Legacy Code
     ↓
Intermediate Representation (IR)
     ↓
Modern Code + Documentation
```

The **Intermediate Representation (IR)** acts as the **single source of truth**.

- Documentation does **not** parse raw code
- Code generation does **not** parse raw code
- All downstream components consume **validated structured IR**

This eliminates duplication, reduces errors, and ensures consistency.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Streamlit UI (app.py)                           │
│  - Upload single file / multiple files / folders                        │
│  - Controls: Analyze & Modernize                                        │
│  - Views: IR JSON, Docs, Modern Code, Skeleton                          │
│  - Downloads: Code ZIP, Docs ZIP, Full Project ZIP                      │
├─────────────────────────────────────────────────────────────────────────┤
│                     Analysis Layer (DocumentationAgent)                 │
│        ┌──────────────────────────────┐                                 │
│        │ LLM-based IR Generation      │                                 │
│        │ - Strict JSON-only output    │                                 │
│        │ - Pydantic schema validation │                                 │
│        └──────────────────────────────┘                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                   Modernization Layer (ModernizationAgent)              │
│        ┌──────────────────────────────┐                                 │
│        │ LLM-based Code Modernization │                                 │
│        │ - Java 17+, Python 3.11+     │                                 │
│        │ - Enforced output JSON       │                                 │
│        └──────────────────────────────┘                                 │
├─────────────────────────────────────────────────────────────────────────┤
│              Documentation Layer (AdvancedDocumentationAgent)           │
│        ┌──────────────────────────────┐                                 │
│        │ Master + Modular Docs        │                                 │
│        │ - README                     │                                 │
│        │ - Architecture               │                                 │
│        │ - Migration Guide            │                                 │
│        │ - API Reference              │                                 │
│        │ - Testing Guide              │                                 │
│        └──────────────────────────────┘                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Design Choice – IR-First Architecture

- Analysis, modernization, and documentation are **decoupled**
- IR is **schema-validated using Pydantic**
- Prevents hallucinated structure
- Enables testing, auditing, and extensibility

---

## 📂 Intermediate Representation (IR)

### High-Level IR Schema

```
ProjectIR
├── language
├── original_filename
├── suggested_filename
├── summary
├── modules[]
│   └── ModuleIR
│       ├── name
│       ├── type (class / module / interface)
│       ├── description
│       ├── functions[]
│       ├── attributes[]
│       ├── imports[]
│       ├── design_patterns[]
├── technical_debt[]
│   └── category, severity, recommendation
├── dependencies[]
└── modernization_priority[]
```

---

### Function-Level IR Detail

```
FunctionIR
├── name
├── description
├── inputs (IOType)
├── outputs (IOType)
├── modifiers
├── decisions
├── side_effects
├── exceptions
├── dependencies
├── business_logic
```

This enables:

- Accurate documentation
- Safe modernization
- Structured technical debt tracking

---

## 🔄 End-to-End Flow (User Journey)

1. User uploads or pastes legacy code
2. Language detected (extension + heuristics)

### Stage 1 – Analysis

- Legacy code sent to LLM
- IR generated (JSON-only)
- Validated using Pydantic
- IR JSON shown to user

### Stage 2 – Modernization

- Legacy code modernized using strict rules
- Output returned as structured JSON

### Stage 3 – Documentation

- Professional documentation generated from IR

### Final Output

- Modernized source code
- Documentation bundle
- Full ZIP with preserved structure

---

## 🧩 Component Responsibilities

### 1️⃣ DocumentationAgent (Analysis Layer)

**Responsibility:**
Convert legacy code → structured IR

**Key Guarantees:**

- JSON-only output
- Exact schema compliance
- No hallucinated structure

**Validation:**

```python
ProjectIR.model_validate_json(...)
```

---

### 2️⃣ ModernizationAgent (Code Transformation)

**Responsibility:**
Convert legacy code → modern code

**Rules Enforced:**

- Java → Java 17+
- Python → Python 3.11+
- Type safety
- Modern APIs
- Robust error handling
- SOLID principles

**Strict Output Format:**

```json
{
  "modernized_code": "...",
  "filename": "...",
  "changes_summary": "..."
}
```

---

### 3️⃣ AdvancedDocumentationAgent

**Responsibility:**
Convert IR → enterprise-grade documentation

**Generated Files:**

- README.md
- MASTER_DOCUMENTATION.md
- ARCHITECTURE.md
- MIGRATION_GUIDE.md
- TECHNICAL_DEBT.md
- API_REFERENCE.md
- TESTING_GUIDE.md

---

## 🧱 Design Principles Applied

- Separation of Concerns
- Schema-First Design
- Deterministic by Default
- LLM as an Engine, Not Authority
- Full User Transparency

---

## ⚠️ Limitations (POC Scope)

- No AST-level parsing
- Decision accuracy depends on LLM
- No automatic unit test generation
- Optimization out of scope

---

## 🛠️ Mitigation & Improvements

- AST integration (`ast`, JavaParser)
- Decision & exception modeling
- Unit test generation from IR
- Static analysis integration

---

## 🗺️ Roadmap

### Phase 1 – IR Quality

- Hybrid LLM + AST
- Richer IR modeling

### Phase 2 – Target Generators

- Spring Boot
- FastAPI
- ASP.NET Core

### Phase 3 – Testing

- Auto unit tests
- Mutation testing
- Coverage checks

### Phase 4 – Observability

- IR versioning
- Diff views
- Migration audit logs

---

## 🧪 Tech Stack

- Python 3.11+
- Streamlit
- Pydantic
- Optional LLMs (OpenRouter / Azure-like)
- JSON schema enforcement

---

## 🧠 One-Line Pitch

> **“We convert legacy code into a language-agnostic Intermediate Representation (IR), then use that IR to generate modern code and enterprise-grade documentation in a deterministic, extensible pipeline.”**

---
