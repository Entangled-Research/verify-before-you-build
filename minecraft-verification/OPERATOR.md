# Operator guide for the Minecraft verification runs

The user supplies the dedicated Java 1.21.6 LAN world and port. The observed
world is `verification benchmark`, host port 61196. These commands are for
the operator; the user need not start a bot, model, or terminal. Preserve
old runs and never rerun into an existing output directory.

## Completed developmental workflow

The November 9 follow-up used four fresh seed 711 episodes with the same locally cached Qwen snapshot described below. Prompt-only v7.1 stopped at 3/12. Prompt-only v7.2 delivered 12/12. Enforced v7.2 stopped at 1/12, then enforced v7.3 delivered 12/12 with improved feedback for denied requests. The [follow-up report](FOLLOWUP-RESULTS.md) links every attempt.

The development sources under `followup-v7.1/`, `followup-v7.2/` and `followup-v7.3/` are independent of the v6 source. Each has a frozen sibling `prepared-followup-VERSION/` with protocol, prompts, source hashes, fixtures and qualification. Full live v7.1 calibration passed the twelve clean recipes, four seeded negatives, duplicate receipt reuse, production delivery and furnace precheck/recovery. The later versions carry forward that physical qualification after checking source equality for unchanged game behavior. The v7.2 and v7.3 model-choice audits also reconcile every displayed option with its raw response and actual server action.

For a separately authorized reproduction with a unique output directory, use Node 22 and the CLI matching the selected freeze. This example shows the successful enforced configuration:

```sh
../minecraft-demo/.local/node22/bin/node minecraft-verification/followup-v7.3/cli.mjs episode --prepared minecraft-verification/prepared-followup-v7.3 --port 61196 --auto-arm --arm enforced --library minecraft-verification/prepared-followup-v7.3/library-mixed.json --seed 711 --out minecraft-verification/runs/NEW-UNUSED-DIRECTORY
```

The successful prompt-only configuration uses `followup-v7.2`, `prepared-followup-v7.2` and `--arm prompt_only`. Both use the same LAN enable/reload authority and dedicated MLX startup described below. The runs described in the report are terminal.

## Verify the world, pack and local dependencies

Use `lsof -nP -iTCP:61196 -sTCP:LISTEN`, inspect that Java PID's open
`session.lock`, and confirm its game version and `level.dat`. Do not infer
the active save from modification time. The v6 cached checkout is in
`minecraft-verification/prepared-lan-v6-qwen/`, including frozen source,
protocol, prompts, libraries, schedule, amendment and qualification. The
currently installed world pack is byte-identical to it and the v5 calibration.

The gameplay adapter uses the existing sibling `../minecraft-demo` Mineflayer
dependencies and its Node 22 runtime. From the research repository root:

```sh
../minecraft-demo/.local/node22/bin/node --test minecraft-verification/test.mjs
./minecraft-verification/mc.sh preflight --offline --prepared minecraft-verification/prepared-lan-v6-qwen
```

If installing in a confirmed fresh world, use `mc.sh install --prepared
minecraft-verification/prepared-lan-v6-qwen --world "$CONFIRMED_WORLD"`.
The CLI refuses to overwrite. For an intentional replacement, fingerprint and
archive **only** the existing experiment pack outside the save's datapacks;
preserve all other packs. Compare the installed files with the frozen pack.

A reload is needed only for a changed or newly installed pack. Use the actual
owner UI, or the separately controlled trusted recorder at an authorized
clean setup boundary with the existing LAN-command permission. In this
session **ReplayCamera**, the earlier observer, issued exactly one scoped
`/reload` at 19:11:36 PST; the [host log](setup-evidence/reload-lan-v5.log)
records the actual issuer. The subsequent recorder is ChronoCam. No new
operator grants, user impersonation, privileged research-agent shortcuts, or
model-accessible slash commands. The pack auto-arms on load and rearms
production only when ProfessorPickaxe is absent. All runtime invocations
therefore use `--auto-arm`; do not issue per-arm privileged commands.
For a different host/world/version, **recalibrate there** rather than carrying
forward this world's evidence.

## Start only the pinned local planner

This uses a dedicated MLX server at `127.0.0.1:18601`, not Ollama, a paid
API, or iteration-lab's own endpoint. The checkpoint is cached locally at
revision `938d8919941c6e7efd3c7150eff7fe9d12afa631`. Confirm the port is
free (or is the already running matching experiment server), available memory
is sufficient, and no nearby project's jobs will be displaced. Never download
or silently substitute a checkpoint. The [provenance record](setup-evidence/mlx-qwen/provenance.json)
lists exact file hashes and installed versions.

