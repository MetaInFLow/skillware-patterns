# Why this is not Observer

Polling sees state after the fact; it is not a Subject notification operation.
Broadcasting to every discovered endpoint also lacks the managed one-to-many
dependency: consumers never register or unregister through the Subject, and
the broadcaster does not invoke one shared Observer contract in deterministic
registration order.

Topic similarity and fan-out are insufficient. Observer requires an explicit
Subject, a common Observer update operation, registered ConcreteObservers, and
notification after ConcreteSubject state change. The constructive sample makes
those relations executable and additionally defines failure isolation,
per-observer accounting, event-copy isolation, and re-entry behavior.
