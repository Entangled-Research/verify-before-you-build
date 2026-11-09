# Minecraft manufacturing: verify before reuse

**Live experiment, November 8, 2026:** Java 1.21.6 calibration passed all 12
reference procedures and a separate delivery-chest smoke test. The first Andy
model run was interrupted after seven non-executable responses; its results
and the earlier calibration failures remain visible in the [LAN evidence
report](setup-evidence/LAN-RESULTS.md).

The new exploratory pilot uses the locally cached Qwen3.5-9B MLX checkpoint
and the same calibrated game executor. Its production player is
**ProfessorPickaxe**, its reset-test player is **InspectorIngot**, and
**ChronoCam** records as a separate spectator. The Qwen pilot's [prospective
amendment](setup-evidence/mlx-qwen/amendment-before-gameplay.md) records its
6/8 exact instruction-following preflight, fixed settings and interpretation
limits. The original Ollama and manual-arm setup notes below are historical.

Working claim: **Running this code from these starting resources produces these items.**

Prepared for local Minecraft Java **1.21.6** LAN and local Ollama. This is a
standalone verifier adapter using the existing `minecraft-demo` dependencies;
it does not modify that checkout's bots, settings, profiles, or action code.
It is not yet an integration with Efferents' journal/executor. Preparation alone does not start a Minecraft episode or model inference; live
calibration and episode results are stored separately under runs/.

## What you do at home

1. Start a **dedicated disposable Minecraft Java 1.21.6 world**, preferably named
   **Efferents Verification**. Enable commands/cheats. The experiment replaces two
   17 × 17 glass work areas with supported sand floors and sand corner pillars around `(0,100,0)` and `(32,100,0)`, so use a fresh world.
2. Choose **Open to LAN**, with **Allow Cheats: ON**. Leave Minecraft running
   and unpaused.
3. Tell Codex: **"The experiment world is open to LAN on port XXXXX. Set it up
   and run the calibration, then the matched comparison."**

**Do not launch Mindcraft, Ollama, a terminal command, or any bots yourself.**
Codex handles the remaining setup on this Mac: locate the active world, install
and load the datapack, start local inference, launch the experiment bots, arm
the episodes through the datapack, check calibration, and run
the matched conditions. You can watch the bots in Minecraft.

The runner creates two named Minecraft players automatically:

| Bot | Role |
|---|---|
| `ProfessorPickaxe` | The manufacturing agent. Plans with the local model and executes production actions. |
| `InspectorIngot` | The verifier's execution client. Replays methods in the separate test area; it is not another independent LLM agent. |

These use the same Mineflayer infrastructure as the existing Minecraft demo,
but the experiment runner replaces the ordinary Mindcraft chat/agent loop.
Neither bot needs operator permission. Privileged setup commands are entered
outside the agent tools. For this LAN session the trusted replay observer may
issue the single authorized setup reload; episode arming is automatic.

If calibration fails, Codex preserves its logs and fixes or reports the setup
problem before attempting comparisons. No model comparison should proceed on
uncalibrated instrumentation. If the running Minecraft version differs from
1.21.6, Codex reports the mismatch rather than silently mixing versions.

[Assistant operation guide](OPERATOR.md) contains the implementation commands;
they are for Codex to execute, not a checklist for you.

## What is frozen

One manufacturing order: deliver one each of hopper minecart, chest minecart,
crossbow, dispenser, sticky piston, comparator, repeater, lectern, enchanting
table, blast furnace, armor stand, and daylight detector. Supply base materials,
coal, one fixed crafting table and one fixed furnace. Final items go into a
delivery chest, checked directly through the game container interface.

Three conditions:

* `no_gate`: optional testing, no verification requirement.
* `prompt_only`: told to reproduce before relying on a method; no executor gate.
* `enforced`: identical prompt to `prompt_only`, but an unverified method cannot
  execute in production.

The same inspect, native-recipe query, direct craft/smelt, method revision,
method execution, and verification tools exist in all conditions. There is no
arbitrary code evaluation, slash-command tool, gathering, teleport tool, or
access to the production bot from test code. Procedures are executable sequences
of actual crafting/smelting operations; inventory assertions do not create items.

