# Splunk Lantern Use Case Draft

# Zero Trust Pillar Data Flow Validation with Port and Protocol Service Management (PPSM) and OMB M-21-31

* **Applies To:** Splunk Enterprise, Splunk Cloud Platform, Splunk Enterprise Security (ES)
* **Target Audience:** Security Architects, SOC Engineers, ISSOs, Federal Compliance Leads
* **Article Type:** How-to / Prescriptive Use Case
* **Author:** John Young Suh (SuhLabs Systems Research / Splunk Trust Contributor)
* **Related Apps:** Splunk Common Information Model (CIM), Splunk App for Zero Trust Compliance (Splunkbase #9582), AWS-DFD-Visualizer (Splunkbase #8628), TA-suhlabs-eMASS (Splunkbase #8253)

---

## 1. Overview & Business Value

Federal agencies and defense programs operate under strict mandates to modernize their cybersecurity architectures. Two foundational directives govern network perimeter traffic and evidentiary monitoring:

1. **OMB Memorandum M-21-31:** Mandates four Event Logging (EL) maturity tiers (EL0 through EL3), requiring comprehensive logging of network flow metadata, inspection of traffic crossing perimeters, and long-term retention of audit telemetry.
2. **DoD Instruction 8551.01 (PPSM):** Requires that all inbound, outbound, and inter-enclave Ports, Protocols, and Services (PPS) traversing network boundaries be cataloged in the DISA Central Registry with assigned Vulnerability Assessment Categories (VAC).
3. **DoD Zero Trust Execution Roadmap:** Sets 152 activities across 7 pillars, specifically requiring continuous verification across the **Network & Environment** and **Visibility & Analytics** pillars.

Historically, organizations have tracked PPSM compliance on disconnected spreadsheets while logging network data into separate silos. When security audits or Authority to Operate (ATO) reviews occur, teams face a significant challenge: proving that observed production traffic actually matches authorized PPSM registrations.

This article shows how to use Splunk Enterprise and the Splunk Common Information Model (CIM) to automate data flow validation, cross-reference live network flows against approved PPSM registries, fulfill OMB M-21-31 EL2/EL3 requirements, and generate tamper-evident audit evidence for Authorizing Officials (AOs).

---

## 2. Prerequisites & Architecture Requirements

### Required Splunk Apps & Add-ons
* **Splunk Common Information Model (CIM):** Version 5.x or later (specifically the `Network_Traffic` and `Network_Sessions` data models).
* **Network Technology Add-ons (TAs):** The relevant Splunk Add-on for your perimeter devices and cloud networks (for example: Splunk Add-on for Palo Alto Networks, Splunk Add-on for Cisco ASA, Splunk Add-on for AWS, or Microsoft Azure Add-on).
* **Splunk App for Zero Trust Compliance (Splunkbase #9582):** Provides persistent KV Store collections for DoD COA activities and the cryptographic Proof of Delivery (PoD) vault.
* **AWS-DFD-Visualizer (Splunkbase #8628):** Renders cloud asset topology and data flows onto NIST SP 800-207 Three-Plane swimlanes.
* **TA-suhlabs-eMASS (Splunkbase #8253):** Provides automated export of non-compliant findings into eMASS POA&M milestone records.

### Data Model & Logging Tier Requirements (OMB M-21-31)
Ensure that boundary firewall logs, Cloud Access Point (CAP) telemetry, and VPC/VNet flow logs are actively ingested and mapped to CIM:
* `datamodel=Network_Traffic.All_Traffic`
* Required CIM fields: `src`, `dest`, `dest_port`, `transport`, `action`, `vendor_product`, `dvc`

---

## 3. Step-by-Step Implementation Guide

```
+----------------------------------------------------------------------------------------------------------+
|                              PPSM & OMB M-21-31 DATA FLOW VALIDATION LOOP                                |
|                                                                                                          |
|   1. INGEST & NORMALIZE (OMB M-21-31 EL1-EL2)                                                            |
|      Boundary Firewalls & Cloud Flow Logs --> Splunk CIM (Network_Traffic Data Model)                    |
|                                     |                                                                    |
|   2. CORRELATE AGAINST AUTHORIZED REGISTRIES (PPSM / CAL)                                                |
|      Live Network Flows <--> zt_ppsm_registry & zt_cal_boundary KV Store Lookups                         |
|                                     |                                                                    |
|   3. DETECT ANOMALIES & COMPUTE EVIDENCE HASH (DART Record Phase)                                        |
|      Identify unapproved ports/protocols --> Generate SHA-256 Dataset Digest                             |
|                                     |                                                                    |
|   4. TRIAGE & REMEDIATE (DART Triage Phase)                                                              |
|      Approved flows: Commit to PoD Vault (Splunkbase #9582)                                              |
|      Unapproved flows: Generate eMASS POA&M Milestones (Splunkbase #8253)                                |
+----------------------------------------------------------------------------------------------------------+
```

### Step 1: Configure the PPSM Registry KV Store Lookup

Create a persistent KV Store collection or lookup table (`zt_ppsm_registry.csv`) containing the authorized PPS baseline approved by your Authorizing Official (AO) and registered in the DISA PPSM Central Registry:

```csv
dest_port,transport,service_name,pps_category,disa_registry_id,approval_status,vac_category
443,tcp,https,Inbound_Internet,PPSM-REG-00104,Approved,CAT_II
22,tcp,ssh,Inter_Enclave,PPSM-REG-00215,Approved,CAT_I
53,udp,dns,Outbound_Internet,PPSM-REG-00088,Approved,CAT_II
123,udp,ntp,Outbound_Internet,PPSM-REG-00012,Approved,CAT_III
8443,tcp,alt_https,Intra_Enclave,PPSM-REG-00512,Approved,CAT_II
```

Upload this file to Splunk via **Settings > Lookups > Lookup table files** and configure a Lookup Definition named `zt_ppsm_registry`.

### Step 2: Verify OMB M-21-31 Logging Coverage & Normalization

Before auditing PPSM compliance, confirm that network perimeter logs are actively populating the accelerated `Network_Traffic` data model as required by OMB M-21-31 EL1/EL2 tiers. Run the following validation search:

```spl
| tstats count min(_time) AS earliest_log max(_time) AS latest_log
  from datamodel=Network_Traffic where nodename=All_Traffic
  by All_Traffic.vendor_product All_Traffic.transport All_Traffic.action
| eval earliest=strftime(earliest_log, "%Y-%m-%d %H:%M:%S"), latest=strftime(latest_log, "%Y-%m-%d %H:%M:%S")
| fields All_Traffic.vendor_product, All_Traffic.transport, All_Traffic.action, count, earliest, latest
```

Verify that all perimeter sensors (firewalls, cloud proxies, and VPC flow logs) show current timestamps and normalized actions (`allowed` or `blocked`).

### Step 3: Run the PPSM Cross-Boundary Data Flow Validation Search

Execute the core validation search. This search examines all permitted traffic (`action=allowed`) crossing boundary interfaces and joins each flow against the authorized `zt_ppsm_registry`:

```spl
| tstats summariesonly=t count
  from datamodel=Network_Traffic where nodename=All_Traffic All_Traffic.action="allowed"
  by All_Traffic.dest_port All_Traffic.transport All_Traffic.src All_Traffic.dest All_Traffic.dvc
| rename All_Traffic.* AS *
| lookup zt_ppsm_registry dest_port transport OUTPUT service_name, pps_category, disa_registry_id, approval_status, vac_category
| eval compliance_status=case(
    isnull(disa_registry_id), "NON_COMPLIANT_UNREGISTERED",
    approval_status!="Approved", "NON_COMPLIANT_UNAPPROVED",
    true(), "COMPLIANT_AUTHORIZED"
  )
| search compliance_status!="COMPLIANT_AUTHORIZED"
| stats sum(count) AS unauthorized_event_count,
        values(src) AS sample_sources,
        values(dest) AS sample_destinations
  by dest_port, transport, compliance_status, dvc
| sort - unauthorized_event_count
```

#### How this search works:
1. `tstats summariesonly=t` accelerates search performance by querying indexed data model summaries, returning results across millions of firewall events in seconds.
2. `lookup zt_ppsm_registry` cross-references each observed `dest_port` and `transport` protocol against your authorized baseline.
3. `eval compliance_status` flags any traffic lacking a DISA Registry ID or marked unapproved.
4. `search compliance_status!="COMPLIANT_AUTHORIZED"` isolates unapproved boundary flows for immediate triage.

### Step 4: Map Data Flows to NIST SP 800-207 Three-Plane Swimlanes

To visualize boundary flows within the wider Zero Trust architecture, open the **AWS-DFD-Visualizer** app (Splunkbase #8628):
1. Navigate to the **Data Flow Diagram (DFD)** view.
2. Select your perimeter firewall or Cloud Access Point (CAP) as the inspection target.
3. The visualizer maps observed connections across the **Identity**, **Policy Decision/Enforcement (PEP/PDP)**, and **Data/Infrastructure** planes.
4. Any active flow utilizing an unregistered PPSM port is flagged in the topology view as an unvalidated boundary traverse.

### Step 5: Commit Evidentiary Proof of Delivery (PoD)

When the validation search returns zero unapproved flows across a scheduled audit window (e.g., the last 30 days), compute and commit the evidentiary proof to the Proof of Delivery vault in the **Splunk App for Zero Trust Compliance** (#9582):

```spl
| tstats summariesonly=t count
  from datamodel=Network_Traffic where nodename=All_Traffic All_Traffic.action="allowed"
  by All_Traffic.dest_port All_Traffic.transport
| rename All_Traffic.* AS *
| lookup zt_ppsm_registry dest_port transport OUTPUT disa_registry_id, approval_status
| where isnull(disa_registry_id) OR approval_status!="Approved"
| stats count AS unapproved_flows
| eval audit_timestamp=now(),
        verified_by="ISSO_Automated_Audit",
        activity_id="ZTOM-NET-03"
| eval evidence_digest=sha256(activity_id . audit_timestamp . unapproved_flows)
| outputlookup append=t zt_evidence_pod
```

*(Note: Splunk provides evidentiary logging, monitoring, and audit verification; active packet filtering remains the operational role of network enforcement devices like firewalls and cloud security groups).*

### Step 6: Automate eMASS POA&M Generation for Exceptions

If unapproved PPSM flows or expired CAL connection links are detected during triage, pass the results directly to **TA-suhlabs-eMASS** (#8253) to format findings into standardized DoD eMASS POA&M milestone updates. This eliminates manual copy-pasting between Splunk and federal compliance portals.

---

## 4. Validation & Verification

To verify that this use case is operating correctly in your environment:
1. **Simulate a Test Flow:** In a staging network, generate a single authorized request (e.g., HTTPS on port 443) and a single unregistered request (e.g., an unapproved port like 8088).
2. **Execute the Validation Search:** Ensure that the unregistered port appears with `compliance_status="NON_COMPLIANT_UNREGISTERED"`, and the authorized port is excluded from the exception list.
3. **Inspect KV Store Audit Records:** Verify that passing audits append records to `zt_evidence_pod` containing the computed SHA-256 digest and execution timestamp.

---

## 5. Next Steps & Recommended Resources

* **Splunkbase Apps:**
  * [Splunk App for Zero Trust Compliance (Splunkbase #9582)](https://splunkbase.splunk.com/app/9582)
  * [AWS-DFD-Visualizer (Splunkbase #8628)](https://splunkbase.splunk.com/app/8628)
  * [TA-suhlabs-eMASS (Splunkbase #8253)](https://splunkbase.splunk.com/app/8253)
* **Standards & Guidance:**
  * **OMB M-21-31:** *Improving the Federal Government's Investigative and Remediation Capabilities Related to Cybersecurity Incidents*
  * **DoD Instruction 8551.01:** *Ports, Protocols, and Services Management (PPSM)*
  * **NIST SP 800-207:** *Zero Trust Architecture*
* **Reference Architecture & Engineering Whitepaper:**
  * [Zero Trust Architecture: Implementation Reality & Evidentiary Proof (SuhLabs)](https://suhlabs.com/zero-trust-whitepaper.html)
