# Pipes and Filters correspondence

## Public open-source candidate

- **Project:** calesthio/OpenMontage
- **Revision:** `db91727598d08d40919d7d68a47864a5467bd448`
- **Exact manifest path:** `pipeline_defs/animated-explainer.yaml`
- **Exact loader path:** `lib/pipeline_loader.py`
- **Exact stage Skill roots:** `skills/pipelines/explainer/`
- **Status:** candidate correspondence
- **Frozen record:** [frozen evidence](evidence/openmontage-frozen-case.md)

The pinned manifest declares an ordered stage list, artifact requirements and
products, and stage Skill identifiers. The loader validates manifests and
extracts stage order and stage Skill paths. The corresponding stage instruction
files exist at the pinned paths.

This establishes a source-level pipeline candidate only. The snapshot does not
verify one common versioned record envelope across every stage, Filter
isolation, or observed runtime execution. Those missing relations prevent a
confirmed correspondence claim.

## Constructive sample

- **Status:** constructive
- **Pipe contract:**
  [`sample/references/support-ticket-record-contract.md`](sample/references/support-ticket-record-contract.md)
- **Root and Filter Skills:** [`sample/`](sample/)
- **Executable oracle:** [`sample/scripts/run_demo.py`](sample/scripts/run_demo.py)
- **Focused tests:** [`sample/tests/test_demo.py`](sample/tests/test_demo.py)

The local sample supplies the common versioned envelope, deep-copy transfers,
Filter substitution, canonical exactly-once order, fail-stop attribution, and
deterministic verification that remain unverified upstream.
