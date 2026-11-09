# Codex operation guide — user supplies the LAN port

**Current dedicated LAN session:** use the selected frozen pack with both
`--prepared <directory>` and `--auto-arm`. It rearms only between producer
connections. At a clean setup boundary the separately controlled replay
observer may issue the single authorized `/reload` using existing LAN
permissions. Log the actual issuer and time; do not impersonate the owner,
change grants, or expose setup commands to the model. The manual owner-UI
workflow below is the fallback for packs without automatic arming.


The user starts a dedicated Minecraft Java 1.21.6 world, enables commands,
opens it to LAN, and supplies its port. That authorizes local setup, calibration,
and the matched comparison. Do not ask them to launch bots, start Ollama, run
shell commands, install the datapack, type `/reload`, or arm individual episodes.
Do not start a connection or experiment before they provide the port and ask
to proceed. Only the guide is being prepared in the current turn.

## Resolve the live world and prepare

Working directory:
`$AUTHOR_HOME/Documents/efferents/efferents research`.

1. Find the Java process listening on the supplied LAN port using `lsof`.
   Inspect that process's open `session.lock` file to identify the world.
   Confirm it contains `level.dat`. The conventional saves directory is
   `~/Library/Application Support/minecraft/saves/`, but launcher profiles may
   use another game directory. Do not select a world merely because its files
   have the latest timestamp. If necessary, inspect the active Minecraft owner
   UI to resolve the world. Ask for its identity only if evidence cannot resolve
   ambiguity; do not modify an unrelated save.
2. Check the actual game version. This protocol is pinned to 1.21.6. If it is
   incompatible, explain what needs changing; do not quietly alter the protocol.
3. Check offline tests and frozen source digests. Use a new prepared directory
   if source has changed, retaining the old one. Pass the selected `--prepared`
   directory consistently to all commands.
4. Install into the confirmed dedicated world:

   ```sh
   ./minecraft-verification/mc.sh install --world ACTUAL_WORLD_DIRECTORY
   ```

   The CLI refuses to overwrite an existing pack. If an identical experiment
   pack is already installed, reuse it. If replacement is necessary, first
   archive only this experiment's existing pack outside the world's datapacks
   directory, record its digest/location, then install the frozen replacement.
   Preserve other datapacks and user files.
5. Use the native computer-use tool to select the actual Minecraft application.
   Follow that tool's returned documentation. Enter `/reload` through the
   world owner's chat interface and inspect feedback. Enable the installed
   datapack if Minecraft lists it as available but disabled. Do not use a bot
   with operator privileges as a shortcut. Leave the game unpaused afterward.

## Local inference and preflight

Start the existing local Ollama service if needed; do not launch normal
Mindcraft profiles. The initial model is
`sweaterdog/andy-4:micro-q8_0`. Check local installed model names without
inference. If a replacement model is necessary, freeze that choice before
the comparison and use it in every arm; retain the original configuration.
No cloud provider calls or new model downloads are implied by this setup.

```sh
./minecraft-verification/mc.sh preflight --port ACTUAL_PORT
```

This tests local dependencies, LAN TCP connectivity and the installed model
listing. It does not join bots or test actual crafting.

## Calibration — Codex handles the interactive prompt

Launch in a persistent PTY so Codex can supply stdin after arming:

```sh
./minecraft-verification/mc.sh calibrate --port ACTUAL_PORT \
  --out minecraft-verification/runs/UNIQUE_CALIBRATION_ID
```

The runner creates **ProfessorPickaxe** and **InspectorIngot** automatically.
When its terminal says both have joined and asks for arming:

1. Through the native Minecraft owner UI, enter `/function efferents:arm`.
2. Inspect feedback confirming the function ran. Do not arm on an error.
3. Leave Minecraft unpaused, then send a newline to the runner's PTY using
   the process stdin tool. The user need not type anything.
4. Monitor output and persisted events. Maintain concise chat updates while
   long smelting operations run. Never reinterpret an incomplete operation
   or a missing result as success.
5. Require `calibration_passed` and 12 verified reference procedures before
   launching agent episodes. If calibration fails, preserve the run, diagnose
   the adapter/setup issue, and freeze any changes before rerunning. No silent
   fallback or replacement result.

Calibration makes no LLM inference calls and is not pooled with agent results.

## Matched comparison

Use the same frozen library, model, seed and budget in every arm. Start with
the first mixed-library triple at seed 701, rotating later repetitions as
specified in `prepared/schedule.json`. Use unique output directories:

```sh
./minecraft-verification/mc.sh episode --port ACTUAL_PORT --arm ARM \
  --library minecraft-verification/prepared/library-mixed.json --seed 701 \
  --out minecraft-verification/runs/UNIQUE_EPISODE_ID
```

Replace `ARM` with `no_gate`, `prompt_only`, or `enforced`. If a different
prepared directory is selected, update the library path too. For each new
episode, wait for both bots, arm through the owner UI, and send stdin yourself
as above. Do not issue setup/reset commands during an active episode.

Evaluate the first triple's instrumentation before expanding to the full
18-episode schedule. Include clean-library episodes to measure false blocks.
Keep infrastructure failures, partial episodes and interrupted runs visible.
Do not change models, budgets, prompts or source code within a matched block
and then attribute the difference solely to verification.

After finishing or stopping, close runner/bot connections and enter
`/function efferents:disarm` through the owner UI to release forced chunks.
Generate the comparison table with `mc.sh summarize`; include calibration
status, task completion, unverified dependency use, actions, test material kits,
tokens and total time. Do not claim net savings without accounting for tests.

## If owner UI automation is unavailable

The port alone does not grant permission to execute privileged Minecraft
commands over the game protocol. Do not fake successful setup or grant operator
status to research agents. Report the actual tool/access failure and the minimum
owner action required. Under normal desktop access Codex performs those actions;
they are not part of the user's expected checklist.
