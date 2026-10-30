# Measures

A **measure** is one specific, checkable thing that demonstrates a Key Security Indicator. There's one TOML file per KSI theme, such as `CMT.toml` for Change Management.

Every measure describes a theoretical cloud service: AWS infrastructure deployed by Terraform from GitHub, the same setup as [aws-federal-baseline](https://github.com/camiati/aws-federal-baseline). None of it describes a real system.

## Fields

| Field | Meaning | Feeds |
|---|---|---|
| `id` | Theme, KSI, and number, e.g. `CMT-LMC-01` | SDR `ksiTests` |
| `ksi` | The KSI it demonstrates, e.g. `KSI-CMT-LMC` | SDR `ksiId` |
| `objective` | What the measure is for | Default artifact 1 |
| `check` | Exactly what is checked | Default artifact 1 |
| `metric` | What's tracked over time | SDR-CSX-KMT metrics |
| `source` | Where the data comes from: `aws-cloudtrail`, `aws-config`, `aws-security-hub`, `github`, `terraform`, `vanta`, or `attestation` | |
| `cycle` | How often it runs: `per-change`, `continuous`, `daily`, `weekly`, `monthly`, `quarterly`, or `annual` | Default artifact 2 |
| `automated` | `true` or `false` | Default artifact 4; FRC-CSX-VVK counts |
| `manual_reason` | Required when `automated = false`: why automation isn't needed | Default artifact 4 |
| `evidence_type` | One of the SDR schema's evidence types: Log, Report, Screenshot, Configuration, Policy, Procedure, Audit Record | SDR `ksiEvidence` |
| `controls` | NIST SP 800-53 controls the measure supports; must be a subset of the KSI's controls | |

"Default artifacts" are the five items FedRAMP expects for each KSI (`info.default_artifacts.KSI`, required in the Security Decision Record by SDR-CSX-KSI). Artifacts 3 and 5, verification and validation, come from evidence, which is a later step.

## Readiness by class

FRC-CSX-VVK sets how many **automated** measures each KSI needs:

| Class | Minimum automated measures per KSI | Force |
|---|---|---|
| A | None | MAY |
| B | 1 | SHOULD |
| C | 2 | MUST |
| D | 4 | MUST |

Manual measures are still recorded, but they don't count toward the minimum. To see readiness for every class:

```sh
uv run python -m fedramp_ksi.measures
```

The target is Class C. Tests fail if a theme that has measures falls below it.
