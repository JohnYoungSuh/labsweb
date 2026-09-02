# Source-Review Methodology and Claim-Verification Register

**Target artifact:** `multi-agent-pipelines-whitepaper.html`  
**Repository:** `JohnYoungSuh/labsweb`  
**Review date:** 2026-09-01  
**Methodology:** Structured claim-to-source review framework, informed by scholarly reference-verification and evidence-extraction practices.  
**Status:** In progress; internal source-review methodology and claim register.

---

## 1. Overview and Review Scope

This internal register tracks the relationship between externally verifiable claims in `multi-agent-pipelines-whitepaper.html` and their underlying reference sources. It is maintained to preserve provenance, record study populations, and document scope qualifications as research and platform features evolve.

### Metric Model & Accounting Dimensions

| Metric Dimension | Count | Description |
| :--- | ---: | :--- |
| **Canonical Sources Catalogued** | 16 | Unique original papers, preprints, vendor docs, and practitioner reports in `source-register.csv` |
| **Material Claims Identified** | 14 | Unique externally checkable claims tracked in `claim-register.csv` |
| **Peer-Reviewed Research (E1)** | 1 | Published academic research with full methods (*Lost in the Middle*, TACL 2024) |
| **Preprints & Empirical Studies (E2)** | 7 | Emerging empirical studies and frameworks (*Control Illusion*, Rajan, OpenAI, STORM, SEMAP, Rodrigues, Acharya) |
| **First-Party Product Docs (E3)** | 4 | Documented platform capabilities (*Google Antigravity SDK*, *Docker Sandboxes*, *Cursor*, *OpenOrchestrator*) |
| **Practitioner Case Studies (E5)** | 4 | Qualitative operational observations (*Bhaumik*, *Böckeler*, *Autonoma*, *CodeCtx*) |
| **Claims with Scope Qualifications** | 8 | Claims narrowed to match tested populations, benchmark subsets, or experimental domains |
| **Documented Tool Capabilities** | 3 | Claims describing documented product features requiring deployment-level validation |
| **Practitioner Observations** | 3 | Qualitative operational experiences not asserted as universal empirical proof |

---

## 2. Review Workflow

The source-review framework uses a 5-stage tracking model:

$$\text{Inventory} \longrightarrow \text{Normalize} \longrightarrow \text{Verify} \longrightarrow \text{Adjudicate} \longrightarrow \text{Maintain}$$

1. **Stage 1 (Inventory):** Extract external citations, numerical figures, and technical capability statements.
2. **Stage 2 (Normalize):** Record canonical titles, DOIs/arXiv IDs, author lists, and source types in `source-register.csv`.
3. **Stage 3 (Verify):** Extract supporting text excerpts, page/section locations, and study constraints from original sources.
4. **Stage 4 (Adjudicate):** Narrow claim language to match verified study scopes, benchmark samples, and product contexts.
5. **Stage 5 (Maintain):** Monitor preprints and vendor documentation on regular review cadences.

---

## 3. Claim Adjudication and Provenance Log

| Claim ID | Source Key | Stated Topic / Metric | Supporting Excerpt & Location | Scope Qualification Applied |
| :--- | :--- | :--- | :--- | :--- |
| **CLM-001** | `SRC-001` (Liu et al., 2024) | Position-sensitive retrieval | TACL 2024 p. 158 §1: Performance decreases when relevant info is in context center. | Scoped to evaluated long-context QA/retrieval tasks; avoids universal failure claims. |
| **CLM-002** | `SRC-002` (Geng et al., 2025) | Instruction hierarchy prioritization | arXiv:2502.15851 §1 p. 2: System prompts fail to consistently constrain behavior under conflict framing across 6 models. | Scoped to evaluated models and conflict scenarios; classified as preprint. |
| **CLM-003** | `SRC-007` (Rodrigues, 2026) | Communication topology effects | arXiv:2606.21666 §4.2: Broadcast increased hallucination in travel planning, but did not replicate in software tasks. | Scoped explicitly to domain contrast (travel vs. software); framed as context-dependent variable. |
| **CLM-004** | `SRC-006` (Mao et al., 2025) | SEMAP protocol framework | arXiv:2510.12120: *Towards Engineering Multi-Agent LLMs: A Protocol-Driven Approach*. | Corrected canonical paper title; framed as structured protocol reducing SE task failures. |
| **CLM-005** | `SRC-008` (Acharya, 2026) | Semantic Intent Divergence (SID) | arXiv:2604.16339 §2: Drift between high-level spec and low-level code under unmanaged silos. | Corrected canonical title (*Semantic Consensus: Process-Aware Conflict Detection and Resolution...*); framed as emerging preprint framework. |
| **CLM-006** | `SRC-003` (Rajan, 2026) | SWE-bench Verified 28.5% broken patches | arXiv:2606.16062 §3 Table 1: 14 of 49 audited tasks accepted patches with incomplete assertions. | Recorded sample denominator ($n=14, N=49$) and evaluation harness weak-assertion criteria. |
| **CLM-007** | `SRC-004` (OpenAI, 2026) | SWE-bench Verified 59.4% difficult failures | OpenAI Benchmark Report: 82 of 138 difficult failure tasks suffered from flawed reference tests or ambiguity. | Recorded sample denominator ($N=138$) and failure classification criteria. |
| **CLM-008** | `SRC-016` (Autonoma, 2025) | Tautological test generation | getautonoma.com blog: Self-testing agents frequently author trivial passing assertions. | Classified as practitioner reporting observing weak or tautological test generation. |
| **CLM-009** | `SRC-015` (Böckeler, 2024) | Same-agent TDD loop limitations | martinfowler.com essay: Agents often skipped red state or tailored assertions to preexisting bugs. | Classified as a practitioner experiment reporting qualitative observations on agentic TDD loops. |
| **CLM-010** | `SRC-005` (Liu et al., 2026) | STORM state-aware mediation | arXiv:2605.20563: *Multi-agent Collaboration with State Management*. Shared-workspace write mediation outperforming uncoordinated worktrees on Commit0-Lite. | Scoped to state-aware write mediation detecting stale views; avoids universal merge claims. |
| **CLM-011** | `SRC-014` (Bhaumik, 2024) | Stale cache state contamination | AI Engineer Talk Transcript: 500ms cache lag led to downstream cascade errors in production. | Classified as practitioner case study observation on state desynchronization. |
| **CLM-012** | `SRC-011` (Docker Inc., 2026) | Docker Sandboxes microVM & proxy | Docker Docs §Sandboxes Defaults: MicroVM isolation with host credential proxy and egress controls. | Qualified as documented platform capability; deployment policy must be independently validated. |
| **CLM-013** | `SRC-010` (Google LLC, 2026) | Google Antigravity SDK policy model | Antigravity SDK Docs §Policies: Declarative tool permission policies and confirmation gates. | Formatted as documented SDK capability configured via application policy. |
| **CLM-014** | `SRC-013` (OpenOrchestrator, 2026) | OpenOrchestrator Conflict Guard | OpenOrchestrator Docs §Conflict Guard: Worktree lifecycle and pre-merge file-overlap detection. | Scoped to direct file-overlap detection; notes that semantic conflicts require schema gates. |

---

## 4. Maintenance and Recheck Guidelines

- **Preprints (E2):** Recheck semi-annually for updated versions, journal/conference acceptance, or author revisions.
- **Vendor Documentation (E3):** Recheck quarterly for product release updates, configuration schema changes, or security notices.
- **Practitioner Observations (E5):** Recheck annually or when structured empirical studies on the topic become available.

---
*Maintained under `source-audit/` in repository `JohnYoungSuh/labsweb`.*
