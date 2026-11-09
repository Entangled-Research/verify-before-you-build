# LAN verification experiment, November 8, 2026

**Calibration passed; no matched comparison was completed.** The Java 1.21.6
server at localhost:61196 returned all 12 expected reference outputs from
InspectorIngot's separate reset sand arena. Fresh server inventory packets
confirmed the exact starting kits and final outputs. ProfessorPickaxe then
manufactured a dispenser and deposited it; a newly opened server chest window
returned one dispenser. This positive control used no language model.

| Run | Outcome | Interpretation |
|---|---|---|
| [Calibration v2](../runs/calibration-20261108-lan-v2-01/result.json) | Infrastructure error; 0 actions | Mineflayer omitted the vanilla terrain-ready acknowledgement. [Paired packet probe](probe-ready.log). |
| [Calibration v3](../runs/calibration-20261108-lan-v3-01/result.json) | 8/12 preliminary receipts | Predicted batched crafting slots and reopened furnace fuel telemetry caused 4 failures. Retained, not used as final certification. |
| [Calibration v5](../runs/calibration-20261108-lan-v5-01/result.json) | 12/12, delivery smoke passed | [Readback audit](calibration-lan-v5-audit.json), 62 primitive attempts, 547.4 seconds, 0 model tokens. Version 4 was prepared but not loaded because the user requested the larger sand arenas before the reload. |
| [Mixed, seed 701, no gate](../runs/prepared-lan-v5-mixed-r1-no_gate/interruption.json) | Interrupted interface diagnostic | 7 complete non-JSON responses, 0 tool actions. A further in-flight response has unknown usage. Other arms did not start. |

**Model-interface finding.** The observed portions of the interrupted episode
used 13,567 prompt and 6,393 generation tokens. Some complete responses
contained Mindcraft-style commands rather than JSON. No action was recovered
from reasoning text. A cap on generation cannot explain all the failures:
a separate short probe with plain JSON mode produced the complete three-token
response `!inventory`; schema mode produced valid JSON but selected `finish`
instead of `inspect`. Ollama [documents this local JSON interface](https://docs.ollama.com/capabilities/structured-outputs).

Four labeled, Minecraft-disconnected diagnostics gave the unchanged local
Andy checkpoint five direct neutral requests each. All were format experiments
on the same requests, not held-out evidence of general skill. Exact action and
arguments matched on 1/5 (flat schema), 3/5 (command first), 3/5 (combined
test/run menu), and 0/5 (native command labels). Neither 3/5 variant got both
the requested test and the requested production use right. The original
requests, responses, schemas and [score ledger](same-model-preflight.json)
are retained. These observations do not justify comparing verification costs
or success rates. They do not establish a general Ollama bug.

Only Andy and the embedding-only embeddinggemma model were installed in Ollama.
The machine also has cached Qwen model weights, including Qwen3.5-9B-MLX-4bit.
The other research project's configured localhost:18590 endpoint had no listener
when inspected. No other project jobs, weights, or inference endpoints were
modified. Any alternative planner requires a new frozen block and an independent
interface check. The incomplete Andy run must remain visible.

The [pilot report](pilot-lan-v5-report.md) records the missing arms explicitly.
Earlier camera exports show calibration; do not label them as comparison footage.
