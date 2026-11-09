# fedramp-20x-ksi

FedRAMP 20x Key Security Indicators (KSIs) as code, with automated evidence.

Companion to [The Grid](https://github.com/camiati/The-Grid), a reference guide to the frameworks, and [aws-federal-baseline](https://github.com/camiati/aws-federal-baseline), a Terraform baseline mapped to NIST SP 800-53. Everything here is a theoretical reference: there is no real system, tenant, or account behind it.

## What's here

<details>
<summary>18 files and folders, each with a plain-language summary</summary>

| File | Defines |
|---|---|
| [`src/fedramp_ksi/catalog.py`](./src/fedramp_ksi/catalog.py) | <ul><li>Reads FedRAMP's official list of security indicators and rules.</li><li>Loads the KSI catalog and FedRAMP's rule IDs, checks them against their pinned SHA-256 and FedRAMP's JSON schema</li></ul> |
| [`src/fedramp_ksi/upstream.py`](./src/fedramp_ksi/upstream.py) | <ul><li>Checks whether FedRAMP has changed its rules since we copied them.</li><li>Compares the pinned files with the latest FedRAMP/rules commit and writes an issue body when they differ</li></ul> |
| [`src/fedramp_ksi/measures.py`](./src/fedramp_ksi/measures.py) | <ul><li>Reads our checks and counts how many each indicator has.</li><li>Loads measures, checks them against the catalog, reports readiness for Classes B, C, and D, and lists each measure's design decisions</li></ul> |
| [`src/fedramp_ksi/readme.py`](./src/fedramp_ksi/readme.py) | <ul><li>Writes the tables in this README, so they always match the data.</li><li>Generates this README's readiness and certification class sections from the catalog and measures</li></ul> |
| [`src/fedramp_ksi/training.py`](./src/fedramp_ksi/training.py) | <ul><li>Asks a training system who is behind on security training.</li><li>Placeholder client for a training platform's reporting API, and the check for who is overdue on training (KSI&#8209;CED&#8209;RAT)</li></ul> |
| [`measures/`](./measures/) | <ul><li>Our checks, one file per topic.</li><li>Measures for each KSI theme, one TOML file per theme, with a field reference</li></ul> |
| [`tests/test_catalog.py`](./tests/test_catalog.py) | <ul><li>Makes sure FedRAMP's list doesn't change without us noticing.</li><li>Pins the catalog: themes, indicator IDs, class-specific statements, rule IDs, and fields read</li></ul> |
| [`tests/test_upstream.py`](./tests/test_upstream.py) | <ul><li>Tests the rule-change check without going online.</li><li>Tests the upstream comparison with faked downloads, offline</li></ul> |
| [`tests/test_measures.py`](./tests/test_measures.py) | <ul><li>Makes sure every check is filled in correctly.</li><li>Checks measures against the catalog and the Class C target, and tests every validation rule</li></ul> |
| [`tests/test_readme.py`](./tests/test_readme.py) | <ul><li>Makes sure this README matches the data.</li><li>Fails when this README's generated sections are stale, or when it cites a FedRAMP ID that isn't in the pinned rules</li></ul> |
| [`tests/test_training.py`](./tests/test_training.py) | <ul><li>Tests the training check against a pretend server.</li><li>Tests the training client with faked responses and a mock server on 127.0.0.1, and the overdue check</li></ul> |
| [`.github/workflows/checks.yml`](./.github/workflows/checks.yml) | <ul><li>Runs every test whenever someone proposes a change.</li><li>Lint, format, and tests on every pull request</li></ul> |
| [`.github/workflows/upstream-check.yml`](./.github/workflows/upstream-check.yml) | <ul><li>Every Monday, looks for new FedRAMP rules.</li><li>Weekly upstream check that opens an issue when pinned files change</li></ul> |
| [`data/fedramp-consolidated-rules.json`](./data/fedramp-consolidated-rules.json) | <ul><li>FedRAMP's rulebook, copied exactly.</li><li>FedRAMP's machine-readable rules, copied unchanged from [FedRAMP/rules](https://github.com/FedRAMP/rules)</li></ul> |
| [`data/fedramp-consolidated-rules.schema.json`](./data/fedramp-consolidated-rules.schema.json) | <ul><li>FedRAMP's description of what the rulebook must look like.</li><li>FedRAMP's JSON schema for the rules, copied unchanged</li></ul> |
| [`data/upstream.json`](./data/upstream.json) | <ul><li>Records exactly which version of the rulebook we copied.</li><li>The upstream commit and the SHA-256 of each copied file</li></ul> |
| [`CLAUDE.md`](./CLAUDE.md) | <ul><li>Instructions for the AI assistant that helps build this repo.</li><li>Instructions for Claude Code: conventions, workflow, and hard rules</li></ul> |
| [`.claude/settings.json`](./.claude/settings.json) | <ul><li>What the AI assistant is and isn't allowed to do.</li><li>Enforced permission rules for Claude Code</li></ul> |

</details>

## Path to certification

FedRAMP 20x certifies a service at one of four classes, from minimal assurance at Class A to significant assurance at Class D. This repo's theoretical service targets Class C. The KSI tables below are generated from the pinned rules and the measures by `uv run python -m fedramp_ksi.readme`, and tests fail when they're out of date.

### Before Class A: Initial Implementation Phase

The closest thing to the old FedRAMP Ready designation, though it's a Marketplace listing rather than a readiness assessment. Every provider needs an Initial Implementation Phase listing before it can apply for any class (FRC&#8209;APP&#8209;MLF). To get and keep one, a provider:

1. Publishes information about the service in human-readable and JSON formats (MKT&#8209;CSO&#8209;MLR, CDS&#8209;CSO&#8209;PUB).
2. Requests the listing through FedRAMP's Marketplace listing request form (MKT&#8209;CSO&#8209;PML).
3. Shows the service is meant for direct or indirect use by agencies (MKT&#8209;IIP&#8209;AGU).
4. Documents progress toward certification against its own goals and milestones, updated at least quarterly (MKT&#8209;IIP&#8209;DCP).
5. Schedules a Class B, C, or D assessment within 2 years of the initial listing (MKT&#8209;IIP&#8209;DLA).

A listing needs a real provider, so this repo doesn't model these steps.

### Class A

Minimal assurance. A provider needs a SOC 2 Type II, FedRAMP Rev5 (including FedRAMP Ready), or GovRAMP certification from the past 12 months (FRC&#8209;CLA&#8209;ASF), plus its assessment materials (FRC&#8209;CLA&#8209;EAM). It must also address the process rules and the 7 KSIs listed in FRC&#8209;CLA&#8209;MFR. Automated measures are optional (FRC&#8209;CSX&#8209;VVK).

<!-- BEGIN GENERATED: class-a -->
**All 7 KSIs Class A requires** have at least one measure in [`measures/`](./measures/), so this repo covers each of them.

<details>
<summary>The 7 KSIs Class A requires</summary>

| KSI ID | Theme | Indicator | Measures | Automated |
|---|---|---|---|---|
| KSI&#8209;CMT&#8209;LMC | Change Management (CMT) | Logging Changes (LMC) | 3 | 3 |
| KSI&#8209;CNA&#8209;RNT | Cloud Native Architecture (CNA) | Restricting Network Traffic (RNT) | 4 | 3 |
| KSI&#8209;CED&#8209;RAT | Cybersecurity Education (CED) | Reviewing All Training (RAT) | 5 | 4 |
| KSI&#8209;IAM&#8209;AAM | Identity and Access Management (IAM) | Automating Account Management (AAM) | 3 | 3 |
| KSI&#8209;IAM&#8209;APM | Identity and Access Management (IAM) | Adopting Passwordless Methods (APM) | 3 | 3 |
| KSI&#8209;INR&#8209;RIR | Incident Response (INR) | Reviewing Incident Response Procedures (RIR) | 4 | 3 |
| KSI&#8209;SVC&#8209;SIN | Service Configuration (SVC) | Securing Information (SIN) | 3 | 3 |

</details>
<!-- END GENERATED: class-a -->

### Class B

Every KSI applies to everything in the assessment scope (FRC&#8209;CSX&#8209;MAS), with at least 1 automated measure each, a SHOULD at this class (FRC&#8209;CSX&#8209;VVK). A fresh independent assessment by a FedRAMP Recognized assessor is required (FRC&#8209;APP&#8209;FIA).

<!-- BEGIN GENERATED: class-b -->
**35 of 46 KSIs ready**, with at least 1 automated measure each.

<details>
<summary>All 46 KSIs at Class B</summary>

| KSI ID | Theme | Indicator | Automated measures | Ready |
|---|---|---|---|---|
| KSI&#8209;CED&#8209;RAT | Cybersecurity Education (CED) | Reviewing All Training (RAT) | 4 | Yes |
| KSI&#8209;CMT&#8209;LMC | Change Management (CMT) | Logging Changes (LMC) | 3 | Yes |
| KSI&#8209;CMT&#8209;RMV | Change Management (CMT) | Redeploying vs Modifying (RMV) | 2 | Yes |
| KSI&#8209;CMT&#8209;RVP | Change Management (CMT) | Reviewing Change Procedures (RVP) | 2 | Yes |
| KSI&#8209;CMT&#8209;VTD | Change Management (CMT) | Validating Throughout Deployment (VTD) | 2 | Yes |
| KSI&#8209;CNA&#8209;DFP | Cloud Native Architecture (CNA) | Defining Functionality and Privileges (DFP) | 3 | Yes |
| KSI&#8209;CNA&#8209;EIS | Cloud Native Architecture (CNA) | Enforcing Intended State (EIS), optional at Class B | 3 | Yes |
| KSI&#8209;CNA&#8209;IBP | Cloud Native Architecture (CNA) | Implementing Best Practices (IBP) | 3 | Yes |
| KSI&#8209;CNA&#8209;MAT | Cloud Native Architecture (CNA) | Minimizing Attack Surface (MAT) | 3 | Yes |
| KSI&#8209;CNA&#8209;OFA | Cloud Native Architecture (CNA) | Optimizing for Availability (OFA) | 2 | Yes |
| KSI&#8209;CNA&#8209;RNT | Cloud Native Architecture (CNA) | Restricting Network Traffic (RNT) | 3 | Yes |
| KSI&#8209;CNA&#8209;RVP | Cloud Native Architecture (CNA) | Reviewing Protections (RVP) | 2 | Yes |
| KSI&#8209;CNA&#8209;ULN | Cloud Native Architecture (CNA) | Using Logical Networking (ULN) | 3 | Yes |
| KSI&#8209;IAM&#8209;AAM | Identity and Access Management (IAM) | Automating Account Management (AAM) | 3 | Yes |
| KSI&#8209;IAM&#8209;APM | Identity and Access Management (IAM) | Adopting Passwordless Methods (APM) | 3 | Yes |
| KSI&#8209;IAM&#8209;ELP | Identity and Access Management (IAM) | Ensuring Least Privilege (ELP) | 3 | Yes |
| KSI&#8209;IAM&#8209;JIT | Identity and Access Management (IAM) | Authorizing Just-in-Time (JIT) | 2 | Yes |
| KSI&#8209;IAM&#8209;SNU | Identity and Access Management (IAM) | Securing Non-User Authentication (SNU) | 3 | Yes |
| KSI&#8209;IAM&#8209;SUS | Identity and Access Management (IAM) | Responding to Suspicious Activity (SUS) | 2 | Yes |
| KSI&#8209;INR&#8209;AAR | Incident Response (INR) | Generating After Action Reports (AAR) | 3 | Yes |
| KSI&#8209;INR&#8209;RIR | Incident Response (INR) | Reviewing Incident Response Procedures (RIR) | 3 | Yes |
| KSI&#8209;INR&#8209;RPI | Incident Response (INR) | Reviewing Past Incidents (RPI) | 3 | Yes |
| KSI&#8209;MLA&#8209;ALA | Monitoring, Logging, and Auditing (MLA) | Authorizing Log Access (ALA), optional at Class B | 2 | Yes |
| KSI&#8209;MLA&#8209;EVC | Monitoring, Logging, and Auditing (MLA) | Evaluating Configurations (EVC) | 2 | Yes |
| KSI&#8209;MLA&#8209;LET | Monitoring, Logging, and Auditing (MLA) | Logging Event Types (LET) | 2 | Yes |
| KSI&#8209;MLA&#8209;OSM | Monitoring, Logging, and Auditing (MLA) | Operating SIEM Capability (OSM) | 3 | Yes |
| KSI&#8209;MLA&#8209;RVL | Monitoring, Logging, and Auditing (MLA) | Reviewing Logs (RVL) | 2 | Yes |
| KSI&#8209;PIY&#8209;GIV | Policy and Inventory (PIY) | Generating Inventories (GIV) | 0 | No |
| KSI&#8209;PIY&#8209;RES | Policy and Inventory (PIY) | Reviewing Executive Support (RES) | 0 | No |
| KSI&#8209;PIY&#8209;RIS | Policy and Inventory (PIY) | Reviewing Investments in Security (RIS) | 0 | No |
| KSI&#8209;PIY&#8209;RSD | Policy and Inventory (PIY) | Reviewing Security in the SDLC (RSD) | 0 | No |
| KSI&#8209;PIY&#8209;RVD | Policy and Inventory (PIY) | Reviewing Vulnerability Disclosures (RVD) | 0 | No |
| KSI&#8209;RPL&#8209;ABO | Recovery Planning (RPL) | Aligning Backups with Objectives (ABO) | 0 | No |
| KSI&#8209;RPL&#8209;ARP | Recovery Planning (RPL) | Aligning Recovery Plan (ARP) | 0 | No |
| KSI&#8209;RPL&#8209;RRO | Recovery Planning (RPL) | Reviewing Recovery Objectives (RRO) | 0 | No |
| KSI&#8209;RPL&#8209;TRC | Recovery Planning (RPL) | Testing Recovery Capabilities (TRC) | 0 | No |
| KSI&#8209;SCR&#8209;MIT | Supply Chain Risk (SCR) | Mitigating Supply Chain Risk (MIT) | 0 | No |
| KSI&#8209;SCR&#8209;MON | Supply Chain Risk (SCR) | Monitoring Supply Chain Risk (MON) | 0 | No |
| KSI&#8209;SVC&#8209;ACM | Service Configuration (SVC) | Automating Configuration Management (ACM) | 2 | Yes |
| KSI&#8209;SVC&#8209;ASM | Service Configuration (SVC) | Automating Secret Management (ASM) | 3 | Yes |
| KSI&#8209;SVC&#8209;EIS | Service Configuration (SVC) | Evaluating and Improving Security (EIS) | 2 | Yes |
| KSI&#8209;SVC&#8209;PRR | Service Configuration (SVC) | Preventing Residual Risk (PRR), optional at Class B | 2 | Yes |
| KSI&#8209;SVC&#8209;RUD | Service Configuration (SVC) | Removing Unwanted Data (RUD), optional at Class B | 3 | Yes |
| KSI&#8209;SVC&#8209;SIN | Service Configuration (SVC) | Securing Information (SIN) | 3 | Yes |
| KSI&#8209;SVC&#8209;VCM | Service Configuration (SVC) | Validating Communications (VCM), optional at Class B | 3 | Yes |
| KSI&#8209;SVC&#8209;VRI | Service Configuration (SVC) | Validating Resource Integrity (VRI) | 2 | Yes |

</details>
<!-- END GENERATED: class-b -->

### Class C

This repo's target. At least 2 automated measures per KSI, a MUST at this class (FRC&#8209;CSX&#8209;VVK).

<!-- BEGIN GENERATED: class-c -->
**35 of 46 KSIs ready**, with at least 2 automated measures each.

<details>
<summary>All 46 KSIs at Class C</summary>

| KSI ID | Theme | Indicator | Automated measures | Ready |
|---|---|---|---|---|
| KSI&#8209;CED&#8209;RAT | Cybersecurity Education (CED) | Reviewing All Training (RAT) | 4 | Yes |
| KSI&#8209;CMT&#8209;LMC | Change Management (CMT) | Logging Changes (LMC) | 3 | Yes |
| KSI&#8209;CMT&#8209;RMV | Change Management (CMT) | Redeploying vs Modifying (RMV) | 2 | Yes |
| KSI&#8209;CMT&#8209;RVP | Change Management (CMT) | Reviewing Change Procedures (RVP) | 2 | Yes |
| KSI&#8209;CMT&#8209;VTD | Change Management (CMT) | Validating Throughout Deployment (VTD) | 2 | Yes |
| KSI&#8209;CNA&#8209;DFP | Cloud Native Architecture (CNA) | Defining Functionality and Privileges (DFP) | 3 | Yes |
| KSI&#8209;CNA&#8209;EIS | Cloud Native Architecture (CNA) | Enforcing Intended State (EIS) | 3 | Yes |
| KSI&#8209;CNA&#8209;IBP | Cloud Native Architecture (CNA) | Implementing Best Practices (IBP) | 3 | Yes |
| KSI&#8209;CNA&#8209;MAT | Cloud Native Architecture (CNA) | Minimizing Attack Surface (MAT) | 3 | Yes |
| KSI&#8209;CNA&#8209;OFA | Cloud Native Architecture (CNA) | Optimizing for Availability (OFA) | 2 | Yes |
| KSI&#8209;CNA&#8209;RNT | Cloud Native Architecture (CNA) | Restricting Network Traffic (RNT) | 3 | Yes |
| KSI&#8209;CNA&#8209;RVP | Cloud Native Architecture (CNA) | Reviewing Protections (RVP) | 2 | Yes |
| KSI&#8209;CNA&#8209;ULN | Cloud Native Architecture (CNA) | Using Logical Networking (ULN) | 3 | Yes |
| KSI&#8209;IAM&#8209;AAM | Identity and Access Management (IAM) | Automating Account Management (AAM) | 3 | Yes |
| KSI&#8209;IAM&#8209;APM | Identity and Access Management (IAM) | Adopting Passwordless Methods (APM) | 3 | Yes |
| KSI&#8209;IAM&#8209;ELP | Identity and Access Management (IAM) | Ensuring Least Privilege (ELP) | 3 | Yes |
| KSI&#8209;IAM&#8209;JIT | Identity and Access Management (IAM) | Authorizing Just-in-Time (JIT) | 2 | Yes |
| KSI&#8209;IAM&#8209;SNU | Identity and Access Management (IAM) | Securing Non-User Authentication (SNU) | 3 | Yes |
| KSI&#8209;IAM&#8209;SUS | Identity and Access Management (IAM) | Responding to Suspicious Activity (SUS) | 2 | Yes |
| KSI&#8209;INR&#8209;AAR | Incident Response (INR) | Generating After Action Reports (AAR) | 3 | Yes |
| KSI&#8209;INR&#8209;RIR | Incident Response (INR) | Reviewing Incident Response Procedures (RIR) | 3 | Yes |
| KSI&#8209;INR&#8209;RPI | Incident Response (INR) | Reviewing Past Incidents (RPI) | 3 | Yes |
| KSI&#8209;MLA&#8209;ALA | Monitoring, Logging, and Auditing (MLA) | Authorizing Log Access (ALA) | 2 | Yes |
| KSI&#8209;MLA&#8209;EVC | Monitoring, Logging, and Auditing (MLA) | Evaluating Configurations (EVC) | 2 | Yes |
| KSI&#8209;MLA&#8209;LET | Monitoring, Logging, and Auditing (MLA) | Logging Event Types (LET) | 2 | Yes |
| KSI&#8209;MLA&#8209;OSM | Monitoring, Logging, and Auditing (MLA) | Operating SIEM Capability (OSM) | 3 | Yes |
| KSI&#8209;MLA&#8209;RVL | Monitoring, Logging, and Auditing (MLA) | Reviewing Logs (RVL) | 2 | Yes |
| KSI&#8209;PIY&#8209;GIV | Policy and Inventory (PIY) | Generating Inventories (GIV) | 0 | No |
| KSI&#8209;PIY&#8209;RES | Policy and Inventory (PIY) | Reviewing Executive Support (RES) | 0 | No |
| KSI&#8209;PIY&#8209;RIS | Policy and Inventory (PIY) | Reviewing Investments in Security (RIS) | 0 | No |
| KSI&#8209;PIY&#8209;RSD | Policy and Inventory (PIY) | Reviewing Security in the SDLC (RSD) | 0 | No |
| KSI&#8209;PIY&#8209;RVD | Policy and Inventory (PIY) | Reviewing Vulnerability Disclosures (RVD) | 0 | No |
| KSI&#8209;RPL&#8209;ABO | Recovery Planning (RPL) | Aligning Backups with Objectives (ABO) | 0 | No |
| KSI&#8209;RPL&#8209;ARP | Recovery Planning (RPL) | Aligning Recovery Plan (ARP) | 0 | No |
| KSI&#8209;RPL&#8209;RRO | Recovery Planning (RPL) | Reviewing Recovery Objectives (RRO) | 0 | No |
| KSI&#8209;RPL&#8209;TRC | Recovery Planning (RPL) | Testing Recovery Capabilities (TRC) | 0 | No |
| KSI&#8209;SCR&#8209;MIT | Supply Chain Risk (SCR) | Mitigating Supply Chain Risk (MIT) | 0 | No |
| KSI&#8209;SCR&#8209;MON | Supply Chain Risk (SCR) | Monitoring Supply Chain Risk (MON) | 0 | No |
| KSI&#8209;SVC&#8209;ACM | Service Configuration (SVC) | Automating Configuration Management (ACM) | 2 | Yes |
| KSI&#8209;SVC&#8209;ASM | Service Configuration (SVC) | Automating Secret Management (ASM) | 3 | Yes |
| KSI&#8209;SVC&#8209;EIS | Service Configuration (SVC) | Evaluating and Improving Security (EIS) | 2 | Yes |
| KSI&#8209;SVC&#8209;PRR | Service Configuration (SVC) | Preventing Residual Risk (PRR) | 2 | Yes |
| KSI&#8209;SVC&#8209;RUD | Service Configuration (SVC) | Removing Unwanted Data (RUD) | 3 | Yes |
| KSI&#8209;SVC&#8209;SIN | Service Configuration (SVC) | Securing Information (SIN) | 3 | Yes |
| KSI&#8209;SVC&#8209;VCM | Service Configuration (SVC) | Validating Communications (VCM) | 3 | Yes |
| KSI&#8209;SVC&#8209;VRI | Service Configuration (SVC) | Validating Resource Integrity (VRI) | 2 | Yes |

</details>
<!-- END GENERATED: class-c -->

### Class D

Significant assurance. On top of Class C:

- At least 4 automated measures per KSI (FRC&#8209;CSX&#8209;VVK).
- Cryptographic modules validated by NIST are required, not just recommended (CMU&#8209;CSO&#8209;UVM).
- Certification materials are supplied for each service (CDS&#8209;CSO&#8209;PSM).
- The Certification Package is brought up to date at least once a week (CPO&#8209;CSX&#8209;CPM).
- KSI metrics must significantly exceed lower classes, with specifics to be set during FedRAMP's 20x Phase 4 Pilot (SDR&#8209;CSX&#8209;KMT).

For the full rules, see [FedRAMP/rules](https://github.com/FedRAMP/rules).

## The catalog

Pinned to FedRAMP/rules commit [`a89d784`](https://github.com/FedRAMP/rules/commit/a89d78477ddea98dc57eca24f5007794c2b4eeb6), dataset version `2026.10.13.01`.

| Theme | Indicators |
|---|---|
| Cybersecurity Education (CED) | 1 |
| Change Management (CMT) | 4 |
| Cloud Native Architecture (CNA) | 8 |
| Identity and Access Management (IAM) | 6 |
| Incident Response (INR) | 3 |
| Monitoring, Logging, and Auditing (MLA) | 5 |
| Policy and Inventory (PIY) | 5 |
| Recovery Planning (RPL) | 4 |
| Supply Chain Risk (SCR) | 2 |
| Service Configuration (SVC) | 8 |

Each indicator has a statement and the NIST SP 800-53 controls it maps to (558 mappings in total; KSI&#8209;PIY&#8209;RES maps to none). Five (CNA&#8209;EIS, MLA&#8209;ALA, SVC&#8209;PRR, SVC&#8209;RUD, SVC&#8209;VCM) have separate statements for service classes B and C instead of one statement. The loader keeps them separate and never fills in a missing class from another one.

```python
from fedramp_ksi import load_catalog

catalog = load_catalog()
ksi = catalog.indicator("KSI-MLA-ALA")
ksi.controls  # ('au-12.3', 'au-6.7', 'si-11')
ksi.statement_for("c")  # the class C statement; None for a class with no statement
```

## Measures

A measure is one specific, checkable thing that demonstrates a KSI, such as "every commit on the default branch belongs to a merged pull request". Each measure states its objective, what's checked, the metric tracked over time, the data source, how often it runs, whether it's automated, and the evidence it produces. See [`measures/README.md`](./measures/README.md) for the fields and how they map to FedRAMP's Security Decision Record.

FedRAMP sets a minimum number of **automated** measures per KSI by certification class (FRC&#8209;CSX&#8209;VVK): 1 for Class B, 2 for Class C, 4 for Class D. The target here is **Class C**. Readiness by theme, the number of KSIs that meet each class's minimum:

<!-- BEGIN GENERATED: readiness -->
| Theme | Class B | Class C | Class D |
|---|---|---|---|
| Cybersecurity Education (CED) | 1/1 | 1/1 | 1/1 |
| Change Management (CMT) | 4/4 | 4/4 | 0/4 |
| Cloud Native Architecture (CNA) | 8/8 | 8/8 | 0/8 |
| Identity and Access Management (IAM) | 6/6 | 6/6 | 0/6 |
| Incident Response (INR) | 3/3 | 3/3 | 0/3 |
| Monitoring, Logging, and Auditing (MLA) | 5/5 | 5/5 | 0/5 |
| Service Configuration (SVC) | 8/8 | 8/8 | 0/8 |
| Other 3 themes: Policy and Inventory (PIY), Recovery Planning (RPL), Supply Chain Risk (SCR) | 0/11 | 0/11 | 0/11 |
<!-- END GENERATED: readiness -->

The readiness table comes from the same command as the certification class sections above.

## Requirements vs. design decisions

FedRAMP sets the KSI statements, the rules a measure implements, the 800-53 controls mapped to each KSI, and the minimum number of automated measures per class (FRC&#8209;CSX&#8209;VVK). Everything else here is a design choice for the theoretical service, and is labeled as one.

Decisions that apply to every theme:

- **Infrastructure** is AWS, deployed by Terraform from GitHub, the same setup as aws-federal-baseline.
- **Workloads** run as containers on Amazon ECS with Fargate in private subnets. The only public entry points are load balancers behind AWS WAF.
- **Changes** go through GitHub pull requests with required checks.
- **Logs** are centralized in a dedicated log archive account and a SIEM.
- **Incidents** are issues in a private GitHub incident repository, and after action reports are merged pull requests in it.
- **People and roles** come from an identity provider's accounts and groups. Staff sign in with phishing-resistant methods only, and reach AWS through IAM Identity Center.
- **Customer data** is encrypted with a separate AWS KMS key for each customer, so deleting the key removes that customer's data everywhere, including backups.
- **Customers** sign in through SAML or OIDC federation with their own identity provider, or with passkeys for local accounts.
- **Shared responsibility:** measures check what the service provides and enforces. How customers configure their own identity providers and settings is their responsibility, and isn't measured.
- **Training** is assigned and tracked in a training platform with a read-only reporting API.
- **Manual reviews** are recorded as attestations and use the automated measures' results as inputs.
- **The target** is Class C.

Each measure also lists its own decisions in a `decisions` field, such as thresholds and cadences. To see them all with the FedRAMP rules and controls each measure maps to, run `uv run python -m fedramp_ksi.measures --decisions`.

## How changes are checked

Every pull request runs these checks. None of them use credentials or contact anything besides GitHub and the Python package index.

| Check | Tool | Catches |
|---|---|---|
| Lint and format | Ruff | Style issues, likely bugs, unformatted code |
| Tests | pytest | Catalog drift, altered data files, schema violations |

Separately, every Monday the **Upstream check** workflow hashes the pinned files at the latest [FedRAMP/rules](https://github.com/FedRAMP/rules) commit. If either file changed, it opens an issue with links to the diff, unless one is already open. Changes to other upstream files are ignored. It can also be run from the Actions tab.

## Repository controls

| Control | Implementation | Maps to |
|---|---|---|
| Change management | A ruleset on `main` requires a pull request and a passing `checks` job, and blocks force-pushes and deletion. It applies to the owner too. | CM&#8209;3; SOC 2 CC8.1 |
| Supply chain | Actions pinned to commit SHAs, with pinning enforced in repository settings; upstream data pinned to a commit and SHA-256; 7-day Dependabot cooldown | SR&#8209;3; SOC 2 CC9.2 |
| Patch management | Dependabot updates for actions and Python dependencies, and Dependabot alerts for known vulnerabilities | SI&#8209;2, RA&#8209;5 |
| Data integrity | The loader refuses data that doesn't match its pinned hash or FedRAMP's schema; a weekly check flags upstream changes | SI&#8209;7, CA&#8209;7 |
| Secrets | Secret scanning and push protection | IA&#8209;5(7) |
| AI tooling guardrails | Claude Code permission rules deny the `aws` CLI, Terraform commands that contact AWS, reads of credential files, and force-pushes; commits, pushes, and pull requests require approval | AC&#8209;6, CM&#8209;7 |

## Known gaps

- **Class A's process rules aren't modeled yet.** Of the 16 rules besides KSIs in FRC&#8209;CLA&#8209;MFR, only IEC&#8209;CSO&#8209;EFR and IEC&#8209;CSO&#8209;FIR are covered by a measure. Some, such as the existing SOC 2 Type II, FedRAMP Rev5, or GovRAMP certification and a FedRAMP Recognized assessor, need a real provider.
- **Upstream updates are applied by hand, on purpose.** The weekly check finds changes; copying new files and updating the test expectations is a reviewed pull request.
- **Measures cover 7 of 10 themes.** Cloud Native Architecture (CNA), Cybersecurity Education (CED), Change Management (CMT), Identity and Access Management (IAM), Incident Response (INR), Monitoring, Logging, and Auditing (MLA), and Service Configuration (SVC) meet the Class C target; the other 11 KSIs have no measures yet.
- **Per-measure decisions are only consolidated by running a command.** The README lists the service-wide decisions, but a reader on GitHub has to open each TOML file, or run `--decisions`, to see the rest. A generated page checked by tests would fix that.
- **The training platform API is a placeholder.** `training.py` assumes a generic paged JSON endpoint. Connecting a real platform means mapping its endpoint and field names; the overdue check doesn't change. Who needs each course (identity provider groups, GitHub write access) isn't fetched yet.
- **FedRAMP's five default artifacts don't map one-to-one to its SDR schema.** SDR&#8209;CSX&#8209;KSI lists five artifacts, but the SDR schema (v1.1.1) has implementation, validation, and assessment statements. The evidence step will document the mapping.

## Roadmap

1. Measures for the other 3 themes, to Class C: Policy and Inventory (PIY), Recovery Planning (RPL), and Supply Chain Risk (SCR)
2. A generated page of every measure's requirements and decisions, kept current by tests
3. Machine-readable evidence per KSI as a Security Decision Record that validates against FedRAMP's SDR schema
4. Coverage rollup from aws-federal-baseline's 800-53 annotations
5. Compliance platform client built against recorded responses and a local mock server

## License

MIT for the code in this repository. The files in `data/` are FedRAMP's, copied unchanged from [FedRAMP/rules](https://github.com/FedRAMP/rules).
