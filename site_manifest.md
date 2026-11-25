# SUHLABS KNOWLEDGE BASE (COMPACT OUTLINE)

## [ai-safety-whitepaper] SuhLabs | Agent Command Logging
- file: ai-safety-whitepaper.html
- url: https://suhlabs.com/ai-safety-whitepaper.html
- summary: Record the agent's prompt text and tool-call strings in Splunk. The checker on this page matches those strings against a keyword list. It does not measure drift, embeddings, or token probabilities.
- sections: Executive Summary | 1. Status codes hide the command | 2. What gets logged | 3. What a reviewer is looking for | 4. Keyword check

## [ARCH-2026-03] SuhLabs | Atomic Governance Transactions: Durable Preauthorization Logging and Resource Reservation for Autonomous Tool Execution
- file: atomic-governance-whitepaper.html
- url: https://suhlabs.com/atomic-governance-whitepaper.html
- summary: Abstract Autonomous tool execution increases the operational importance of coordinating authorization, resource accounting, and audit evidence. This paper proposes Atomic Governance Transactions (AGT), a fail-closed protocol that reserves policy-governed resources and durably records an authorization decision before releasing a single-use, request-bound execution capability. The intended safety pr...
- sections: Abstract | 1. Introduction, Scope & Series Boundaries | 2. Threat Model, System Entities & Trust Relocation | 2.1 System Entities | 2.2 Adversary Capabilities & Availability Trade-Off | 3. Proposed AGT Protocol, State Machine & Crash Recovery | 3.1 Request-Body Binding vs. RFC 9449 DPoP | 3.2 Linearization Point & Crash-Recovery Protocol

## [community] SuhLabs | Contribute & Peer Review
- file: community.html
- url: https://suhlabs.com/community.html
- summary: SuhLabs builds defensive Zero Trust compliance tooling and AI governance reference architectures in the open. We invite contributions, bug reports, and peer review from security practitioners, developers, and architects.
- sections: GitHub Repositories | Splunk Community Publications | Direct Research Inquiries

## [POLICY-2026-01] SuhLabs | The DART Policy Framework: Institutional AI Governance via Zero Trust & Deterministic Control Planes
- file: dart-policy-whitepaper.html
- url: https://suhlabs.com/dart-policy-whitepaper.html
- summary: // EXECUTIVE_SUMMARY & BASIC_RULES Just asking an AI to be good does not keep systems safe. When smart computer programs act on their own with open access, test their own work, or use tools without taking notes, companies face real danger, big fines, and broken systems. The DART Policy Framework fixes this with four plain rules that programs cannot bypass: Declare (lock in the job and boundaries b...
- sections: 1. Why Simple AI Prompts Fail | 2. The Four Mandatory Rules (DART) | Rule 1 (Declare): Lock the Plan Before You Start | Rule 2 (Authorize): An Outside Guard Grants Permission | Rule 3 (Record): Write Notes in Advance | Rule 4 (Triage): Test in a Locked Room | 3. Company Policy Template (For Board & Security Leads) | PLAIN POLICY RULES FOR AI AGENTS (POLICY-DART-01)
- citations: Zero Trust Architecture | Artificial Intelligence Risk Management Framework (AI RMF 1.0) | Information Technology: Artificial Intelligence: Management System (ISO/IEC 42001:2023) | OMB Memorandum M-24-10: Advancing Governance, Innovation, and Risk Management for Agency Use of Artificial Intelligence | JSON Canonicalization Scheme (JCS) | OAuth 2.0 Demonstrating Proof-of-Possession at the Application Layer (DPoP)

## [ARCH-2026-02] SuhLabs | Deterministic Control Planes for Autonomous Enterprise Systems: Mechanical Containment Across the L0–L5 Assurance Spectrum
- file: deterministic-control-planes-whitepaper.html
- url: https://suhlabs.com/deterministic-control-planes-whitepaper.html
- summary: Abstract Autonomous software systems executing enterprise resource planning (ERP), liquidity management, and procurement workflows optimize strictly across their permitted parameter spaces. When governed solely by probabilistic language models or prompt-level policies, goal-directed optimization may exploit cumulative edge cases, including leverage expansion and single-vendor dependency concentrat...
- sections: Abstract | I. Threat Model: Failure Modes of Probabilistic Governance | II. Tri-Plane System Architecture | 1. The Planning Plane | 2. The Control Plane | 3. The Execution Plane | III. Formal Invariant Specifications | 1. Capital Structure and Leverage Ceiling

## [POLICY-2026-01] SuhLabs | Research & Technical Whitepapers
- file: experiments.html
- url: https://suhlabs.com/experiments.html
- summary: We start with real tests to see where computer programs break or cheat. Next, we build tools that stop bad actions before they happen. Finally, we turn those tools into plain rules that companies and government agencies can actually follow.
- sections: The DART Policy Framework: How to Keep AI Safe with Fixed Rules and Zero Trust | Atomic Governance Transactions: Writing Notes Before Taking Action | Fixed Guardrails for Autonomous Business Systems | Building Reliable Multi-Agent Coding Teams | Zero Trust Compliance & Proof of Delivery | The Sovereign Shield? Strategic Defense Dependency & Financial Distress | Agent Command Logging | Digital Sensor Characterization

## [index] SuhLabs | Open-source tools for agent gates, Zero Trust evidence, Splunk compliance
- file: index.html
- url: https://suhlabs.com/index.html
- summary: Open-source work on agent pipeline failure, Zero Trust control evidence, and compliance automation. Issues welcome.
- sections: Agents Without Mechanical Gates | Zero Trust as Purchases, Not Control Proof | Manual Audit Overhead & POA&M Tracking

