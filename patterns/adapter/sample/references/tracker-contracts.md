# Tracker target contracts

## Canonical issue

The Adaptee accepts four required, non-empty string fields: `id`, `title`,
`description`, and `severity`. Severity is one of `low`, `medium`, `high`, or
`critical`. Every Adapter preserves canonical `id` as `external_id` so a
published payload remains traceable to the same issue. The outer request has
exactly `target` and `issue`; the nested issue has exactly the four canonical
fields. Additional fields are rejected rather than silently discarded.

## GitHub Target

| Canonical meaning | Target field | Translation |
| --- | --- | --- |
| identity | `external_id` | copy `id` |
| title | `title` | copy `title` |
| description | `body` | copy `description` |
| severity | `labels` | one label `severity:<value>` |

The severity vocabulary is preserved verbatim inside the label.

## Jira Target

| Canonical meaning | Target field | Translation |
| --- | --- | --- |
| identity | `external_id` | copy `id` |
| title | `summary` | copy `title` |
| description | `description` | copy `description` |
| severity | `priority.name` | `low` -> `Low`; `medium` -> `Medium`; `high` -> `High`; `critical` -> `Highest` |

## Linear Target

| Canonical meaning | Target field | Translation |
| --- | --- | --- |
| identity | `external_id` | copy `id` |
| title | `title` | copy `title` |
| description | `description` | copy `description` |
| severity | `priority` | `low` -> `4`; `medium` -> `3`; `high` -> `2`; `critical` -> `1` |

For this sample, Linear priorities mean `1` urgent, `2` high, `3` medium, and
`4` low. The mapping preserves ordering and maps canonical `critical` to the
Target's strongest available value, `urgent`.

## Compatibility rule

Field renaming is not enough. An Adapter must retain identity and preserve the
meaning of every required canonical field through a documented target
representation. If a Target cannot represent a required meaning, reject the
translation rather than silently omit or weaken it.