Two source libraries are prepared: 12 hand-authored reference procedures, and a
copy with four explicitly injected missing-prerequisite steps. These are **not
natural agent-generated publications**. Fault labels are saved for observers,
not shown to the planner. To study natural publication failures later, add a
separate source-author phase and freeze its unfiltered outputs before consumption.
Do not pool that future experiment with injected faults.

Each verification executes in a separate reset test arena from exactly the
method's declared inputs. Success requires newly produced output items. Test
outputs never enter production. Receipts bind the full procedure, input/output
contract, Minecraft version, workstations, episode context and adapter source.
A revised procedure requires a new receipt; the latest failed attempt revokes
the same revision's previous success. Reset/infrastructure failures remain
distinct from a failed production claim.

## Calibration and comparison

Codex first executes all 12 reference procedures through the real game without
an LLM. Every method must pass before any agent comparison starts. Calibration
failures are setup/adapter diagnostics, not research outcomes.

The initial comparison uses the mixed library and seed 701 across all three
arms. Codex launches one episode at a time with a fresh bot pair. The datapack
automatically rearms production when the previous producer disconnects. During an episode, do not add items, move
inventories, or modify the work areas. Codex disarms the setup after finishing.

The full exploratory matrix is **2 libraries × 3 arms × 3 repetitions = 18
episodes**, not 18 independent tasks. `prepared/schedule.json` rotates arm order
and lists seeds. Include the clean library to measure unnecessary blocking.
Run the first three paired episodes and inspect instrumentation before expanding.
Each episode has a 60-minute active limit, 70 model turns, 240 primitive attempts,
18 verification attempts and a 200,000 observed model-token stopping threshold.
One in-flight model response can cross the token threshold; it is fully counted.
Setup waiting is outside the active limit and reported wall time includes it.
All verification actions and inference count toward the same episode limits.
Test kits are separately allocated and logged; include them in resource reporting.
Model behavior may differ despite the same seed. Do not claim statistical
significance from this small exploratory matrix.

## Evidence and limits

Every run gets immutable initial protocol/source digests, source methods and
model/seed settings; append-only JSONL events; per-step before/after inventory;
furnace state; method revisions; receipts; delivery chest counts; model token
counts; failures; and final JSON results. Raw local inference responses are
retained. No fabricated metrics or self-reported success are used for completion.

```sh
./minecraft-verification/mc.sh summarize
```

Calibration is labeled separately. Missing/failed episodes remain visible.
Do not treat an infrastructure failure as task failure or drop it from a table
without reporting it. Token counts are local inference telemetry, not GPU FLOPs
or billed API cost. Inventory transfers into a furnace are not necessarily fuel
burned; retain fuel-slot/burn telemetry before interpreting consumption.

The gate enforces **declared** method use, not hidden intellectual dependence.
The planner may reject a method and implement direct native actions in any arm.
Interpret unverified starts together with method adoption and final completion.
Known Minecraft crafting tests workflow enforcement, not unknown scientific
discovery. A passing item-production test does not certify a functional installed
redstone circuit or generalize to different starting conditions.

Offline checks already available:

```sh
"$AUTHOR_HOME/Documents/efferents/minecraft-demo/.local/node22/bin/node" \
  --test minecraft-verification/test.mjs
./minecraft-verification/mc.sh preflight --offline
```

Sources: local Mindcraft/MineCollab checkout and bundled `minecraft-data` recipe
registry. Cite White et al., *Collaborating Action by Action* (2025),
https://arxiv.org/abs/2504.17950, if using this infrastructure in the paper.
Java 1.21.6 uses datapack format 80:
https://www.minecraft.net/en-us/article/minecraft-java-edition-1-21-6.

Camera-ready motivation: Kim et al., *Into the Unknown* (2026),
https://arxiv.org/abs/2610.19159, reports that none of 135 submissions from nine
agents on 15 open scientific follow-up problems met all evaluation conditions;
114 failed the authors' integrity check. This motivates checking claims against
execution evidence, not claiming that reproduction alone solves scientific
correctness. The citation and bounded statement have been added to the paper's
LaTeX source. The preserved submitted PDF has not been overwritten.
