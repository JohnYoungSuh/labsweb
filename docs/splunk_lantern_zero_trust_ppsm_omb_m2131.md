# Splunk Lantern Use Case Draft

# Zero Trust Pillar Data Flow Validation with Port and Protocol Service Management (PPSM) and OMB M-21-31

* **Applies To:** Splunk Enterprise, Splunk Cloud Platform, Splunk Enterprise Security (ES)
* **Target Audience:** Security Architects, SOC Engineers, ISSOs, Federal Compliance Leads
* **Article Type:** How-to / Prescriptive Use Case
* **Author:** John Young Suh (SuhLabs Systems Research / Splunk Trust Contributor)
* **Related Apps:** Splunk Common Information Model (CIM), Splunk App for Zero Trust Compliance (Splunkbase #9582), AWS-DFD-Visualizer (Splunkbase #8628), TA-suhlabs-eMASS (Splunkbase #8253)

---

## 1. Overview & Business Value

Federal agencies and defense programs operate under strict mandates to modernize their cybersecurity architectures. Three foundational directives govern cloud network perimeter traffic, configuration baselines, and evidentiary monitoring:

1. **OMB Memorandum M-21-31:** Mandates four Event Logging (EL) maturity tiers (EL0 through EL3), requiring comprehensive logging of network flow metadata, inspection of traffic crossing perimeters, and long-term retention of audit telemetry.
2. **DoD Instruction 8551.01 (PPSM):** Requires that all inbound, outbound, and inter-enclave Ports, Protocols, and Services (PPS) traversing network boundaries be cataloged in the DISA Central Registry with assigned Vulnerability Assessment Categories (VAC).
3. **DoD Zero Trust Execution Roadmap (Pillars 3 & 5):** Sets 152 activities across 7 pillars, specifically requiring continuous verification across:
   * **Pillar 3 (Applications & Workloads):** Boundary security group rules, server group configurations, and authorized workload execution baselines.
   * **Pillar 5 (Network & Environment):** VPC configurations, Cloud Access Point (CAP) perimeters, Connection Approval List (CAL) peering links, and PPSM port governance.

Historically, organizations have tracked PPSM compliance on disconnected spreadsheets while logging network data into separate silos. When security audits or Authority to Operate (ATO) reviews occur, teams face a significant challenge: proving that observed production traffic actually matches authorized PPSM registrations without overwhelming search performance across billions of raw flow logs.

This article provides a prescriptive AWS deployment architecture that ingests VPC Flow Logs via AWS CloudWatch, crawls server group and VPC configurations via an AWS CLI bash script (`aws:config:json`), rolls high-velocity flows into a scheduled summary index (`summary_vpc_flow`), and automates cross-registry matching against CAL, CSAL, and PPSM baselines.

---

## 2. Prerequisites & Architecture Requirements

### Ingestion & Cloud Telemetry Sources (AWS Environment)
* **AWS CloudWatch Logs:** VPC Flow Logs configured across all monitored VPCs and subnets, streamed into Splunk via the Splunk Add-on for AWS or Kinesis Firehose.
* **AWS Configuration Baseline (`aws:config:json`):** An automated bash script running on an authorized server group queries the AWS CLI for Security Group configurations (`aws ec2 describe-security-groups`) and VPC topology (`aws ec2 describe-vpcs`), parses the output with `jq`, and indexes the structured records with `sourcetype=aws:config:json`. Because every organization has unique network topologies, this crawler adapts dynamically to customer-specific VPC structures.
* **Splunk Summary Indexing:** A user-designated summary index (e.g., `summary` or `summary_vpc_flow`) used to store pre-aggregated flow telemetry, satisfying OMB M-21-31 EL2/EL3 retention while delivering sub-second audit query speeds.

### Required Splunk Apps & Add-ons
* **Splunk Common Information Model (CIM):** Version 5.x or later (specifically the `Network_Traffic` data model).
* **Splunk Add-on for Amazon Web Services (AWS):** Used for CloudWatch VPC flow ingestion.
* **Splunk App for Zero Trust Compliance (Splunkbase #9582):** Provides persistent KV Store collections for DoD COA activities and the cryptographic Proof of Delivery (PoD) vault.
* **Splunk Lookup File Editor (Splunkbase #1724):** Recommended tool for easily importing, editing, and managing CAL, CSAL, and PPSM lookup tables directly within the Splunk Web UI.
* **AWS-DFD-Visualizer (Splunkbase #8628):** Renders cloud asset topology, security groups, and data flows onto NIST SP 800-207 Three-Plane swimlanes.
* **TA-suhlabs-eMASS (Splunkbase #8253):** Provides automated export of non-compliant findings into eMASS POA&M milestone records.

---

## 3. Step-by-Step Implementation Guide

> [!IMPORTANT]
> **Operational Security & CUI Notice: Conceptual SPL Reference Blueprints**  
> All SPL searches, field extractions, and data model examples presented in this guide are **conceptual reference blueprints**. In federal and defense enclaves, production queries contain sensitive network topology details (such as proprietary CIDR blocks, mission VPC IDs, private peering endpoints, and operational interface tags) that constitute Controlled Unclassified Information (CUI) and cannot be published in public documentation. Implementers must adapt these conceptual search patterns to match their enclave-specific data models, index naming conventions, and local classification boundaries.

```
+----------------------------------------------------------------------------------------------------------+
|                              AWS ZERO TRUST DATA FLOW VALIDATION LOOP                                    |
|                                                                                                          |
|   1. CONFIGURATION CRAWLER (Pillar 3: Applications & Workloads)                                          |
|      Server Group (AWS CLI + jq) --> Ingests VPC & Security Group Rules (sourcetype=aws:config:json)     |
|                                     |                                                                    |
|   2. HIGH-VELOCITY FLOW INGESTION (OMB M-21-31 EL1-EL2)                                                  |
|      AWS CloudWatch Logs --> Raw VPC Flow Logs Ingested into Splunk                                      |
|                                     |                                                                    |
|   3. SUMMARY INDEX ROLLUP (Pillar 5: Network & Environment)                                              |
|      Scheduled Saved Search "summary_vpc_flow" (with Summary Indexing enabled)                           |
|      Rolls up hourly flow counts by src, dest, dest_port, protocol into summary index of choice           |
|                                     |                                                                    |
|   4. CORRELATE AGAINST AUTHORIZED REGISTRIES (CAL, CSAL, PPSM)                                           |
|      Summary Index Flows <--> zt_ppsm_registry & zt_cal_boundary KV Lookups                              |
|                                     |                                                                    |
|   5. RECORD PROOF OF DELIVERY & TRIAGE (DART Loop)                                                       |
|      Compliant flows: Commit SHA-256 Digest to PoD Vault (Splunkbase #9582)                              |
|      Unapproved flows: Generate eMASS POA&M Milestones (Splunkbase #8253)                                |
+----------------------------------------------------------------------------------------------------------+
```

### Step 1: Ingest AWS Security Group and VPC Configuration (`aws:config:json`)

To satisfy Zero Trust Pillar 3 (Applications & Workloads), an authorized EC2 instance or container in your server group runs an automated bash collection script on a recurring cron schedule. The script queries the AWS CLI and formats the output with `jq`:

```bash
#!/usr/bin/env bash
# collect_aws_config.sh: Crawl security groups and VPC configurations for Splunk ingestion
set -euo pipefail

OUTPUT_DIR="/opt/splunk_telemetry/aws_config"
mkdir -p "${OUTPUT_DIR}"

# 1. Crawl Security Group Ingress/Egress Rules
aws ec2 describe-security-groups --output json | \
  jq -c '.SecurityGroups[] | {group_id: .GroupId, group_name: .GroupName, vpc_id: .VpcId, ip_permissions: .IpPermissions, ip_permissions_egress: .IpPermissionsEgress, collected_at: (now | todate)}' \
  > "${OUTPUT_DIR}/security_groups.json"

# 2. Crawl VPC Topologies and Peering Connections
aws ec2 describe-vpcs --output json | \
  jq -c '.Vpcs[] | {vpc_id: .VpcId, cidr_block: .CidrBlock, state: .State, is_default: .IsDefault, collected_at: (now | todate)}' \
  > "${OUTPUT_DIR}/vpcs.json"

# Forward to Splunk UF or ingest via Splunk HEC with sourcetype=aws:config:json
```

This crawler captures the ground-truth configuration of server groups and subnets, allowing Splunk to compare declared security group rules against actual traffic flows.

### Step 2: Configure the `summary_vpc_flow` Scheduled Search

VPC Flow Logs in large enterprise environments produce hundreds of millions of events daily. Querying raw logs across 30-day compliance windows creates extreme search overhead. 

To solve this, configure a scheduled saved search named **`summary_vpc_flow`**:
1. In the Splunk Web UI, navigate to **Settings > Searches, reports, and alerts > New Report**.
2. Name the search **`summary_vpc_flow`**.
3. In the search box, enter the rollup aggregation query:

```spl
`comment("Conceptual Reference SPL: Adapt index names and field tags to local enclave requirements to prevent CUI exposure")`
index=aws_vpc_flow sourcetype="aws:cloudwatch:vpcflow" action="ACCEPT"
| stats count AS flow_count, sum(bytes) AS total_bytes, sum(packets) AS total_packets
  by srcaddr, dstaddr, dstport, protocol, interface_id, vpc_id, action
```

4. Set the search schedule to run hourly (e.g., cron `0 * * * *`) over the previous 60 minutes (`earliest=-60m@m latest=@m`).
5. Under **Edit > Edit Actions**, check the box for **"Enable summary indexing"**.
6. Select the **Summary Index** of the implementer's choice (e.g. `summary` or `summary_vpc_flow`).

Checking this box automatically populates the summary index with lightweight, pre-calculated flow records, satisfying OMB M-21-31 EL2/EL3 retention requirements with minimal disk and compute footprint.

### Step 3: Configure the PPSM Registry KV Store Lookup

Create a persistent KV Store lookup (`zt_ppsm_registry.csv`) containing the authorized PPS baseline approved by your Authorizing Official (AO) and registered in the DISA PPSM Central Registry:

```csv
dest_port,transport,service_name,pps_category,disa_registry_id,approval_status,vac_category
443,tcp,https,Inbound_Internet,PPSM-REG-00104,Approved,CAT_II
22,tcp,ssh,Inter_Enclave,PPSM-REG-00215,Approved,CAT_I
53,udp,dns,Outbound_Internet,PPSM-REG-00088,Approved,CAT_II
123,udp,ntp,Outbound_Internet,PPSM-REG-00012,Approved,CAT_III
8443,tcp,alt_https,Intra_Enclave,PPSM-REG-00512,Approved,CAT_II
```

Upload this file to Splunk via **Settings > Lookups > Lookup table files** and configure a Lookup Definition named `zt_ppsm_registry`.

#### Practitioner Reality: Extracting CAL and CSAL Baselines from Excel via VBA

In operational federal environments, program offices rarely deliver CAL (Connection Approval List) and CSAL (Cybersecurity Software Authorization List) baselines as ready-to-ingest CSV files. Instead, they are typically delivered as complex, multi-tab Excel workbooks (`.xlsx` or `.xlsm`) containing merged header rows, formula formatting, and program-specific metadata.

To bridge this operational gap, security engineers write custom VBA (Visual Basic for Applications) extraction macros inside the master workbook. 

*(Important Implementation Note: The VBA script below is an illustrative reference pattern. Because every program office, command, and customer maintains its CAL and CSAL workbooks with unique sheet structures, tab names, and column orders, the implementer must write or adapt a macro tailored to their specific spreadsheet layout. The goal is simply to extract clean, unmerged rows that can be imported directly into Splunk using the **Splunk Lookup File Editor** app (Splunkbase #1724) or via **Settings > Lookups**).*

```vba
' Example VBA Macro: Export_CAL_CSAL_To_Splunk_CSV
' Illustrative pattern: Implementers should adapt column indexes and sheet names to match their workbook layout
Sub ExportCALToSplunkCSV()
    Dim ws As Worksheet
    Dim csvFile As String
    Dim rowNum As Long, lastRow As Long
    Dim lineStr As String
    Dim fileNum As Integer

    On Error GoTo ErrorHandler
    Set ws = ThisWorkbook.Sheets("CAL_Registry")
    lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    csvFile = ThisWorkbook.Path & Application.PathSeparator & "zt_cal_boundary.csv"
    fileNum = FreeFile

    Open csvFile For Output As #fileNum
    ' Write normalized Splunk header
    Print #fileNum, "vpc_id,peering_id,approved_cidr,atc_expiration,disa_cal_id,approval_status"

    For rowNum = 2 To lastRow
        If Trim(ws.Cells(rowNum, 1).Value) <> "" Then
            lineStr = ws.Cells(rowNum, 1).Value & "," & _
                      ws.Cells(rowNum, 2).Value & "," & _
                      ws.Cells(rowNum, 3).Value & "," & _
                      Format(ws.Cells(rowNum, 4).Value, "YYYY-MM-DD") & "," & _
                      ws.Cells(rowNum, 5).Value & "," & _
                      ws.Cells(rowNum, 6).Value
            Print #fileNum, lineStr
        End If
    Next rowNum

    Close #fileNum
    MsgBox "CAL lookup CSV exported successfully for Splunk: " & csvFile, vbInformation, "Splunk Lookup Export"
    Exit Sub

ErrorHandler:
    If fileNum > 0 Then Close #fileNum
    MsgBox "Error exporting CAL lookup: " & Err.Description, vbCritical, "Export Failure"
End Sub
```

Running an adapted macro produces clean lookup files ready to be imported directly via the **Splunk Lookup File Editor** into Splunk KV Store collections or standard CSV lookup definitions without manual copy-pasting.

### Step 4: Run the Accelerated Data Flow Validation Search on the Summary Index

Now, execute the compliance validation search against the **summary index** populated by `summary_vpc_flow`. This search maps numeric IANA protocol numbers (e.g. protocol 6 to `tcp`, protocol 17 to `udp`), joins each flow against the authorized `zt_ppsm_registry`, and flags any unapproved boundary traversals:

```spl
`comment("Conceptual Reference SPL: Adapt summary index name, field aliases, and registry lookups to local enclave topology")`
index=summary search_name="summary_vpc_flow"
| eval transport=case(protocol=6, "tcp", protocol=17, "udp", protocol=1, "icmp", true(), tostring(protocol)),
       dest_port=dstport,
       src=srcaddr,
       dest=dstaddr
| lookup zt_ppsm_registry dest_port transport OUTPUT service_name, pps_category, disa_registry_id, approval_status, vac_category
| eval compliance_status=case(
    isnull(disa_registry_id), "NON_COMPLIANT_UNREGISTERED",
    approval_status!="Approved", "NON_COMPLIANT_UNAPPROVED",
    true(), "COMPLIANT_AUTHORIZED"
  )
| search compliance_status!="COMPLIANT_AUTHORIZED"
| stats sum(flow_count) AS unauthorized_flows,
        sum(total_bytes) AS total_bytes_transferred,
        values(src) AS sample_sources,
        values(dest) AS sample_destinations
  by dest_port, transport, vpc_id, compliance_status
| sort - unauthorized_flows
```

#### Why this architecture is effective:
* **Speed & Scale:** Runs against lightweight summary index records rather than scanning raw CloudWatch streams, returning results in seconds.
* **Continuous Verification (cATO):** Evaluates live cloud boundaries against static DISA PPSM registrations continuously.
* **Pillar Alignment:** Answers DoD Zero Trust Pillar 3 (server group workload protection) and Pillar 5 (network perimeter boundaries).

### Step 5: Map Data Flows to NIST SP 800-207 Three-Plane Swimlanes

To visualize the validated flows within your cloud topology, open **AWS-DFD-Visualizer** (Splunkbase #8628):
1. In the **Data Flow Diagram (DFD)** view, select your monitored AWS VPC or Cloud Access Point (CAP) as the target.
2. The visualizer maps observed connections across the **Identity**, **Policy Decision/Enforcement (PEP/PDP)**, and **Data/Infrastructure** planes.
3. Topologies correlate the security group rules from `aws:config:json` against observed summary flows, visually highlighting unapproved port bindings or unmapped peering connections.

### Step 6: Commit Evidentiary Proof of Delivery (PoD)

When the validation search returns zero unapproved flows across the audit evaluation window, compute and commit the evidentiary proof to the Proof of Delivery vault in the **Splunk App for Zero Trust Compliance** (#9582):

```spl
`comment("Conceptual Reference SPL: Adapt activity_id and audit parameters to program compliance requirements")`
index=summary search_name="summary_vpc_flow"
| eval transport=case(protocol=6, "tcp", protocol=17, "udp", protocol=1, "icmp", true(), tostring(protocol)),
       dest_port=dstport
| lookup zt_ppsm_registry dest_port transport OUTPUT disa_registry_id, approval_status
| where isnull(disa_registry_id) OR approval_status!="Approved"
| stats count AS unapproved_flows
| eval audit_timestamp=now(),
        verified_by="ISSO_Automated_Audit",
        activity_id="ZTOM-NET-03"
| eval evidence_digest=sha256(activity_id . audit_timestamp . unapproved_flows)
| outputlookup append=t zt_evidence_pod
```

*(Note: Splunk provides evidentiary logging, monitoring, and audit verification; active packet filtering remains the operational role of network enforcement devices like AWS Network Firewalls and Security Groups).*

### Step 7: Automate eMASS POA&M Generation for Exceptions

If unapproved PPSM flows or expired CAL connection links are detected during triage, pass the results directly to **TA-suhlabs-eMASS** (#8253) to format findings into standardized DoD eMASS POA&M milestone updates. This eliminates manual copy-pasting between Splunk and federal compliance portals.

---

## 4. Validation & Verification

To verify that this use case is operating correctly in your environment:
1. **Verify Summary Population:** Search `index=summary search_name="summary_vpc_flow" | head 10` to confirm that flow counts, bytes, and port data are landing from CloudWatch.
2. **Verify Configuration Ingestion:** Search `sourcetype="aws:config:json" | head 5` to confirm security group rules and VPC IDs are actively updating.
3. **Simulate a Test Flow:** In a staging VPC, generate an unapproved port request (e.g. port 8088). Verify that the summary search flags it as `NON_COMPLIANT_UNREGISTERED`.
4. **Inspect KV Store Audit Records:** Verify that passing audits append records to `zt_evidence_pod` containing the computed SHA-256 digest and execution timestamp.

---

## 5. RMF & NIST SP 800-53 Rev. 5 Control Crosswalk (Zero CUI)

Federal agencies and defense programs executing the Risk Management Framework (RMF under NIST SP 800-37 Rev. 2) must demonstrate continuous control assessment (NIST SP 800-53A) without exposing Controlled Unclassified Information (CUI). 

The following public crosswalk maps the operational telemetry ingested in this guide directly to NIST SP 800-53 Rev. 5 security controls and public DoD policy directives:

| Operational Requirement | Primary NIST SP 800-53 Rev. 5 Controls | Public Policy Authority (Non-CUI) | Control Intent & Evidentiary Proof |
| :--- | :--- | :--- | :--- |
| **PPSM** *(Ports, Protocols & Services)* | **CM-7** *(Least Functionality)*<br>**CM-7(1)** *(Periodic Review)*<br>**SC-7** *(Boundary Protection)*<br>**SC-7(5)** *(Deny by Default)* | **DoD Instruction 8551.01** (*Ports, Protocols, and Services Management*) | Enforces that only registered, mission-essential ports and protocols traverse boundary firewalls. Accelerated summary searches prove zero unauthorized flows. |
| **CAL** *(Connection Approval List)* | **CA-3** *(Information Exchange)*<br>**CA-3(1)** *(Interconnection Agreements)*<br>**SC-7(3)** *(Access Points)*<br>**SC-7(4)** *(External Telecom)* | **DoD Instruction 8500.01** (*Cybersecurity*) & DISA Connection Process Guide (CPG) | Validates that Cloud Access Points (CAP) and VPC peering connections possess active Authority to Connect (ATC) dates prior to routing cross-boundary packets. |
| **CSAL** *(Software Authorization List)* | **CM-7(4)** *(Authorized Software / Allowlisting)*<br>**CM-10** *(Software Usage Restrictions)*<br>**SI-7(1)** *(Integrity Verification)* | **NIST SP 800-218** (*Secure Software Development Framework*) & OMB M-22-18 | Requires maintaining an approved software baseline. Prevents unauthorized binary execution by verifying process execution against cryptographic SHA-256 digests. |
| **OMB M-21-31** *(Event Logging)* | **AU-2** *(Event Logging)*<br>**AU-3** *(Content of Audit Records)*<br>**AU-6** *(Audit Review & Analysis)*<br>**AU-12** *(Data Retention)* | **OMB Memorandum M-21-31** (*Improving Federal Incident Capabilities*) | Establishes EL0 to EL3 logging maturity, requiring comprehensive network flow metadata ingestion, time-synchronized retention, and automated audit analysis. |

### RMF System Life Cycle Integration (NIST SP 800-37 Rev. 2)

```
+----------------------------------------------------------------------------------------------------------+
|                             RMF LIFECYCLE WITH DART & SPLUNK EVIDENCE                                    |
|                                                                                                          |
|  RMF STEP 2: SELECT (NIST SP 800-53 Rev. 5 Controls)                                                     |
|  - Select CA-3 (CAL), CM-7 / SC-7 (PPSM), CM-7(4) (CSAL), and AU-2/3/6 (OMB M-21-31).                   |
|                                     |                                                                    |
|  RMF STEP 3: IMPLEMENT (DART "Declare" & "Authorize" Phases)                                             |
|  - Ingest aws:config:json crawler (Pillar 3) and AWS CloudWatch VPC Flow Logs (Pillar 5).                |
|  - Schedule summary_vpc_flow rollup search into designated summary index.                                |
|  - Establish zt_ppsm_registry and zt_cal_boundary lookups (extracted from Excel via VBA).                |
|                                     |                                                                    |
|  RMF STEP 4: ASSESS (NIST SP 800-53A Rev. 5 / DART "Record" Phase)                                       |
|  - Execute accelerated summary query: cross-reference live flows against authorized lookups.             |
|  - Compute cryptographic SHA-256 evidence digest binding query results to zt_evidence_pod.              |
|                                     |                                                                    |
|  RMF STEP 5: AUTHORIZE (DART Stage-Gate Acceptance)                                                      |
|  - Authorizing Official (AO) reviews tamper-evident Proof of Delivery vault for ATO / ATC decision.      |
|                                     |                                                                    |
|  RMF STEP 6: MONITOR (Continuous Monitoring / cATO & DART "Triage" Phase)                                |
|  - Scheduled searches run continuously to detect unapproved ports, expired CAL links, or shadow software. |
|  - Automated POA&M milestone updates exported directly to DoD eMASS via TA-suhlabs-eMASS (#8253).        |
+----------------------------------------------------------------------------------------------------------+
```

---

## 6. Next Steps & Recommended Resources

* **Splunkbase Apps:**
  * [Splunk App for Zero Trust Compliance (Splunkbase #9582)](https://splunkbase.splunk.com/app/9582)
  * [Splunk Lookup File Editor (Splunkbase #1724)](https://splunkbase.splunk.com/app/1724)
  * [AWS-DFD-Visualizer (Splunkbase #8628)](https://splunkbase.splunk.com/app/8628)
  * [TA-suhlabs-eMASS (Splunkbase #8253)](https://splunkbase.splunk.com/app/8253)
* **Standards & Guidance (Public / Unclassified):**
  * **NIST SP 800-53 Rev. 5:** [Security and Privacy Controls for Information Systems and Organizations](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
  * **NIST SP 800-37 Rev. 2:** [Risk Management Framework for Information Systems and Organizations](https://csrc.nist.gov/publications/detail/sp/800-37/rev-2/final)
  * **NIST SP 800-207:** [Zero Trust Architecture](https://csrc.nist.gov/publications/detail/sp/800-207/final)
  * **NIST SP 800-218:** [Secure Software Development Framework (SSDF)](https://csrc.nist.gov/publications/detail/sp/800-218/final)
  * **OMB M-21-31:** *Improving the Federal Government's Investigative and Remediation Capabilities Related to Cybersecurity Incidents*
  * **DoD Instruction 8551.01:** *Ports, Protocols, and Services Management (PPSM)*
* **Reference Architecture & Engineering Whitepaper:**
  * [Zero Trust Architecture: Implementation Reality & Evidentiary Proof (SuhLabs)](https://suhlabs.com/zero-trust-whitepaper.html)
