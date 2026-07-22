# Why this is not Adapter

The neighboring `SKILL.md` changes field names but does not implement semantic
compatibility. It drops canonical `id`, so the output cannot be traced to the
same issue identity. It also drops `severity` after treating a scheduling
decision as the same concept, losing required meaning instead of translating it.

An Adapter must preserve the Adaptee's required semantics through the Target
contract. In the constructive sample, identity and severity are retained in
documented body, description, and label fields; no scheduling policy is
invented. The misuse does neither. Field renaming alone is therefore not enough
to satisfy the Gang of Four Adapter intent, even though the output resembles a
Jira request fragment.
