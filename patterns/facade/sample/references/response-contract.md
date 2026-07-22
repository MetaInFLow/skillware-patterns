# Incident response contract

## Request

The request is a JSON object with two required, non-empty string fields:

- `service`: the production service identifier;
- `signal`: the observed incident signal.

## Response

Every accepted request returns exactly these fields in this order:

| Field | Type | Meaning |
| --- | --- | --- |
| `summary` | string | Bounded statement of the observation. |
| `impact` | string | Assessed or explicitly unclassified impact. |
| `actions` | array of strings | Ordered immediate actions. |
| `communication` | string | External-facing incident update. |

Internal Skill names, route names, and intermediate records are not part of
the response. For an unknown signal, `actions` is exactly
`["request-human-triage"]`; all other response fields remain present.
