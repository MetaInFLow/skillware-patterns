# Why this is not Strategy

The root text contains a branch, but its alternatives are not interchangeable
algorithms for one task. Dependency discovery accepts a query and returns
links; deployment approval accepts a proposal and returns a decision. A caller
cannot substitute one branch for the other through a stable request/result
contract.

Conditional routing alone is insufficient. Strategy requires a Context that
delegates the same operation to independently variable ConcreteStrategies
implementing one Strategy interface. The constructive sample preserves that
relation: Fast Scan and Deep Review both accept one code-review request and
return one code-review result, even though their review procedures differ.
