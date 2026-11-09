# Minecraft manufacturing: verify before reuse

**Does executing a published procedure from its declared inputs actually produce
its claimed item?** This experiment measures method use, real verification
costs, and chest-confirmed manufacturing outcomes. It is a standalone
Mineflayer adapter, not the Efferents journal/executor itself.

The live Java 1.21.6 calibration passed all 12 reference procedures and a
separate production delivery-chest smoke test. The exploratory model block uses
the locally cached [Qwen3.5-9B-MLX-4bit configuration](prepared-lan-v6-qwen/protocol.json).
The earlier Andy/Ollama pilot was interrupted after seven non-executable
responses and is **not a completed comparison**. Its failed interface probes
and the earlier calibration failures remain in the [LAN evidence report](setup-evidence/LAN-RESULTS.md).

In the November 9 development runs, prompt-only v7.2 and enforced v7.3 each delivered all twelve requested items. The local model chose each repair from recipe-book suggestions derived from the failed test. Earlier attempts, including two interrupted runs, are retained in the [follow-up report](FOLLOWUP-RESULTS.md).

## Watching the experiment

The user opens the dedicated Java 1.21.6 world to LAN with commands enabled
and gives Codex the port. Codex handles the rest. On November 8 the confirmed
world was `verification benchmark`, LAN port 61196.

| Player | Role |
|---|---|
| **ProfessorPickaxe** | The manufacturing agent; the frozen local planner chooses among the finite tool set. |
| **InspectorIngot** | Executes a deterministic reproduction in a separate test area. It is not another LLM. |
| **ChronoCam** | Independent Replay Mod spectator. It observes the world and has no role in model decisions. |

The two boxes are centered at (0,100,0) and (32,100,0). Each has a 17 × 17
sand floor on sandstone, glass walls and roof, and four supported sand
corner pillars. Each reset verifies the selected floor, wall, roof and pillar
blocks against the live server. The table, furnace and chest remain near each
player. Do not move inventories or change the arenas during an active episode.

## What is compared

One order requires one hopper minecart, chest minecart, crossbow, dispenser,
sticky piston, comparator, repeater, lectern, enchanting table, blast furnace,
armor stand and daylight detector. The server—not the agent—determines delivery
by returning the contents of a freshly opened production chest.

Three arms use the same planner, checkpoint, seed, tools, budget, library,
arenas and observer. **No gate** allows optional testing. **Prompt only** asks
the planner to test before reuse but permits an unverified start. **Enforced**
uses the identical prompt-only instruction and blocks a method unless its exact
revision has a current, passing reproduction receipt. All arms can also inspect
recipes, craft or smelt directly, revise methods, and finish.

The authored clean library contains 12 reference procedures; the mixed library
omits prerequisites in four of them. These controlled omissions are **not
natural source-agent publications**. A receipt binds the procedure, contract,
Minecraft version, setup context and adapter; a new revision cannot borrow an
old receipt. Fresh test kits, all actions, fuel transfers, model tokens and wall
time are recorded. Test outputs never enter production. The gate controls
declared method use; it cannot detect undeclared intellectual reliance.

The frozen v6 pilot is the mixed library, seed 701, one fresh episode per arm.
Its [prospective amendment](prepared-lan-v6-qwen/amendment-before-gameplay.md)
preserves the failed 8/8 exact-choice preflight (6/8 exact, 8/8 parseable) and
explains why this is an exploratory manufacturing pilot. Budgets are 60
active minutes, 70 model turns, 240 primitive attempts, 18 test attempts and
a 200,000-observed-token threshold; a final in-flight response can cross it.
The original study ended after this triple. The later user-requested development attempts used their own frozen versions and seed 711.

## Evidence boundaries

- [Developmental follow-up results](FOLLOWUP-RESULTS.md): all four follow-up agent attempts, audited manufacturing deliveries, interface changes and separate calibration records.
- [Pilot results](PILOT-RESULTS.md) and [three-arm CSV](setup-evidence/mlx-qwen/pilot-comparison.csv): terminal Qwen outcomes and separately labeled scripted qualification.
- [Frozen v6 source and protocol](prepared-lan-v6-qwen/) and [calibration equivalence](prepared-lan-v6-qwen/qualification.json): same server datapack, executor, source methods, kits and schedule as the passed v5 calibration.
- [Model provenance](setup-evidence/mlx-qwen/provenance.json): exact cached snapshot, weight-file hashes and MLX runtime.
- [Run evidence](runs/): each episode has a separate manifest, append-only events, raw model responses/usage and result. Calibration, Andy's interrupted diagnostic and the Qwen arms remain separately labeled.
- [Scripted qualification specification](setup-evidence/qualification-v1/spec.json): independent lifecycle/fault controls, **not** model choices or pilot deliveries.
- [Operator guide](OPERATOR.md): exact local startup, datapack, arming, command authority, runner and audit workflow. The old default `prepared/` pack and Andy instructions are [historical](setup-evidence/historical-docs/).

This is one known manufacturing order at one pilot seed. A correct receipt
does not show that a planner will use it, that the order will be completed,
or that verification saves net compute. Do not infer statistical significance.
