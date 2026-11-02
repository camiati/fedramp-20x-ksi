# fedramp-20x-ksi

FedRAMP 20x Key Security Indicators (KSIs) as code, with automated evidence.

Companion to [The Grid](https://github.com/camiati/The-Grid), a reference guide to the frameworks, and [aws-federal-baseline](https://github.com/camiati/aws-federal-baseline), a Terraform baseline mapped to NIST SP 800-53. Everything here is a theoretical reference: there is no real system, tenant, or account behind it.

## What's here

| File | Defines |
|---|---|
| `src/fedramp_ksi/catalog.py` | Loads the KSI catalog and FedRAMP's rule IDs, checks them against their pinned SHA-256 and FedRAMP's JSON schema |
| `src/fedramp_ksi/upstream.py` | Compares the pinned files with the latest FedRAMP/rules commit and writes an issue body when they differ |
| `src/fedramp_ksi/measures.py` | Loads measures, checks them against the catalog, reports readiness for Classes B, C, and D, and lists each measure's design decisions |
| `src/fedramp_ksi/training.py` | Placeholder client for a training platform's reporting API, and the check for who is overdue on training (KSI&#8209;CED&#8209;RAT) |
| [`measures/`](./measures/) | Measures for each KSI theme, one TOML file per theme, with a field reference |
| `tests/test_catalog.py` | Pins the catalog: themes, indicator IDs, class-specific statements, rule IDs, and fields read |
| `tests/test_upstream.py` | Tests the upstream comparison with faked downloads, offline |
| `tests/test_measures.py` | Checks measures against the catalog and the Class C target, and tests every validation rule |
| `tests/test_training.py` | Tests the training client with faked responses and a mock server on 127.0.0.1, and the overdue check |
| `.github/workflows/checks.yml` | Lint, format, and tests on every pull request |
| `.github/workflows/upstream-check.yml` | Weekly upstream check that opens an issue when pinned files change |
| `data/fedramp-consolidated-rules.json` | FedRAMP's machine-readable rules, copied unchanged from [FedRAMP/rules](https://github.com/FedRAMP/rules) |
| `data/fedramp-consolidated-rules.schema.json` | FedRAMP's JSON schema for the rules, copied unchanged |
| `data/upstream.json` | The upstream commit and the SHA-256 of each copied file |
| [`CLAUDE.md`](./CLAUDE.md) | Instructions for Claude Code: conventions, workflow, and hard rules |
| [`.claude/settings.json`](./.claude/settings.json) | Enforced permission rules for Claude Code |

## The catalog

Pinned to FedRAMP/rules commit [`a89d784`](https://github.com/FedRAMP/rules/commit/a89d78477ddea98dc57eca24f5007794c2b4eeb6), dataset version `2026.10.13.01`.

| Theme | Name | Indicators |
|---|---|---|
| KSI&#8209;CED | Cybersecurity Education | 1 |
| KSI&#8209;CMT | Change Management | 4 |
| KSI&#8209;CNA | Cloud Native Architecture | 8 |
| KSI&#8209;IAM | Identity and Access Management | 6 |
| KSI&#8209;INR | Incident Response | 3 |
| KSI&#8209;MLA | Monitoring, Logging, and Auditing | 5 |
| KSI&#8209;PIY | Policy and Inventory | 5 |
| KSI&#8209;RPL | Recovery Planning | 4 |
| KSI&#8209;SCR | Supply Chain Risk | 2 |
| KSI&#8209;SVC | Service Configuration | 8 |

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

FedRAMP sets a minimum number of **automated** measures per KSI by certification class (FRC&#8209;CSX&#8209;VVK): 1 for Class B, 2 for Class C, 4 for Class D. The target here is **Class C**. Readiness so far, from `uv run python -m fedramp_ksi.measures`:

| Theme | Class B | Class C | Class D |
|---|---|---|---|
| KSI&#8209;CED | 1/1 | 1/1 | 1/1 |
| KSI&#8209;CMT | 4/4 | 4/4 | 0/4 |
| KSI&#8209;CNA | 8/8 | 8/8 | 0/8 |
| KSI&#8209;IAM | 6/6 | 6/6 | 0/6 |
| KSI&#8209;INR | 3/3 | 3/3 | 0/3 |
| KSI&#8209;MLA | 5/5 | 5/5 | 0/5 |
| KSI&#8209;SVC | 8/8 | 8/8 | 0/8 |
| Other 3 themes | 0/11 | 0/11 | 0/11 |

All 7 KSIs that Class A requires (FRC&#8209;CLA&#8209;MFR) have measures.

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

- **Upstream updates are applied by hand, on purpose.** The weekly check finds changes; copying new files and updating the test expectations is a reviewed pull request.
- **Measures cover 7 of 10 themes.** Cloud Native Architecture, Cybersecurity Education, Change Management, Identity and Access Management, Incident Response, Monitoring, Logging, and Auditing, and Service Configuration meet the Class C target; the other 11 KSIs have no measures yet.
- **Per-measure decisions are only consolidated by running a command.** The README lists the service-wide decisions, but a reader on GitHub has to open each TOML file, or run `--decisions`, to see the rest. A generated page checked by tests would fix that.
- **The training platform API is a placeholder.** `training.py` assumes a generic paged JSON endpoint. Connecting a real platform means mapping its endpoint and field names; the overdue check doesn't change. Who needs each course (identity provider groups, GitHub write access) isn't fetched yet.
- **FedRAMP's five default artifacts don't map one-to-one to its SDR schema.** SDR&#8209;CSX&#8209;KSI lists five artifacts, but the SDR schema (v1.1.1) has implementation, validation, and assessment statements. The evidence step will document the mapping.

## Roadmap

1. Measures for the other 3 themes, to Class C: Policy and Inventory (KSI&#8209;PIY), Recovery Planning (KSI&#8209;RPL), and Supply Chain Risk (KSI&#8209;SCR)
2. A generated page of every measure's requirements and decisions, kept current by tests
3. Machine-readable evidence per KSI as a Security Decision Record that validates against FedRAMP's SDR schema
4. Coverage rollup from aws-federal-baseline's 800-53 annotations
5. Compliance platform client built against recorded responses and a local mock server

## License

MIT for the code in this repository. The files in `data/` are FedRAMP's, copied unchanged from [FedRAMP/rules](https://github.com/FedRAMP/rules).