## [multi-agent-pipelines-whitepaper] SuhLabs | Engineering Robust Multi-Agent Coding Pipelines
- file: multi-agent-pipelines-whitepaper.html
- url: https://suhlabs.com/multi-agent-pipelines-whitepaper.html
- summary: Executive Abstract Autonomous software agents can produce changes that appear credible, pass incomplete test suites, and still violate intended behavior, security constraints, or integration assumptions. These risks compound when multiple agents plan, implement, test, and merge changes across shared or partially isolated state. Prompt instructions, personas, and dynamically retrieved rulebooks rem...
- sections: Executive Abstract | 1. Scope, Definitions, and Assurance Levels | 1.1 Definition of Mechanical Controls | 1.2 Operational Scope & Architectural Contribution | 1.3 Actor and Trust Zone Model | 1.4 Agentic Assurance Maturity Levels (Proposed Adoption Rubric) | 2. Why Prompt Guidance Is Not Enforcement | 2.1 Statistical and Contextual Limits of Prompts
- citations: The Protection of Information in Computer Systems | Zero Trust Architecture | OAuth 2.0 Token Exchange | JSON Canonicalization Scheme (JCS) | Lost in the Middle: How Language Models Use Long Contexts | Control Illusion: The Failure of Instruction Hierarchies in Large Language Models

## [projects] SuhLabs | Projects & Tooling
- file: projects.html
- url: https://suhlabs.com/projects.html
- summary: Open-source defensive security tools, compliance automation apps, and active engineering repositories by SuhLabs.
- sections: Zero Trust Compliance | AWS-DFD-Visualizer | TA-suhlabs-eMASS | Asset & Identity in Splunk ES | ai-agent-governance-framework | okta-recon-generator | purple-apt-cicd-recon | Cloud-AIDevSecOps-Templates

## [sensor-whitepaper] SuhLabs | Sensor Architecture Whitepaper
- file: sensor-whitepaper.html
- url: https://suhlabs.com/sensor-whitepaper.html
- summary: A rigorous look at quantum efficiency, photon transfer curves, and characterizing sensor performance in a home laboratory setting.
- sections: 1. The Architecture of Modern Capture | 2. The Photon Transfer Curve (PTC) | Reading the curve | 3. Experiment: Generating Your Own PTC | Equipment Required | Procedure | Python Analysis Snippet | 4. Interactive Simulations

## [signals] SuhLabs | Signal Intercepts
- file: signals.html
- url: https://suhlabs.com/signals.html
- summary: Optical signal intercepts and perception research. Physical-layer hardware investigation into sensor metadata isolation. Research preview: not for commercial sale.
- sections: Uniform Flat Field Calibration | Transmission Step Tablet Wedge | Spatial Frequency Edge Target

## [MEMO-2026-01] SuhLabs | The Sovereign Shield? Strategic Defense Dependency, Financial Distress, and Autonomous-Agent Incentives
- file: sovereign-shield-whitepaper.html
- url: https://suhlabs.com/sovereign-shield-whitepaper.html
- summary: Executive Preface: Why Systems Architects Examine Capital Structure Enterprise security and systems engineering often treat external corporate infrastructure as a static boundary while focusing exclusively on internal code execution. We design cryptographic boundaries, zero-trust network access, and multi-layered identity perimeters, yet frequently overlook a critical external dependency governing...
- sections: Executive Preface: Why Systems Architects Examine Capital Structure | Abstract | I. Historical Context: Concentration in Leveraged Liquidity | II. Leverage Mechanics, Dataset Separation, and Sensitivity Math | 2.1 Unified Brokerage Margin Indicators (September 2026) | 2.2 Illustrative Collateral Drawdown Sensitivity Model | III. Causal Decoupling: Five Outcomes of Financial Distress | IV. Illustrative Industry Cases & Analytical Boundaries

## [zero-trust-whitepaper] SuhLabs | Zero Trust Compliance & IMS Splunk App
- file: zero-trust-whitepaper.html
- url: https://suhlabs.com/zero-trust-whitepaper.html
- summary: // EXECUTIVE_SUMMARY Buying new security tools does not mean your network is safe. In defense projects, teams must finish all 152 tasks required by the DoD Zero Trust Roadmap and prove it on a real project schedule. Security scanners and log tools give you lots of data, but they do not assemble audit proof or track project tasks. The Splunk App for Zero Trust Compliance (Splunkbase #9582) runs rig...
- boundary: // CLAIMS_BOUNDARY: OBSERVATION VS. ENFORCEMENT AWS-DFD-Visualizer detects CSP asset environments (AWS, Azure, GCP) and marks topology paths that miss an expected control, such as unapproved direct SSH (port 22) ingress. A marked path is an operational finding to review. It does not prove that a pol...
- sections: 1. The Problem: Buying a Tool Does Not Finish the Job | 2. How the Tool Works: Planning Inside Splunk | 3. How Work Gets Done: The 5-Step Delivery Board | 4. Critical Path Engine & Integrated Master Schedule | 5. Proof of Delivery (PoD) Vault & REST Endpoints | 6. Architecture Topology: AWS-DFD-Visualizer (Splunkbase #8628) | POLICY COMPONENTS IDENTIFIED IN TOPOLOGY | 7. System Boundaries & Operational Reality
