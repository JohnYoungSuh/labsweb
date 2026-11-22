# Splunk Idea Submission: Native Zero Trust Proof of Delivery (PoD) Engine

**Idea Title:** Native Zero Trust Proof of Delivery (PoD) Engine: Operationalizing the 152 DoD COA Activities, DART Telemetry Loop, and Automated CAL/CSAL/PPSM Compliance in Splunk Enterprise  
**Category:** Security, Compliance & Public Sector  
**Target Platform:** Splunk Enterprise (Core Search & CIM), Splunk Enterprise Security (ES), Splunkbase Ecosystem  
**Author / Proposer:** John Young Suh (SuhLabs Systems Research / Splunk Trust Contributor)  
**Related Splunk Apps:** Splunk App for Zero Trust Compliance (Splunkbase #9582), AWS-DFD-Visualizer (Splunkbase #8628), TA-suhlabs-eMASS (Splunkbase #8253)  

---

### Executive Summary & Problem Statement

Across federal, defense (DoD), and regulated enterprise environments, organizations face a critical operational dilemma: they must implement and satisfy all **152 activities defined in the DoD Zero Trust Execution Roadmap (Courses of Action 1 to 3)** across the 7 Zero Trust pillars (User, Device, Applications & Workloads, Data, Network & Environment, Automation & Orchestration, Visibility & Analytics).

Concurrently, defense programs are bound by statutory perimeter and software governance mandates:
1. **PPSM (DoDI 8551.01):** Ports, Protocols, and Services Management requires all network traffic traversing enclave, DISN, and cloud boundaries to be registered in the DISA Central Registry with approved Vulnerability Assessment Categories (VAC).
2. **CAL (Connection Approval List / Cloud Access Layer):** Enclaves and Cloud Access Points (CAP) must maintain active Authority to Connect (ATC) packages before cross-boundary data routing is authorized.
3. **CSAL (Cybersecurity Software Authorization List):** Systems may only execute software binaries verified and approved by the Authorizing Official (AO) / ISSM with cryptographic SHA-256 digests.

Today, programs attempt to track these complex requirements using disconnected CSV spreadsheets, static Jira tickets, or third-party GRC systems divorced from real-time operational telemetry. When audits or ATO renewals occur, an acute evidence gap emerges between deployed vendor controls and the defensible artifacts required by Authorizing Officials (AOs) and ISSOs.

---

### Proposed Solution: The DART Zero Trust Proof of Delivery (PoD) Engine

We propose establishing a native, telemetry-grounded Zero Trust delivery and verification framework inside Splunk Enterprise. Rather than treating compliance as a static checkbox, Splunk can operationalize the **DART** framework (Declare, Authorize, Record, Triage) directly across Splunk Common Information Model (CIM) data models and persistent KV Store collections.

```
+----------------------------------------------------------------------------------------------------------+
|                             THE DART ZERO TRUST PROOF OF DELIVERY PIPELINE                                |
|                                                                                                          |
|   1. DECLARE (Baseline Specification)                                                                    |
|      - Program declares 152 DoD COA activities, approved PPSM ports, CAL links, and CSAL software SHA-256 |
|      - Stored in KV Store: zt_compliance_items, zt_ppsm_registry, zt_csal_manifest                       |
|                                     |                                                                    |
|   2. AUTHORIZE (Deterministic Stage-Gates)                                                               |
|      - Agile Kanban transitions gated by role checks (SME, Scrum Master, ISSM/ISSO)                      |
|      - REST handlers require valid evidence digests before cards advance to Done / Accepted              |
|                                     |                                                                    |
|   3. RECORD (Cryptographic Telemetry Ingestion)                                                          |
|      - Splunk CIM models ingest telemetry: Network_Traffic (PPSM/CAL), Endpoint (CSAL), Authentication   |
|      - Splunk search calculates SHA-256 digest of matching query results and commits to zt_evidence_pod  |
|                                     |                                                                    |
|   4. TRIAGE (Continuous Drift Detection & eMASS POA&M Sync)                                              |
|      - SPL scheduled searches detect unregistered ports, expired CAL ATCs, or unapproved software hashes |
|      - Automatic export of compliance findings to TA-suhlabs-eMASS (#8253) and | getcriticalpath schedule |
+----------------------------------------------------------------------------------------------------------+
```

---

### Key Architectural Components

#### 1. The 3-Part Proof of Delivery (PoD) Drawer
Each activity card in the Splunk planning canvas exposes an interactive slide-out Proof of Delivery drawer (`zt_pod_handler.py`) divided into three structured sections:
* **Section 2 (The COA Baseline):** The authoritative regulatory mandate directly from the DoD Zero Trust Execution Roadmap (Activity ID, pillar, target maturity tier, and predecessor milestones).
* **Section 3 (Work in Progress & Operational Gaps):** Ground-truth engineering reality: active security tools feeding Splunk, unmonitored subnets, and an experimental AI review agent (PoC) that parses raw index logs to draft gap analyses.
* **Section 4 (Recorded & Triaged Evidence Vault):** The cryptographic evidence package: live Splunk CIM query strings, execution timestamps, SHA-256 result hashes, and authenticated session signatures committed to internal audit logs.

#### 2. Deep Integration with PPSM, CAL, and CSAL
* **PPSM under DoDI 8551.01:**
  - Network firewall and cloud flow logs (Palo Alto, Cisco, AWS VPC Flow) are normalized into the Splunk CIM `Network_Traffic` data model.
  - Telemetry is joined against the `zt_ppsm_registry` KV Store collection containing approved port, protocol, service, and DISA Tracking IDs.
  - Any observed traffic lacking an approved PPSM registration triggers an immediate compliance exception.
* **CAL (Connection Approval List & Cloud Access Points):**
  - Gateway routing and border session logs are evaluated against declared ATC expiration dates and approved peering endpoints.
  - Expired connection approvals or unauthorized boundary traversal paths are flagged before an audit finding occurs.
* **CSAL (Cybersecurity Software Authorization List):**
  - Endpoint telemetry (Sysmon, CrowdStrike Falcon, Carbon Black, Linux auditd) is ingested into the Splunk CIM `Endpoint.Processes` data model.
  - Binary hashes (`process_hash`, `sha256`) are checked against the `zt_csal_manifest` lookup.
  - Execution of binaries absent from the CSAL triggers a high-severity triage event.

#### 3. Automated eMASS POA&M Integration (`TA-suhlabs-eMASS #8253`)
When triage searches identify unapproved PPSM traffic, un-registered CAL boundary traversals, or un-remediated gaps across the 152 activities, the engine formats findings directly into eMASS-compliant POA&M milestone records. This eliminates duplicate manual data entry between Splunk and DoD eMASS instances.

#### 4. Schedule Dependency Analytics via `| getcriticalpath`
Zero Trust compliance involves complex inter-activity dependencies. The native search command `| getcriticalpath` implements Kahn's DAG topological sort directly in Splunk search:
* Calculates Early Start, Late Start, and Total Float for all 152 activities.
* Accounts for federal holidays, weekends, and team PTO.
* Highlights critical-path milestone chains that risk slipping program Authority to Operate (ATO) deadlines.

---

### Customer & Community Impact

1. **Eliminates Compliance Spreadsheets:** Defense programs, system integrators, and commercial enterprises can manage Zero Trust and federal compliance entirely within Splunk Enterprise.
2. **Defensible Evidence for Authorizing Officials:** Provides ISSOs and AOs with tamper-evident, cryptographically bound telemetry proofs rather than unverifiable self-attestation questionnaires.
3. **Continuous Authorization (cATO):** Transitions programs from snapshot, annual compliance reviews to real-time continuous monitoring of PPSM, CAL, CSAL, and Zero Trust outcomes.
4. **Open-Source and Splunk Native:** Implemented using standard Splunk primitives (KV Store, CIM, Python 3.13 REST endpoints, and custom search commands), avoiding proprietary vendor lock-in.

---

### Supporting References & Live Open-Source Projects
* **Splunkbase App #9582:** [Splunk App for Zero Trust Compliance](https://splunkbase.splunk.com/app/9582)
* **Splunkbase App #8628:** [AWS-DFD-Visualizer](https://splunkbase.splunk.com/app/8628)
* **Splunkbase App #8253:** [TA-suhlabs-eMASS](https://splunkbase.splunk.com/app/8253)
* **GitHub Repository:** [JohnYoungSuh/Zero_Trust_Compliance](https://github.com/JohnYoungSuh/Zero_Trust_Compliance)
* **Technical Whitepaper:** [Zero Trust Architecture: Implementation Reality & Evidentiary Proof (SuhLabs)](https://suhlabs.com/zero-trust-whitepaper.html)
