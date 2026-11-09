# Minecraft verification pilot: mixed library, seed 701

All three arms left the same twelve-item order incomplete. Enforcing verification prevented unverified production starts but did not improve completion on this order and seed. One local Qwen model ran independently under each rule. The outcomes below use the server delivery chest. Real verifier reproductions, calibration deliveries and scripted tests earn no delivery credit for the agent.

| Arm | Delivered / 12 | Model turns | Prompt + output tokens | Time (min) | Primitive attempts | Test attempts | Unverified starts | Blocked starts |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| [no_gate](runs/prepared-lan-v6-qwen-mixed-r1-no_gate/result.json) | 2 | 70 | 162,945 + 2,656 | 39.1 | 121 | 0 | 61 | 0 |
| [prompt_only](runs/prepared-lan-v6-qwen-mixed-r1-prompt_only/result.json) | 2 | 70 | 195,735 + 6,739 | 53.9 | 102 | 1 | 29 | 0 |
| [enforced](runs/prepared-lan-v6-qwen-mixed-r1-enforced/result.json) | 0 | 56 | 199,793 + 1,356 | 52.7 | 66 | 11 | 0 | 45 |

Each arm started with fresh production stock, isolated verifier kits, a fresh conversation and an empty receipt table. The no-gate and prompt-only arms delivered one hopper minecart and one chest minecart each. Both exhausted the 70-turn limit; the prompt-only arm also crossed the 200,000-token start-of-turn check on its final request by 2,474 tokens. Enforced exceeded that threshold by 1,149 tokens. Token totals include all reported prompt and generated units; they do not estimate compute. Wall time includes setup. The two permissive arms each left one raw iron in an unlit production furnace, as established by separate post-terminal server reads. The fixed toolset cannot clear and recover that furnace, which can amplify a planning mistake after resources run short.

| Arm | Revision requests | Changed method identity | No change | New versions yielding their intended target |
| --- | ---: | ---: | ---: | ---: |
| [no_gate](setup-evidence/mlx-qwen/no-gate-revisions.json) | 9 | 2 | 7 | 0 |
| [prompt_only](setup-evidence/mlx-qwen/prompt-only-revisions.json) | 40 | 7 | 33 | 0 |
| [enforced](setup-evidence/mlx-qwen/enforced-revisions.json) | 0 | 0 | 0 | 0 |

No-gate allocated no verifier kits and attempted the supplied faulty crossbow and dispenser in production. Prompt-only allocated two logs, two raw iron, one coal and two string for its only isolated test; the supplied faulty crossbow procedure failed. It also started 18 crossbow and 9 dispenser procedures in production across their supplied and revised versions. Its revisions yielded no repaired target. In the enforced arm, the first attempt to reuse the hopper procedure without a receipt was blocked. The agent obtained a valid receipt for it, then repeatedly requested other unverified production methods. All 11 passing tests were repeats of that one method. Of 45 blocked requests, one was the initial hopper request and 44 were for the correct, untested chest minecart. None detected a defective procedure. There were zero production starts and no receipt bypass. The post-terminal production furnace and delivery chest were both empty. This arm exhausted the token budget on its 56th request; it did not hit the wall limit. Its 11 verifier kits allocated 110 raw iron, 22 logs and 22 coal in addition to its untouched production stock.

**Scripted controls, outside the agent episodes.** The [prospective specification](setup-evidence/qualification-v1/spec.json) was frozen before the controls began. The [control result](setup-evidence/qualification-v1/result-01/result.json) has status **qualification_passed**, 10/10 assertions true, 5 test attempts and zero model calls. Assertions and server observations are retained individually.

- PASS: unverified clean use blocks without production action or state change
- PASS: clean hopper reproduction verified with observed output delta
- PASS: authorized matching receipt produces one actual delivery
- PASS: changed hopper revision cannot reuse hopper receipt
- PASS: different chest minecart method cannot reuse hopper receipt
- PASS: mixed crossbow fails from exact fresh test kit
- PASS: mixed dispenser fails from exact fresh test kit
- PASS: mixed lectern fails from exact fresh test kit
- PASS: mixed blast_furnace fails from exact fresh test kit
- PASS: fault tests preserve production state

**Interpretation.** These are descriptive outcomes for one fixed order, mixed hand-authored library and seed. A valid test does not ensure the planner will use its receipt. Do not treat repeated tests of one procedure as independent replications, a correct untested method being blocked as a detected fault, or a scripted delivery as agent success. Primitive attempt counts include procedure steps in both testing and production. Test-kit allocations and wall time are reported separately. Neither this pilot nor its controls establish a general improvement in completion, compute cost or throughput.

The [frozen amendment](prepared-lan-v6-qwen/amendment-before-gameplay.md) records why the Qwen interface was used despite imperfect tool selection. [Calibration and rejected interface diagnostics](setup-evidence/LAN-RESULTS.md) are distinct from the matched comparisons. The [detailed pilot report](setup-evidence/mlx-qwen/pilot-report.md) includes individual test kits, resources, accounting and receipt evidence. See the [operator guide](OPERATOR.md) for reproduction. The [comparison CSV](setup-evidence/mlx-qwen/pilot-comparison.csv) contains one row per agent arm; independent packet/token audits are [no-gate](setup-evidence/mlx-qwen/no-gate-audit.json), [prompt-only](setup-evidence/mlx-qwen/prompt-only-audit.json) and [enforced](setup-evidence/mlx-qwen/enforced-audit.json). Further seeds and the clean-library matrix were not run; review the recovery tools and how results are exposed to the planner before expanding.
