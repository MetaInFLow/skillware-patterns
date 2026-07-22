# Why this is not State

The text names onboarding phases and contains conditional branches, but it has
no persisted current state, State operation, or ConcreteState ownership. The
root prompt chooses all behavior, so the current phase is data passed through
one conditional procedure rather than an object that owns state-dependent
handling.

Restart recovery is also undefined: the workflow guesses from conversation
instead of validating a durable record. Illegal actions have no deterministic
rejection-before-write policy because there is no owned write at all. Phase
vocabulary is insufficient; State requires a Context delegating to its current
State, concrete implementations with distinct behavior, explicit legal
transitions, and recovery of the persisted state.
