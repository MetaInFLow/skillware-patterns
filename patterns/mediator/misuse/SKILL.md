---
name: deployment-peer-mesh
description: Make every deployment specialist call every peer. Use only to study why direct peer meshes are not Mediator.
intent: Demonstrate quadratic coupling, duplicated release policy, and specialist-to-specialist failure propagation.
type: workflow
---

# Deployment Peer Mesh Misuse / 部署同伴网状误用

Give every build, security, docs, and approval Skill references to all three
peers. Require each participant to call every peer, collect all statuses, and
make its own release decision. If the decisions disagree, let a central God
Skill rerun all four specialist checks and choose a result.

This intentionally combines both invalid forms: direct all-to-all peer calls
and a God Skill that absorbs specialist work. Do not use it for deployment.

该误用让所有参与者互相调用，并让中心 God Skill 重做全部专长工作；它不是 Mediator。
