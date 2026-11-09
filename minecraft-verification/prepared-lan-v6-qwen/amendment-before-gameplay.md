# Prospective amendment: exploratory Qwen pilot

Recorded before any Qwen Minecraft episode or action. This is a new pilot, not
a continuation or completion of the Andy comparison. The original Qwen exact
instruction-following qualification **failed**; it has not been changed to a
pass. The first Qwen probe was 1/7 exact under its reason-required parser.
The second, fresh eight-tool probe used feasible inventory/receipts and made
the non-executed rationale optional. All eight final responses were valid
allowed tool requests; six selected exactly the requested tool and arguments.
Direct craft selected use_method and direct smelt selected revise_method.
The requested verify, use, revision and finish were correctly expressed.

**Why run this pilot?** The model can express tool calls that the interpreter can
execute, including both testing and production reuse. Its occasional choice of
a different valid action is planner behavior. This pilot measures that behavior
and whether the gate is actually exercised, without claiming perfect instruction
following. Direct craft/smelt were not chosen correctly in that neutral probe.
The previous stricter result remains visible in every report.

**Scope and controls:** one exploratory mixed-library triple, seed 701, in order
no_gate, prompt_only, enforced. All arms use the same cached MLX Qwen3.5-9B-4bit
weights, pinned snapshot, tokenizer and runtime; dedicated localhost:18601;
temperature 0.2, maximum 1,024 output tokens per response, thinking disabled,
same strict final-content parser, finite tool set, context history and budgets.
The no_gate policy differs by design; prompt_only and enforced receive identical
prompts. Game executor, action definitions, reset kits, arena, libraries and
schedule are byte-identical to the positive v5 server calibration. Fresh bots,
inventories, conversations and receipt namespaces per arm. Keep ChronoCam as
the single steady recorder. No coaching, model substitution, response recovery
from reasoning/prose, artifact replacement, or code/fixture changes within the
block.

**Stopping and reporting:** keep wrong valid choices, failed method uses,
repairs, blocks, early finishes, and budget exits as outcomes. Five consecutive
structurally invalid requests mark an interface failure; stop for inspection on
missing usage, failed evidence audit, or infrastructure failure. These are not
successful arms. No retries. Do not expand to the remaining matrix before
reviewing this triple. The primary descriptive outputs are chest-confirmed
targets, declared method starts by receipt status, verification attempts,
blocked starts, repairs, material kits, action counts, inference tokens and
elapsed time. If negligible dependency activity occurs, the pilot cannot
establish an effect of the verification gate. No statistical significance or
cost-savings claims from this one exploratory triple.
