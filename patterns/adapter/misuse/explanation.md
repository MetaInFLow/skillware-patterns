# Why this is not Adapter

The neighboring `SKILL.md` changes field names but does not implement semantic
compatibility. It drops canonical `id`, so the output cannot be traced to the
same issue identity. It also drops `severity` merely because the Target names
the concept `priority`, losing a required meaning instead of translating it.

An Adapter must preserve the Adaptee's required semantics through the Target
contract. In the constructive sample, identity becomes `external_id` and
canonical severity is mapped to a documented target representation. The misuse
does neither. Field renaming alone is therefore not enough to satisfy the Gang
of Four Adapter intent, even though the output resembles a Jira payload.
