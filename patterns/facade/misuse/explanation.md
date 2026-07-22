# Why this is not Facade

The neighboring `SKILL.md` is only a directory of child Skills. It names three
specialists but defines no unified incident-response access operation, no
request/result contract, no routing or coordination behavior, and no fallback
for an unknown signal.

Naming or linking subsystem capabilities can help discovery, but discovery
alone does not simplify their collaboration for a Client. The missing
behavioral relation is decisive: the caller still has to choose each
specialist and invent the interaction. Therefore the artifact does not satisfy
the Gang of Four Facade intent even though its file shape resembles the
constructive sample.