```sh
snapshot="$HOME/.cache/huggingface/hub/models--mlx-community--Qwen3.5-9B-MLX-4bit/snapshots/938d8919941c6e7efd3c7150eff7fe9d12afa631"
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 TOKENIZERS_PARALLELISM=false PYTHONDONTWRITEBYTECODE=1 \
  iteration-lab/.venv/bin/mlx_lm.server --model "$snapshot" --host 127.0.0.1 --port 18601 \
  --temp 0.2 --max-tokens 1024 --chat-template-args '{"enable_thinking":false}' \
  --decode-concurrency 1 --prompt-concurrency 1 --prefill-step-size 256 \
  --prompt-cache-size 1 --prompt-cache-bytes 268435456
```

Start it in a persistent session. Do not start a second instance if the
dedicated matching listener is already present. Then run:

```sh
./minecraft-verification/mc.sh preflight --prepared minecraft-verification/prepared-lan-v6-qwen --port 61196
```

The [frozen transport and parser](prepared-lan-v6-qwen/source/model.mjs) send
the snapshot path to local `/v1/chat/completions`, seed 701, temperature 0.2,
maximum 1,024 generated tokens, thinking disabled. It parses only a single
JSON tool object from assistant final content; reason is optional, all tool
and argument checks remain strict. No extraction from reasoning or prose.
Five consecutive structural invalids stop an arm. Preserve raw usage and
responses. The old checkout's Andy/Mindcraft chat syntax is not this contract.

## Calibration, pilot and scripted controls

The [actual v5 calibration](runs/calibration-20261108-lan-v5-01/) passed
12/12 methods and independently confirmed a production dispenser delivery
with zero model calls. The [v6 qualification record](prepared-lan-v6-qwen/qualification.json)
proves the action executor, pack, libraries, fixtures, schedule and context
remained unchanged; it explicitly says calibration was **reused, not rerun**.
A fresh deterministic calibration uses `mc.sh calibrate --port 61196 --auto-arm
--prepared minecraft-verification/prepared-lan-v6-qwen --out NEW_CALIBRATION_DIR`.

The pilot launcher did the following, once each: no_gate, prompt_only,
enforced; `--port 61196 --auto-arm --prepared minecraft-verification/prepared-lan-v6-qwen
--library minecraft-verification/prepared-lan-v6-qwen/library-mixed.json
--model mlx-community/Qwen3.5-9B-MLX-4bit --seed 701`, unique output under
`runs/prepared-lan-v6-qwen-mixed-r1-ARM/`. The [launcher](setup-evidence/launch-mlx-pilot.py)
requires qualification and refuses to overwrite any arm; the actual pilot is
not a command to rerun on top of its evidence. A genuinely new replication
must use a newly frozen, separately qualified ID and preserve original
results. The original pilot stopped after this triple. Later development used the distinct versioned protocols above.

The model cannot move test output into production. At each start the runner
checks stock and enclosing geometry from the live game. After each craft
application and each final receipt/delivery it checks fresh server windows;
the server returns actual slot contents. The observer checks run outside the
active interval after both clients leave, reconnect read-only and never alter
stock or repair a furnace. The no_gate terminal main run had a final server
chest read plus a post-terminal furnace read. The other two arms additionally
have independent post-terminal chest reads. Keep discrepancies, if any.

Read-only audit/report commands:

```sh
python3 minecraft-verification/setup-evidence/report-matched.py minecraft-verification/prepared-lan-v6-qwen minecraft-verification/runs --pilot
python3 minecraft-verification/setup-evidence/audit-run.py minecraft-verification/runs/prepared-lan-v6-qwen-mixed-r1-ARM
../minecraft-demo/.local/node22/bin/node minecraft-verification/setup-evidence/revision-audit.cjs minecraft-verification/runs/prepared-lan-v6-qwen-mixed-r1-ARM
```

Replace `ARM` with an actual completed arm. Revision requests, hash-changing
revisions and target-producing repairs are different counts. All coal loads
and additional test material kits count; transfers are not equivalent to burn.

The separately [frozen scripted control](setup-evidence/qualification-v1/)
has no model calls. Its output belongs outside `runs/`: after all three
audited terminals and post-terminal observations, use the cached Node to run
`minecraft-verification/setup-evidence/qualification-v1/run.mjs NEW_OUTPUT_DIR
61196`. Treat lifecycle, negative/fault, and calibration evidence as scripted.
Never score or pool those receipts or deliveries as Qwen outcomes.

## Historical attempts

The original `prepared/` defaults, older player names, per-episode manual
arming instructions, and Andy/Ollama launcher from earlier drafts are
[historical](setup-evidence/historical-docs/). Early v2 calibration hit a
missing terrain-ready acknowledgement; v3 reached 8/12 on preliminary
instrumentation; v4 was prepared but not loaded; v5 passed the live checks.
The Andy mixed no_gate attempt stopped after seven non-JSON responses and
zero game actions. Prompt-only/enforced Andy arms never started. The local
interface probes and [interruption](runs/prepared-lan-v5-mixed-r1-no_gate/interruption.json)
remain visible and separate from the Qwen block.
