# Reproducing the artifact

## Read-only validation

Use the README commands for the standalone Python tests, seven-episode evidence checks, offline Minecraft tests and preflight. `portable/test-minecraft.mjs` copies the unchanged archived test modules into a disposable layout and supplies the installed dependency root. It does not modify the historical executable sources or their hashes. The new npm lock pins a portable installation; it is not asserted to be the original author's complete package lock.

The frozen source hash is SHA-256 of `JSON.stringify` of the relevant value (including source text), as implemented in each version's `protocol.mjs`; it is not always the raw file-byte SHA-256. The publication export manifest separately uses ordinary SHA-256 over original and published file bytes. UTF-8 evidence containing author-local home paths is published with `$AUTHOR_HOME` redactions; source snapshot `.mjs` bytes were not altered. Original and published hashes are both retained. No new episodes were run to publish this artifact.

## Standalone Python evaluation

The two unit tests exercise all 13 permission cases and the exact/altered verdict fixture. To repeat the supplement's latency study without overwriting archived output, copy `python/supplement/` into a new working directory and run `python3 evaluate.py` there. This launches the predetermined metric fixture, not training. Report newly measured timing separately from the archived results.

`python/evaluation/evaluate_verifier.py` requires a full historical Efferents installation. The included `python/framework-excerpts/` files are from compatible revision `c24a6c8403166bbceb28c30080a8d016541285ae`; they are inspection excerpts, not a complete installable checkout. The original evaluator JSON did not record a framework commit, so the excerpt identity does not prove that exact revision produced the archived numbers.

## Live Minecraft prerequisites

1. Independently install Minecraft Java **1.21.6** and use a dedicated world with commands enabled. Open it to LAN and record the current port. The host datapack creates production and isolated-test sandboxes and resets their contents; use a dedicated world.
2. Install Node.js **22+**, then `npm ci --prefix dependencies --ignore-scripts`. Direct versions are Mineflayer 4.33.0, minecraft-data 3.119.0 and vec3 0.1.10. The package root is named `dependencies/`; no Mindcraft service, sibling checkout or provider API credential is required.
3. On a compatible Apple Silicon host, install `mlx-lm` and independently cache `mlx-community/Qwen3.5-9B-MLX-4bit`, revision `938d8919941c6e7efd3c7150eff7fe9d12afa631`. The historical adapter expects the Hugging Face snapshot under the current user's home cache. Serve only on `127.0.0.1:18601`, with temperature 0.2, maximum 1024 output tokens, thinking disabled and one decoding worker. The exact original package provenance is in `minecraft-verification/setup-evidence/mlx-qwen/provenance.json`. No checkpoint, game jar or model server is included here.

For example, after caching the model, a dedicated local server can be started with:

```sh
snapshot="$HOME/.cache/huggingface/hub/models--mlx-community--Qwen3.5-9B-MLX-4bit/snapshots/938d8919941c6e7efd3c7150eff7fe9d12afa631"
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 \
  mlx_lm.server --model "$snapshot" --host 127.0.0.1 --port 18601 \
  --temp 0.2 --max-tokens 1024 --chat-template-args '{"enable_thinking":false}' \
  --decode-concurrency 1 --prompt-concurrency 1 --prefill-step-size 256 \
  --prompt-cache-size 1 --prompt-cache-bytes 268435456
```

Use a free port for the dedicated matching endpoint and do not displace another process. The adapter's endpoint is frozen; changes require a newly frozen version, not edits to the archived protocol.

## Operator sequence

The portability wrapper supplies `--mindcraft` as a dependency-root argument; the historical name does not require Mindcraft. It also supplies the selected prepared directory. Supported versions are `v6`, `v7.1`, `v7.2` and `v7.3`.

```sh
# Offline only: no connection or inference.
node portable/minecraft.mjs v7.3 preflight --offline

# Install only into a confirmed dedicated world. Refuses an existing pack.
node portable/minecraft.mjs v7.3 install --world /absolute/path/to/dedicated-world
```

Enter `/reload` in Minecraft once after installing, or `/datapack enable "file/efferents-verification"` if the preserved pack was disabled. Observe the armed announcement. Subsequent fresh episodes use automatic arming. Supply your current LAN port in place of `PORT`:

```sh
node portable/minecraft.mjs v7.3 preflight --port PORT
node portable/minecraft.mjs v7.3 calibrate --port PORT --auto-arm \
  --out local-runs/new-calibration
```

Review calibration and server-backed controls before any agent episode. Do not count calibration/test deliveries as agent production results. For an independently qualified fresh replication of the final enforced development configuration:

```sh
node portable/minecraft.mjs v7.3 episode --arm enforced --port PORT --auto-arm \
  --library minecraft-verification/prepared-followup-v7.3/library-mixed.json \
  --model mlx-community/Qwen3.5-9B-MLX-4bit --seed 711 \
  --out local-runs/new-enforced-replication
```

The CLI command is `episode` in the archived implementation. It refuses to overwrite an output directory. The original operator log in `minecraft-verification/OPERATOR.md` describes the measured host and previous qualification; its paths, port and old qualification do not establish readiness on another machine. Preserve each new attempt and report changes in machine, interface, code, inputs or qualification. Do not call the v7.2 prompt-only and v7.3 enforced successes a matched comparison.

After experiments, disarm and disable only this pack through Minecraft commands. Keep model and bot shutdown separate from the user's host world. The research planner never receives privileged chat or arbitrary-code tools.

## Paper and figures

Compile `paper/main.tex` with its local bibliography and NeurIPS style using a standard LaTeX installation or upload the `paper/` source files to Overleaf. The checked-in `paper/paper.pdf` is the accompanying camera-ready revision. Editable figure generators are in `paper/figure-sources/`; Figure 1 is vector artwork. Figure 2's generator extracts its small set of item illustrations from the user's independently installed Minecraft jar. It does not need a Minecraft world or model run. Raw game assets are not bundled.
