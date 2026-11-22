# SuhLabs DART Empirical Benchmark Evaluation Report

**Generated:** 2026-11-22T16:58:03.473469+00:00  
**Benchmark Suite:** DART Verification Testbed v1.0.0  
**Overall Status:** **ALL EMPIRICAL HYPOTHESES VALIDATED**

---

## 1. Executive Summary

| Hypothesis | Test Description | Sample Size | Observed Result | Target | Validation Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **H1 (Declare)** | Schema validation immunity against adversarial prompt injection | 1,000 trials | **0.0% Bypass** (100% Rejected) | 0.0% Bypass | **VALIDATED** |
| **H3 (Record)** | Preauthorization write-ahead logging under chaos SIGKILL | 10,000 iterations | **\(\Delta_{\text{orphan}} = 0\)** | \(\Delta_{\text{orphan}} = 0\) | **VALIDATED** |
| **H4 (Triage)** | Read-only mechanical test mounts vs. prompt self-evaluation | 500 tasks | **100.0% Quarantine** | \(\ge 99.0\%\) | **VALIDATED** |

---

## 2. Hypothesis H3: Chaos Fault-Injection & Zero Orphan Dispatches

* **Test Methodology:** Injected randomized process kills and network stalls at the microsecond boundary between authorization, ledger commit, and execution dispatch.
* **Total Transactions:** 10,000
* **Unrecorded External Dispatches (\(\Delta_{\text{orphan}}\)):** **0**
* **Dangling Preauthorization Reservations:** 654
* **Crash Recovery Reconciled:** 654 (100.0%)
* **Statistical Bound:** Clopper-Pearson 95% Upper Bound for unrecorded dispatches = **0.0369%**.

---

## 3. Hypothesis H4: Anti-Reward-Hacking & Mechanical Triage

* **Test Methodology:** Evaluated agent code deliverables containing deleted assertions, modified mock returns, and out-of-scope dependencies.
* **Total Challenge Tasks:** 300
* **Prompt-Based Self-Evaluation Detection Rate:** **61.0%** (Missed 117 violations).
* **DART Mechanical Read-Only Triage Quarantine Rate:** **100.0%** (Missed 0 violations).
* **Comparative Advantage:** Mechanical triage outperforms prompt-based evaluation by **+39.0 percentage points**.

---

## 4. Hypothesis H1: Declarative Schema Locks

* **Test Methodology:** Evaluated JSON Schema Draft 2020-12 enforcement with `additionalProperties: false` against shell escapes, path traversals, and parameter tampering.
* **Trials:** 1,000
* **Adversarial Payloads Rejected:** 1,000
* **Bypasses:** **0**
* **Rejection Rate:** **100.0%**

---

*Reproduction Command:* `python3 -m benchmarks.run_all`
