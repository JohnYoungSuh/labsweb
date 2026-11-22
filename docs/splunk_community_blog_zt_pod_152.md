# Splunk Community Blog Post Draft

**Title:** Operationalizing the 152 DoD Zero Trust Activities in Splunk: From Kanban Planning to Cryptographic Proof of Delivery (PoD)  
**Author:** John Young Suh (SuhLabs Systems Research)  
**Target Category:** Security & Compliance / Splunk Community Blog  
**Related Applications:** Splunk App for Zero Trust Compliance (Splunkbase #9582), AWS-DFD-Visualizer (#8628), TA-suhlabs-eMASS (#8253)  
**Status:** Submission Draft for Splunk Community Review  

---

### Introduction: The Spreadsheet Bottleneck in Zero Trust

Implementing Zero Trust (ZT) across defense programs frequently breaks down when teams treat the mandate as a vendor procurement exercise. In federal environments, programs are required to satisfy all **152 activities mandated by the DoD Zero Trust Execution Roadmap (Courses of Action 1–3)** across the 7 Zero Trust Pillars (User, Device, Applications & Workloads, Data, Network & Environment, Automation & Orchestration, Visibility & Analytics).

In practice, most security teams attempt to track these 152 activities using disconnected CSV spreadsheets or static Jira tickets. When audit time arrives, there is an acute gap between the commercial tools deployed (EDR, identity providers, firewalls) and the defensible evidence required by an Authorizing Official (AO) or ISSO.

To address this gap directly inside Splunk Enterprise, we built the open-source **Splunk App for Zero Trust Compliance (Splunkbase #9582)**. 

*A quick note on maturity:* We want to be completely transparent with the community: this application is in its **early stages**, and parts of it—especially the integrated Kanban planning board and the prototype AI review agent that inspects telemetry data to draft delivery records—are currently an experimental **Proof of Concept (PoC)**. We are sharing it openly to co-create with the defense and Splunk practitioner community.

---

### The Operational Delivery Loop: Moving Beyond Static Statuses

A task is not complete simply because an agent or vendor tool was purchased. A task is complete only when a program satisfies a **Zero Trust Operational Milestone (ZTOM)** backed by tamper-evident evidence.

The application introduces an Agile-inspired delivery loop inside Splunk Enterprise (running natively on Splunk 10.4+ and Python 3.13), replacing static spreadsheets with four persistent Splunk KV Store collections. 

Work progresses through role-governed stage gates:
1. **Backlog & To Do:** 152 pre-loaded DoD activities mapped to target maturity tiers.
2. **In Progress:** Technical SMEs attach telemetry digests to active sprint cards.
3. **Testing / In Review:** Gated queue where required preconditions must be met.
4. **Done / Accepted (ISSO Verified):** Formal sign-off when verified telemetry proves the milestone outcome.

---

### The Core Architecture: The Proof of Delivery (PoD) Drawer

The centerpiece of the application is the **Proof of Delivery (PoD)** slide-out drawer (`zt_pod_handler.py`). Instead of a simple checkbox, each activity card opens a structured 3-part record that documents the lifecycle of the requirement:

```
+---------------------------------------------------------------------------------------------------------+
|                                    PROOF OF DELIVERY (PoD) DRAWER                                       |
|                                                                                                         |
|  [ SECTION 2: THE COA BASELINE ]                                                                        |
|  • DoD Activity ID (e.g. ZTOM-NET-01) & Target Maturity Tier                                            |
|  • Pillar Scope & Predecessor Dependencies                                                              |
|                                                                                                         |
|  [ SECTION 3: WORK IN PROGRESS & OPERATIONAL GAPS ]                                                     |
|  • Current sprint engineering tasks & active telemetry sources                                          |
|  • Known coverage gaps (e.g. legacy subnets missing 802.1X, unmanaged endpoints)                       |
|                                                                                                         |
|  [ SECTION 4: RECORDED & TRIAGED EVIDENCE VAULT ]                                                       |
|  • Live Splunk CIM search string & SHA-256 query result hash                                             |
|  • Raw event volume, ACAS/VRAM scan digests, and ISSO attestation timestamp                             |
+---------------------------------------------------------------------------------------------------------+
```

#### Section 2: What is in the COA for the Activity
This section establishes the authoritative regulatory baseline directly from the DoD Zero Trust Execution Roadmap:
* **Activity Definition:** Exact statutory wording from COA 1, 2, or 3.
* **Target Tier:** Targeted maturity tier (Target vs. Advanced).
* **Architectural Pillar:** Mapping to the 7 Zero Trust pillars.
* **Predecessor Dependencies:** Graph predecessors that must be satisfied before this activity can close.

#### Section 3: What Work is Being Done and Identified Gaps
This section captures ground-truth engineering reality:
* **Active Controls:** Which identity providers, microsegmentation agents, or logging forwarders are actively sending events to Splunk.
* **Operational Gaps:** Explicit documentation of what is *not* covered (e.g., unmanaged OT devices, legacy subnets, or staging environments).
* **AI Assistance (PoC):** In our experimental pilot, an autonomous review agent scans raw index logs against the activity requirements to draft the initial gap summary for the human SME to review.

#### Section 4: What is Recorded and Triaged with Evidence
This is the immutable evidentiary record proving that the milestone outcome has been delivered:
* **Splunk CIM Query String:** The exact SPL query executed across the Common Information Model (e.g. `tag=authentication action=success`).
* **Cryptographic Evidence Digest:** A SHA-256 hash computed over the query results, binding the exact telemetry state to the record.
* **Audit Trail:** Attestation metadata recording the authenticated Splunk user and timestamp, committed to `index=_internal sourcetype=zerotrust_audit`.

---

### Critical Path Planning: DAG Kahn's Algorithm in Splunk Search

Tracking 152 activities without a schedule leads to unmanaged blockers. To solve this, the application includes a custom Splunk search command:

```spl
| getcriticalpath
```

Implemented in `bin/get_critical_path.py`, this command executes a server-side Directed Acyclic Graph (DAG) Critical Path Method (CPM) using Kahn's topological sort. It dynamically computes:
* Early start and early finish dates.
* Late start and late finish dates.
* Total float and schedule slack.
* Critical path chains that risk slipping program Authority to Operate (ATO) deadlines.

---

### Summary & Invitation for Community Feedback

Zero Trust compliance should not be an annual spreadsheet scramble. By tracking the 152 DoD COA activities directly in Splunk Enterprise and anchoring milestones to cryptographic Proof of Delivery records, security teams can bridge the gap between commercial tool telemetry and audit readiness.

We invite the Splunk community to test the pilot application, inspect the KV Store schemas, and share feedback on GitHub:

* **Download on Splunkbase:** [Splunk App for Zero Trust Compliance (Splunkbase #9582)](https://splunkbase.splunk.com/app/9582)
* **GitHub Repository:** [JohnYoungSuh/Zero_Trust_Compliance](https://github.com/JohnYoungSuh/Zero_Trust_Compliance)
* **Companion Topology App:** [AWS-DFD-Visualizer (Splunkbase #8628)](https://splunkbase.splunk.com/app/8628)

*Do you track DoD Zero Trust roadmaps or NIST SP 800-207 milestones in Splunk? Drop your feedback, telemetry recipes, and search queries in the comments below!*
