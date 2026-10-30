# fedramp-20x-ksi

FedRAMP 20x Key Security Indicators (KSIs) as code, with automated evidence.

Companion to [The Grid](https://github.com/camiati/The-Grid), a reference guide to the frameworks, and [aws-federal-baseline](https://github.com/camiati/aws-federal-baseline), a Terraform baseline mapped to NIST SP 800-53. Everything here is a theoretical reference: there is no real system, tenant, or account behind it.

## What's here

| File | Defines |
|---|---|
| `src/fedramp_ksi/catalog.py` | Loads the KSI catalog, checks it against its pinned SHA-256 and FedRAMP's JSON schema |
| `tests/test_catalog.py` | Pins the catalog: themes, indicator IDs, class-specific statements, and fields read |
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

## How changes are checked

Every pull request runs these checks. None of them use credentials or contact anything besides GitHub and the Python package index.

| Check | Tool | Catches |
|---|---|---|
| Lint and format | Ruff | Style issues, likely bugs, unformatted code |
| Tests | pytest | Catalog drift, altered data files, schema violations |

## Repository controls

| Control | Implementation | Maps to |
|---|---|---|
| Change management | All changes go through a branch and pull request with passing checks | CM&#8209;3; SOC 2 CC8.1 |
| Supply chain | Actions pinned to commit SHAs; upstream data pinned to a commit and SHA-256; 7-day Dependabot cooldown | SR&#8209;3; SOC 2 CC9.2 |
| Patch management | Dependabot updates for actions and Python dependencies | SI&#8209;2 |
| Data integrity | The loader refuses data that doesn't match its pinned hash or FedRAMP's schema | SI&#8209;7 |
| AI tooling guardrails | Claude Code permission rules deny the `aws` CLI, Terraform commands that contact AWS, reads of credential files, and force-pushes; commits, pushes, and pull requests require approval | AC&#8209;6, CM&#8209;7 |

## Known gaps

- **Upstream changes are found by hand.** A scheduled check against FedRAMP/rules is on the roadmap.
- **Branch protection, secret scanning, and SHA-pinning enforcement are repository settings**, configured in GitHub after the first pull request merges.

## Roadmap

1. Scheduled check that flags new FedRAMP/rules commits
2. Measures for each KSI: what's checked, how often, and the data source
3. Machine-readable evidence per KSI, built around FedRAMP's five default artifacts
4. Coverage rollup from aws-federal-baseline's 800-53 annotations
5. Vanta client built against recorded responses and a local mock server

## License

MIT for the code in this repository. The files in `data/` are FedRAMP's, copied unchanged from [FedRAMP/rules](https://github.com/FedRAMP/rules).
