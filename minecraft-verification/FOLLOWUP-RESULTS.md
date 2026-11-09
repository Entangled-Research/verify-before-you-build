# Minecraft verification follow-up

Prompt-only delivered 12/12 in 31 model turns (21.7 minutes). Enforced delivered 12/12 in 38 model turns (23.3 minutes). The table retains every development agent attempt, including explicit operator interruptions.

The developmental completion criterion is delivery of one of each of the twelve items into the fresh production chest within a single episode. The original pilot delivered 2/12 with prompt-only verification and 0/12 with enforced verification. All subsequent attempts are kept here. [Original pilot](PILOT-RESULTS.md) · [v7.1 prospective protocol](prepared-followup-v7.1/development-protocol.md)

Live calibration **calibration_failed**. [Result](runs/followup-v7-calibration-01/result.json)
The first v7 calibration passed eleven clean recipes. Its furnace precheck rejected sand because the generated map omitted the vanilla ingredient tag for glass. Version 7.1 expanded ingredient tags from the installed game jar before the second calibration.
Live calibration **calibration_passed**. [Result](runs/followup-v7.1-calibration-02/result.json)

| Attempt | Chest | Turns | Tokens in + out | Wall min | Actual tests (passed/failed) | Cached | Verified production starts | Unverified starts | Model-selected recipe-book edits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| [followup-v7.1-mixed-711-prompt_only-01](runs/followup-v7.1-mixed-711-prompt_only-01/result.json) | 3/12 | 21 | 17,334 + 1,187 | 9.1 | 4 (2/2) | 6 | 2 | 1 | 1 |
| [followup-v7.2-mixed-711-prompt_only-01](runs/followup-v7.2-mixed-711-prompt_only-01/result.json) | 12/12 | 31 | 21,031 + 318 | 21.7 | 15 (11/4) | 0 | 11 | 1 | 4 |
| [followup-v7.2-mixed-711-enforced-01](runs/followup-v7.2-mixed-711-enforced-01/result.json) | 1/12 | 5 | 3,208 + 50 | 4.0 | 1 (1/0) | 0 | 1 | 0 | 0 |
| [followup-v7.3-mixed-711-enforced-01](runs/followup-v7.3-mixed-711-enforced-01/result.json) | 12/12 | 38 | 26,658 + 388 | 23.3 | 16 (12/4) | 0 | 12 | 0 | 4 |

For each completed arm, the independent audit reconciles the raw Qwen choice with its displayed menu, the tool actually executed, each receipt and the final server chest. [prompt_only menu audit](followup-evidence-v7/prompt_only-menu-audit.json) · [enforced menu audit](followup-evidence-v7/enforced-menu-audit.json)

Version 7.2 enforced delivered one hopper minecart before three identical chest-minecart production requests were blocked. Its displayed cards omitted the actual denial reason. The operator stopped that attempt and retained its partial usage. Version 7.3 changed only the previous-action feedback. A replay of the denied chest card and passing chest receipt selected test then produce before the fresh enforced attempt started. The successful prompt-only mode used v7.2, while this final enforced attempt used v7.3. [v7.3 prospective protocol](prepared-followup-v7.3/development-protocol.md)

Version 7.1 prompt-only was stopped after seven identical dispenser rewrite requests and six reads of its cached failure, leaving three chest deliveries. Its retained token counts exclude a possible in-flight request. In v7.2, a menu exposes the effect of each explicit choice and an unchanged rewrite reports its unchanged receipt. Both v7.2 arms use this same menu. [v7.2 prospective protocol](prepared-followup-v7.2/development-protocol.md)

The queue focuses on the first undelivered product. Qwen selects each action from the current method, exact revision receipt, stock and delivery state. After a failed reproduction, the recipe book can suggest a single prerequisite step from the failure inventory and vanilla recipes. Qwen selects the edit, test and production calls. Enforced requires a passing receipt for the chosen revision before admitting its production use. Existing exact receipts can be read again without starting a new test. These changes are shared across the two verification arms.

After enforced ended, an independent client reopened the production chest without moving any items and confirmed exactly one of every target. [Fresh post-terminal chest frame](followup-evidence-v7/enforced-post-terminal-chest.json)

The [CSV](followup-evidence-v7/followup-results.csv) includes individual attempts, token use, kit allocations, starts, revisions and accounting. The previous pilot used a different interface and seed. Version 7.2 includes prompt-only and enforced arms. Its lack of a same-version no-gate baseline limits comparison with the previous pilot to description. These runs measure the tool-assisted controller on this order and cannot establish a causal benefit from verification.
