# Why this is not Composite

The neighboring `SKILL.md` is a directory of related investment capabilities,
but relation by topic is not part-whole composition. Its leaves return a list,
different objects, and an unstructured document, while the root returns paths.
A Client therefore cannot invoke an atomic result and a grouped result through
one Component contract.

A workflow also fails Composite when it merely sequences incompatible shapes
or lets multiple parents share one child as a DAG. Composite requires uniform
Leaf and Composite treatment plus one rooted, reachable, acyclic part-whole
tree. Folder nesting, a shared investment theme, or a workflow label does not
supply those properties. The constructive sample proves the distinction with
the same five result keys, explicit Leaf execution, exactly one parent per
non-root node, and whole-registry cycle and reachability validation.
