# TURION — Session Log

Log of every Claude Code working session on this project: date, time, what was discussed/done, and what's next. Newest entry on top.

---

## 2026-09-01, ~23:35–23:51 (continuing into overnight, unattended by user)

**Session:** Wired the trained wake-word model into TURION's main loop
- Brief detour first: user asked several questions about whether voice could control the whole laptop/other tools (via Claude Code directly, or via TURION+Claude API tools) — clarified Claude Code itself has no general desktop mouse/keyboard control (only within the Browser pane), and that full device/tool control for TURION is Phase 5 territory, best done as local rule-based command routing for simple actions (to save API tokens) with Claude reserved for genuinely conversational requests — consistent with the project's existing "local-first, paid API only for reasoning" principle. Documented as context but not started.
- User asked Claude to proceed with wake-word integration overnight while they slept, to test in the morning — found the downloaded model files in `Downloads\`, moved them into the repo at `turion/wake_word/models/`
- Installed `openwakeword` in the main project's `.venv` (Python 3.14) — installed cleanly with no compatibility issues, confirming the earlier Colab pain was almost entirely from *training*-specific dependencies, not openWakeWord's own lightweight runtime (onnxruntime + scipy + scikit-learn)
- Hit and fixed two small setup issues: the pip package doesn't bundle its required preprocessing models (melspectrogram/embedding — fixed via `openwakeword.utils.download_models()`), and the repo's `.gitignore` had a broad `models/` rule that was silently excluding the small trained wake-word model too (added a negation exception)
- Wrote `turion/wake_word/listen.py` (model preload + continuous-listening `wait_for_wake_word()`) and updated `turion/main.py` to replace `input("Press Enter to talk...")` with it — verified the whole thing imports and preloads without error, but **has not been tested against a real spoken "Hi Sisu"** — that needs the builder's own voice, first thing tomorrow
- Documented everything in `project_info.md`/`project_status.md`, including the known unknowns (whether the 0.5 detection threshold is well-tuned; the model was trained with only 100 examples, well below openWakeWord's recommended 1,000+, so retraining with more examples is the fallback if live detection quality disappoints)

**Next session should start with:** Run `turion/main.py` (or the Desktop shortcut) and say "Hi Sisu" out loud — confirm it actually triggers, and judge whether the sensitivity needs tuning. If it works, Phase 2 (Vision) is next.

---

## 2026-09-01, ~20:58–23:32

**Session:** Built a double-click launcher, added conversation logging, then trained a custom wake word ("Hi Sisu") through a long dependency-debugging marathon
- Added `run_turion.bat` + a Desktop shortcut so the builder doesn't need to manually open PowerShell/cd/type the run command each time
- Added `turion/conversation_log.py` — every turn (transcribed user text + Claude's reply) now appends to `logs/conversations.jsonl` (gitignored, personal content) so past conversations are reviewable later
- Builder asked for TURION to be always-on with a spoken wake phrase instead of "press Enter to talk". Researched wake-word engines: **Picovoice Porcupine's free tier for custom wake words was permanently discontinued 2026-06-30** ("no non-commercial tier planned") — ruled out immediately, not a close call. **openWakeWord** (fully free, open-source, runs 15-20 models simultaneously on a Raspberry Pi 3 core) was the clear remaining choice.
- Worked through picking the actual wake phrase with the builder — tried "TURION" itself first (pronunciation issues with "gy"-type sounds collapsing into "j" in the English-phoneme synthetic training pipeline meant candidates like "Gyanu" didn't work cleanly), considered Sisu (Finnish, meaning resilience/grit) vs. Gyanu (Sanskrit-rooted, meaning knowledge, but too close to a common Indian nickname — higher false-trigger risk) vs. a few Sanskrit alternatives (Dhriti, Chetana). **Landed on "Hi Sisu"** — clean pronunciation, "Hi" prefix reduces false-trigger risk like "Hey Siri" does. TURION stays the assistant's name; this is only the activation trigger.
- **Trained the model via openWakeWord's official Colab notebook** — meant to be a <1-hour, no-code process, but the notebook (last maintained ~April 2026) had drifted badly out of sync with Colab's current Python 3.13 environment. Walked through the Colab UI screenshot-by-screenshot (same pattern as the Anthropic Console and Windows settings work earlier) and fixed, in sequence: a PyPI package (`piper-phonemize-cross`) that no longer exists at all (swapped for the maintained fork `piper-phonemize-fix`); an unnecessary torchvision pin with no matching wheel; a stale-partial-install guard that kept skipping reinstall after failed attempts (needed explicit `rm -rf` between retries); `torch.load()`'s new `weights_only=True` default breaking two different old-format checkpoints in two unrelated packages; `pkgutil.ImpImporter` being removed in Python 3.12+ breaking `webrtcvad`'s `pkg_resources` import chain (monkey-patched); the system `pkg_resources` itself being fundamentally incompatible with Python 3.13 (worked around by patching `webrtcvad.py` to stop importing it entirely, since it was only used for a version string); and two separate `torchaudio` APIs (`set_audio_backend`, `info`) removed in the current torchaudio version, patched out of `torch_audiomentations`'s IO module (the second one replaced with an equivalent `soundfile.info()` call).
- **Training succeeded** — confirmed live via progress bar (`Training: 21% 2132/10000 [01:04<03:10, 41.35it/s]`). Final model downloaded: `hi_si_su.onnx` + `hi_si_su.tflite`, ~200KB each — confirms wake-word models are genuinely tiny regardless of the huge (~16GB) training data, which stays on Colab and isn't needed on the robot.
- User asked whether Claude could work through the night on the remaining integration work (mirroring the earlier Indic-TTS overnight session) — confirmed yes for the code/install/setup portions (installing `openwakeword` in the main `.venv`, writing the always-listening loop) but the live "does it actually trigger on my voice" test needs the builder specifically. Documented everything in `project_info.md`/`project_status.md` before deciding how to proceed with that overnight work.

**Next session should start with:** Integrate the trained wake-word model into `turion/main.py` (install `openwakeword`, replace "press Enter to talk" with continuous listening + wake-word trigger), then validate live with the builder's voice. After that, Phase 2 (Vision) is the next open item.

---

## 2026-09-01, ~20:15–20:44

**Session:** Funded the Claude API and ran TURION's first real conversation — Phase 1 complete
- Helped diagnose an unrelated Windows annoyance first: a "tick" sound on every physical keypress, turned out to be Ease of Access → Keyboard → Filter Keys accidentally enabled (likely from holding right Shift for 8s) with "Beep when keys are pressed" checked — found via Volume Mixer (showed "System Sounds" as the source, ruling out Sound Scheme and third-party apps) then checking each Ease of Access toggle in turn. Fixed.
- Confirmed a debit card works for Anthropic Console billing (needs international/online payments enabled; USD; Visa/Mastercard safer than RuPay) and estimated $5 lasts roughly 1-2+ months at the builder's usage level on Haiku 4.5 (`shared/claude-api` skill pricing table)
- Walked through funding Anthropic Console: card had defaulted to a $20 purchase (not the intended $5) plus 18% Indian GST added at checkout — both normal, not errors. Guided creating the first API key (renamed from the default "bro-onboarding-api-key" to "TURION")
- User saved the raw key to `D:\TURION_ROBO\chavi\Cloude_API_KEY.txt` — **inside the git repo**. Caught this before any commit; added `chavi/` to `.gitignore` (user wanted to keep the local backup rather than delete it) so it can never be accidentally pushed
- Set `ANTHROPIC_API_KEY` via `setx`, verified it works with a direct test call through `turion.brain.claude_client`
- Added per-step module visibility to `main.py`/`speak.py` console output at the user's request (e.g. `Thinking... (module: Claude API, model: claude-haiku-4-5-20251001)`, `(module) TTS: Piper [mr] -> "..."`) — answers "how do I know which module is running" directly in the running output rather than requiring code-reading
- **User ran `turion/main.py` themselves and had TURION's first real conversation** — full pipeline confirmed working live: mic → IndicConformer STT → Claude Haiku 4.5 → Piper TTS
- User reported the reply's audio sounded choppy ("तुटक") with the voice switching between a male and female speaker mid-sentence — traced to the script-splitting design in `speak.py` (each language switch was a separate audio clip with an audible gap, and pyttsx3's male English voice was alternating with Piper's female Marathi voice). **Removed script-splitting** — `speak()` now always uses one consistent voice for the whole reply (default Marathi Piper), accepting imperfect pronunciation of embedded English words in exchange for continuous, consistent audio. Deleted the now-dead `_split_by_script`/`_is_devanagari` helpers.
- Documented all of this in `project_info.md` and marked **Phase 1 fully complete** in `project_status.md`

**Next session should start with:** Phase 2 (Vision) — nothing is blocking anymore. Everything from here is new work: camera input, object/face detection, and eventually the person-identification capability captured this morning.

---

## 2026-09-01, ~07:00–08:49

**Session:** Reviewed overnight Indic-TTS results; settled the TTS/interpreter question; decided Phase 4 compute board (Jetson); captured a new person-ID vision
- Sent longer (~28s) Indic-TTS audio samples (male + female) since the overnight ones were too short (~2s) to judge — user found pronunciation less natural than Piper's Marathi voice, with a "Hindi touch" accent. Confirmed only 2 built-in speakers exist (no others), checked AI4Bharat's GitHub for a newer release (none — same 2023 "v1" as before) and for other AI4Bharat voice projects (IndicVoices/-R are datasets, not usable TTS models)
- Explained why the accent issue can't be fixed by "swapping the voice module" alone: FastPitch (the acoustic model) is what determines pronunciation, not HiFi-GAN (the vocoder) — a real fix needs either a different independently-trained model or fine-tuning, not a simple swap
- User asked about a one-time-purchase, fully local alternative to ElevenLabs (for privacy + no subscription) — found a couple of small Gumroad products but flagged them as unverified, Hindi-only (no Marathi), likely just repackaged XTTS v2; recommended against spending money on them
- **User revealed the actual motivation** behind wanting broad language coverage: a future "universal interpreter" capability — TURION asking any Indian person what language they speak and translating between people. Documented as a distinct future capability in `project_info.md`, not Phase 1 scope
- Re-checked Indic Parler-TTS specifically for a "one consistent voice across languages" fit: it supports 21 languages with 69 named speaker identities that stay consistent across all of them — exactly the requirement, already solved by the model. Only blocker is CPU speed (already measured: 34.2x real-time), which should stop mattering once this feature is built on GPU-capable hardware later
- User asked why not use mobile-phone-class hardware for the robot instead of a laptop-class board — explained the real blockers (no GPIO for motor control, Android doesn't run the existing PyTorch stack easily, no robotics ecosystem) and surfaced RK3588-based SBCs (Orange Pi 5 / Radxa Rock 5) as genuine middle ground (phone-class NPU, but Linux + GPIO)
- Published a comparison artifact (spec table + cost breakdown): **https://claude.ai/code/artifact/a3121061-7981-4c50-ac34-e8d5f9827f06** — Jetson Orin Nano vs Orange Pi 5/Rock 5, plus whole-Phase-4-robot cost estimates (Jetson build ₹28,500–48,500 vs Rockchip build ₹20,500–34,500)
- Talked through the tradeoff from a few angles (immediate need vs. future-proofing vs. cost) — **user decided on Jetson Orin Nano**, explicitly prioritizing avoiding future rework (can't code independently, so redoing an integration later costs more than the price gap now) over the project's usual "prototype cheap, expand later" default. Documented as a deliberate, reasoned exception in `project_info.md`
- User outlined a near-term plan: get the Claude API working first, then Phase 2 (camera/vision), then combine both into a person-identification capability (voice + face + object + human detection, culminating in recognizing owner/family members with persistent memory). Clarified "safety" for this means three things together: data privacy (biometric data stays local), access/security (know vs. unknown person), and avoiding misidentification (prefer "don't recognize" over a confident wrong guess). Documented under Phase 3 in `project_info.md`

**Next session should start with:** Fund the Claude API (min. $5) and run `turion/main.py` for TURION's first real conversation — still the only blocker on Phase 1 itself. Everything else discussed today is future-phase planning, captured in docs, not blocking.

---

## 2026-08-31, ~23:07–23:54 (overnight, unattended by user)

**Session:** Got AI4Bharat Indic-TTS working end-to-end for Marathi — a long debugging chain, but a real success
- User asked to go ahead with the Indic-TTS setup overnight rather than waiting until morning, explicitly confirming: (a) the session would stay open so work could continue, and (b) build it fully in parallel — never touch the working main project (`D:\TURION_ROBO\.venv`, Python 3.14). Confirmed both throughout.
- Recreated the isolated-Python-environment approach from the Parler-TTS experiment, but hit a new wall: `Trainer`'s setup.py has a **buggy version check** (`sys.version_info > (3, 11)` is `True` for any 3.11.x patch due to Python tuple comparison) that rejects 3.12 *and* 3.11 — actually needs exactly **3.10**. Set up portable Python 3.10 (embeddable zip + get-pip + virtualenv, same workaround as before since the real installer still fails on this machine) at `D:\indic_tts_env`.
- Cloned the two forked libraries Indic-TTS needs (`gokulkarthik/TTS`, `gokulkarthik/Trainer`) into `D:\indic_tts_src`.
- Hit and fixed, in order: missing C headers on the embeddable Python (fixed by pulling the official `python` NuGet package — a plain zip, no installer — and copying `include`/`libs` into the venv's actual expected location, `<venv>\Scripts\Include`/`libs`, which is non-standard for a venv built on an embeddable base); a broken old `pyworld==0.2.10` pin with no wheel (relaxed to `>=0.3.5`); a numpy/scipy/numba three-way version conflict (kept `numpy==1.21.6` for numba, pinned `scipy==1.7.3` and `soundfile==0.12.1` to match); an **import-order-dependent DLL crash** where importing `librosa`/`numba` before `torch` breaks torch's own DLL loading on Windows (worked around by writing a standalone script that imports `torch` first, then calls `TTS.utils.synthesizer.Synthesizer` directly instead of the buggy-order CLI entry point); a hardcoded bad `speakers_file` path in the downloaded checkpoint's `config.json` (edited it); and a Devanagari-to-console encoding crash (fixed with `PYTHONIOENCODING=utf-8`, same class of issue seen with PowerShell earlier this project).
- Downloaded the Marathi checkpoint (1.41GB) from GitHub Releases — hit "disk full" on D: again mid-extraction, moved everything to C: (which had more room) instead of re-doing the WSL cleanup.
- **It worked.** Generated Marathi audio with both bundled speakers ("male": 1.85x real-time, "female": 1.5x real-time) — far faster than Indic Parler-TTS's 34.2x, though slower than Piper's 0.16x. Same limitation as Piper: embedded English words (e.g. "TURION") aren't in the single-language vocabulary and get silently dropped.
- Sent both audio samples to the user to review in the morning. Documented the full fix chain in `project_info.md` (useful if Indic-TTS is ever revisited for a non-Piper language). Kept the working environment (unlike Parler-TTS's, which was deleted) since it took real effort and could be reused.
- **Not integrated into `speak.py`** — this was a feasibility test only; Piper stays the production Marathi/Hindi/English TTS. Disk space is tight again (D: ~2GB free) — flagged for a cleanup pass if it becomes a problem.

**Next session should start with:** Review the Indic-TTS audio samples and decide whether it's worth integrating anywhere, then — unrelated to this thread — fund the Claude API (min. $5) and run `turion/main.py` for TURION's first real conversation, still the only blocker on Phase 1 itself.

---

## 2026-08-31, ~22:52–23:04

**Session:** Discussion + research — building a custom Indian-language model (ruled out), broader TTS language coverage
- User asked what it would take to build a custom in-house speech model covering all Indian languages, from scratch. Explained honestly: this is what AI4Bharat itself already spent years and institutional funding building — realistically needs lakhs of hours of labeled audio, weeks of multi-GPU training, and ML-specialist engineers; a solo/hobby budget could not replicate it. Realistic alternative: fine-tune an existing open model for a specific need (days, ~₹5,000–50,000) rather than building from scratch.
- Explained what IndicConformer actually is (Conformer = CNN+Transformer hybrid architecture, AI4Bharat-trained, 600M params) since the user asked directly.
- Asked about faster alternatives to Piper for Indian languages — confirmed Piper's Marathi voice is a single package (9 speakers, all female — speaker 8 already chosen) with nothing new added since last check. Total Indian-language coverage in Piper is only 7 languages (hi, mr, bn, te, ml, ur, ne) — missing Tamil, Kannada, Gujarati, Punjabi, Odia, Assamese, Sanskrit, etc.
- Researched two candidates for broader coverage: **Meta MMS-TTS** (1,107 languages total, VITS-based so likely fast, untested) and **AI4Bharat's separate "Indic-TTS" project** (distinct from the already-tested Indic Parler-TTS — easy to confuse) — 13 Indian languages, FastPitch+HiFi-GAN architecture (lightweight/fast, unlike Parler-TTS's slow generative approach). This looks genuinely promising.
- User wants to test Indic-TTS tomorrow rather than tonight — documented the plan so it isn't lost. Setup will likely need another isolated Python environment (same pattern as the Parler-TTS experiment), est. 1-2 hours.

**Next session should start with:** Test AI4Bharat's Indic-TTS (13 Indian languages) for speed/quality. Then, unrelated to this thread: fund the Claude API (min. $5) and run `turion/main.py` for TURION's first real conversation — still the only blocker on Phase 1 itself.

---

## 2026-08-31, ~22:11–22:48

**Session:** Actually tested Indic Parler-TTS; found and fixed a disk-space crisis along the way
- User asked to go ahead and install Indic Parler-TTS in the isolated `D:\parler_tts_env` (Python 3.12) prepared last session
- Install succeeded cleanly (tokenizers built fine on 3.12, unlike 3.14)
- Hit a gated-repo error even with `HF_TOKEN` set — this model needs its own separate access grant on Hugging Face (per-model, not per-account); user accepted terms on the model page and it worked
- Hit "No space left on device" downloading the 3.75GB model file — **discovered C: drive had ~0GB free and D: only ~3GB**. Investigated: an unused WSL Ubuntu install was consuming ~20GB. User confirmed they don't use WSL; removed it (user ran `wsl --unregister Ubuntu` themselves — Claude's auto-mode classifier blocks running destructive commands like this directly). Freed C: to ~22GB, D: to ~4GB. This was a real, general problem worth having found regardless of the TTS experiment — likely also explains the earlier Python 3.12 MSI installer failures
- Re-ran the test successfully: voice quality was genuinely good, but **generation took 34.2x real-time** (~140s to produce 4s of Marathi audio) — confirms this model needs a GPU to be practical; not viable on this hardware. User agreed, staying with Piper.
- Cleaned up afterward: deleted `D:\parler_tts_env`, `C:\Python312_portable`, and the downloaded model caches (~4GB) — nothing from this experiment persists in the project or on disk
- Documented the full experiment outcome in `project_info.md` and `project_status.md`, including the disk-space finding as a standalone note (worth checking periodically going forward)

**Next session should start with:** Fund the Claude API (min. $5) and run `turion/main.py` for TURION's first real conversation — this remains the only blocker on Phase 1

---

## 2026-08-31, ~21:55–22:10

**Session:** Researched single-voice multilingual TTS options; set up a separate Python 3.12 environment for future experimentation
- User asked about getting one single voice that speaks Marathi/English/Hindi clearly, instead of the current 3-engine setup. Researched options: XTTS v2 (Coqui, free/local) supports Hindi but **not Marathi**; ElevenLabs (paid, cloud) is the only option that genuinely does all three fluently in one voice with native code-switching — checked pricing (~₹1,600–1,900/month for the Creator tier, likely needed for real daily use), but that's local/privacy principle broken plus a real recurring cost on top of the Claude API. User decided to keep the current Piper-based multi-voice setup rather than pay for ElevenLabs.
- User asked what it would take to get Indic Parler-TTS working (it supports Marathi natively) despite the earlier Python 3.14 incompatibility. Answer: a separate, older Python (3.11/3.12) environment, isolated from the main project to avoid risking the working `transformers` version STT depends on — estimated 3-6 hours with real risk it's still too slow on this CPU-only hardware even after all that setup.
- User asked to at least prepare the isolated environment now (keeping the current setup as primary) — set that up:
  - The standard Python 3.12 installer failed on this machine (MSI error 0x80070003 — registry access denied on `HKLM\...\Installer\Rollback\Scripts`, for both InstallAllUsers=0 and various target directories)
  - Worked around it using the portable/embeddable Python 3.12 distribution instead (no installer/MSI involved): extracted to `C:\Python312_portable`, enabled site-packages in `python312._pth`, bootstrapped pip via `get-pip.py`, installed `virtualenv`, created a venv at `D:\parler_tts_env`
  - This environment is intentionally outside `D:\TURION_ROBO` (not tracked by git, can't affect the main project) and currently empty (just pip) — installing/testing `parler-tts` itself is unstarted, for a future session

**Next session should start with:** Fund the Claude API (min. $5) and run `turion/main.py` for TURION's first real conversation. The Indic Parler-TTS experiment (`D:\parler_tts_env`) is separate, optional, unscheduled follow-up work.

---

## 2026-08-31, ~20:16–21:51

**Session:** Solved Marathi/Hindi TTS end-to-end; diagnosed and fixed perceived latency — Phase 1 is now fully built and validated except for API funding
- **Tried WinRT** (`Windows.Media.SpeechSynthesis`) to reach the Hindi OneCore voice: got voice enumeration and raw-PCM playback (via `sounddevice`, since `MediaPlayer` doesn't work reliably in a console script) working as a proof of concept. Tested it speaking Marathi text with the Hindi voice ("Hemant") — functional but not great pronunciation, as expected for Hindi-reading-Marathi.
- **Tried AI4Bharat Indic Parler-TTS** (native Marathi-trained, likely best quality) — blocked: its pinned `transformers<=4.46.1` needs `tokenizers<0.21`, which has no Python 3.14 wheel and fails to build from source (PyO3 doesn't support 3.14 yet). Would also have downgraded the working `transformers` used by STT. Install failed atomically (nothing got installed, confirmed clean). Abandoned.
- **Found Piper TTS** — lightweight, fast, ONNX-based, and (unlike the other two options) has a genuine **native Marathi voice** (`rhasspy/piper-voices`, trained on OpenSLR-64). Installed cleanly on Python 3.14 with no conflicts.
  - Downloaded and auditioned all 9 speakers of the Marathi voice — user picked **speaker 8** (female)
  - Also checked Hindi Piper voices (pratham, rohan — male; priyamvada — female) for a male-voice option; user picked **pratham**. Confirmed pratham's Marathi pronunciation is poor (it's Hindi-trained), so it's Hindi-only, not a Marathi substitute
  - Removed the now-unused WinRT packages
- Rewrote `turion/voice_output/speak.py`: routes by script — English via `pyttsx3`, Devanagari via Piper (Marathi by default, `lang="hi"` to force Hindi) — and **splits mixed-language text word-by-word** so a sentence like "मी TURION आहे" speaks each part in the right voice instead of the whole thing going through one engine
- User reported ~12-15s of perceived lag after speaking. Benchmarked each stage: STT model load ~35s / inference ~0.36x real-time; TTS model load ~5s / generation ~0.16x real-time — both fast once loaded. Added `preload()` to both `transcribe_indic.py` and `speak.py`, called at `main.py` startup, so the one-time load cost happens up front with a "Loading..." message instead of mid-conversation
  - Remaining ~8s turned out to be the stub reply's own spoken *length* (not overhead) — confirmed by timing a short realistic reply (~3.4s). Shortened the stub reply text accordingly
- Added `(debug)` per-stage timing prints to `main.py` (transcribe/think/speak) — useful for spotting future regressions
- Downloaded voice audition samples into `tests/marathi_voice_samples/` and sent them to the user directly for listening
- Updated `project_info.md` and `project_status.md` with the full TTS decision (including the two abandoned approaches and why) and the latency findings

**Next session should start with:** Fund the Claude API (min. $5) and run `turion/main.py` for TURION's first real conversation — nothing else is blocking Phase 1

---

## 2026-08-31, ~19:45–20:15

**Session:** USB mic research (deferred); Claude API blocked on funding — added STUB mode; found Marathi/Hindi TTS gap
- Researched dedicated USB mics for far-field (2 ft+) pickup in a noisy home — real far-field hardware (ReSpeaker USB Mic Array ~₹8,700, Anker PowerConf ~₹12,999) is expensive; recommended deferring this purchase until Phase 4 (robot build), where a mic array reused directly on the Raspberry Pi makes more sense than a laptop accessory
- User has no funds for Claude API right now. Checked Anthropic Console: no free trial credit is offered — a $5 minimum purchase is required even to generate an API key. Rather than block, added a **stub mode**: `claude_client.is_configured()` / `think()` return a labeled placeholder reply (echoing the heard text) when `ANTHROPIC_API_KEY` isn't set, instead of crashing. `main.py` now runs the full loop either way with zero code changes needed once a real key is added later
- Fixed `main.py` to use the validated Marathi/IndicConformer transcriber (it was still wired to the English Whisper one)
- Ran the full loop in stub mode successfully — confirmed working end-to-end (mic → Marathi STT → stub reply → TTS)
- **Found a new gap:** TTS can't speak Marathi/Hindi. Added a Hindi voice via Windows Settings, but it's a modern "OneCore" voice, invisible to `pyttsx3`/classic SAPI (confirmed via direct `win32com` SAPI query — only sees English David/Zira). Needs a WinRT-based rewrite of `speak.py` to use it; deliberately deferred until after the API is funded. Confirmed with user that daily use will be mostly Marathi, regularly English, occasionally Hindi — documented as a language-profile decision in `project_info.md`
- Updated `project_info.md` and `project_status.md` with all of the above

**Next session should start with:** Once Claude API has funding — set `ANTHROPIC_API_KEY` and run `turion/main.py` for a real end-to-end conversation

---

## 2026-08-31, ~19:25–19:42

**Session:** Root-caused Marathi STT accuracy/reliability issue — Bluetooth earbuds mic
- User asked how to push accuracy further; discussed options (audio normalization, shorter/realistic utterances, Claude compensating for minor STT errors via context, external USB mic) but before implementing any, user mentioned they were using Bluetooth earbuds (realme Buds Air7 Pro) during all testing
- This explained both open mysteries at once: the occasional near-silent recordings (Bluetooth call-mode/HFP mic audio is compressed/narrowband and less reliable to capture) and some of the accuracy gaps
- Walked through fixing it: Windows lets input and output audio devices be set independently (Settings → System → Sound) — set Input explicitly to the built-in Realtek mic while leaving Output on the Bluetooth earbuds, so the user can still listen privately without hurting mic input quality
- Even after that, Windows' own mic test showed no signal at all (volume was already 100%) — a restart fixed it (audio driver had gotten stuck)
- Re-tested with the built-in mic post-restart: a 10-digit spoken phone number came back **100% correct** — confirmed real accuracy is much better than earlier sessions suggested once the right mic is used
- Documented the finding in `project_info.md` / `project_status.md`: always use the built-in mic for TURION input, Bluetooth only for output if needed
- User asked how this mic situation will be handled once TURION moves into an actual robot — explained that Phase 4+ hardware will have its own dedicated, hardwired mic (not a shared/Bluetooth-paired device like a laptop), so this class of problem is specific to the Phase 1 laptop-prototyping setup; a dedicated USB mic now would give the same "always-consistent-device" benefit early

**Next session should start with:** Set `ANTHROPIC_API_KEY` and run the full Phase 1 loop (`turion/main.py`) end-to-end, using the built-in mic (not Bluetooth)

---

## 2026-08-31, ~17:40–19:21

**Session:** Full input/output validation — TTS fixed and confirmed clear; Marathi STT validated with live speech
- **TTS bug found and fixed:** pyttsx3's cached engine dropped/clipped audio on repeated use (Windows SAPI5 quirk — reusing one engine across multiple say()/runAndWait() calls is unreliable). Fixed by creating a fresh engine per `speak()` call. User confirmed audio is now clear.
- **Marathi STT (IndicConformer) got working end-to-end:**
  - Hit a gated Hugging Face repo (401 error) — walked user through creating an HF account, accepting the model's terms, generating a read-only access token, and setting it as `HF_TOKEN` (user handled the token themselves, as with the Anthropic key)
  - Hit a missing `onnxruntime` dependency after that — installed `onnx` + `onnxruntime`
  - Hit intermittent near-silent recordings (peak ~0.001) a few times during testing — tried explicitly pinning the mic to the Realtek device by name, which made it *worse* (picked a non-working duplicate device entry); reverted to relying on Windows' own default-device selection, which is more reliable. Root cause of the occasional silence still unclear; retry-on-failure is the current mitigation.
  - Switched decoding from CTC to **RNNT** — clearly more accurate in side-by-side testing
  - Ran two custom test scripts (`tests/marathi_test_script.txt` — daily-use sentences, `tests/marathi_test_script_hard.txt` — long/technical/number-heavy sentences) multiple times via `tests/test_stt_indic_manual.py` (which now also writes output to `tests/last_transcription.txt`, since PowerShell's console font can't render Devanagari — Claude reads the file directly instead of relying on the terminal)
  - **Verdict:** strong on common vocabulary and even long, complex ordinary sentences (often perfect); weaker on technical/uncommon words and occasionally drops a word/clause near the end of longer utterances. Judged good enough for daily-use voice commands — full findings in `project_info.md`
- Updated `Doc/project_status.md` and `Doc/project_info.md` with all findings above

**Next session should start with:** Set `ANTHROPIC_API_KEY` and run the full Phase 1 loop (`turion/main.py`) end-to-end for the first time

---

## 2026-08-31, ~12:00–12:03

**Session:** TTS tested; error handling added (user away from mic, so no live audio testing this session)
- Tested TTS (`turion/voice_output/speak.py`) — runs cleanly. Checked installed Windows voices: only English (Microsoft David, Zira) — no Marathi voice on this machine, so spoken replies will always be in an English voice/accent regardless of reply language
- Confirmed `ANTHROPIC_API_KEY` is still not set (checked existence only, never the value)
- Added error handling to `turion/main.py` / `turion/brain/claude_client.py`:
  - Missing API key now fails fast at startup with a clear message, instead of failing confusingly mid-conversation (discovered the `anthropic` SDK doesn't validate the key at client construction — added an explicit env-var check in `claude_client.get_client()`)
  - Mic errors (`sounddevice.PortAudioError`) and Claude API errors (`anthropic.APIError`) are now caught per-turn in the main loop so one bad turn doesn't crash the whole assistant
- Verified all `turion/` modules import cleanly

**Next session should start with:** Set `ANTHROPIC_API_KEY`, then do a live mic test of `tests/test_stt_indic_manual.py` (Marathi) and `turion/main.py` (full loop)

---

## 2026-08-30, ~20:52–22:29

**Session:** GitHub backup set up; Phase 1 scaffolded; mic input + STT built and debugged
- Set up local git repo + GitHub backup (private repo: https://github.com/TuRaing/TURION_ROBO), agreed on push policy (always ask before `git push`, never auto-push — session runs indefinitely so there's no natural end-of-session trigger)
- Scaffolded repo structure: `turion/` Python package (audio, voice_output, brain, vision, memory, hardware modules) + `firmware/` placeholder for Phase 4 microcontroller code; documented the Python/C++ language split in `project_info.md`
- Installed Phase 1 dependencies (torch, openai-whisper, sounddevice, anthropic, pyttsx3) — all compatible with Python 3.14 on this machine
- Built and debugged the mic → STT pipeline end-to-end:
  - Diagnosed and fixed a Windows mic input-volume issue (was near 0, boosted to 100 in Windows Sound settings)
  - Fixed Whisper hallucinating text over trailing silence by replacing fixed-duration recording with `record_until_silence()` — auto-stops after a pause, with ambient noise calibration at the start of each recording so the silence threshold adapts to mic gain/room noise instead of using one fixed number
  - Added `initial_prompt` hint so Whisper reliably recognizes "TURION" as a name
  - English STT via Whisper (`small` model) now working accurately
  - Marathi STT via Whisper was poor (small model, low-resource language) — decided to add AI4Bharat's **IndicConformer** (`ai4bharat/indic-conformer-600m-multilingual`) as a second, Marathi-specialized local STT engine (see `project_info.md` for the decision and why paid cloud STT — Google/Azure, checked current pricing — was ruled out in favor of local/free for privacy)
  - Installed `transformers` + `torchaudio`; wrote `turion/audio/transcribe_indic.py` and `tests/test_stt_indic_manual.py` — **not yet tested against real Marathi speech**
- Confirmed this laptop has no usable GPU (Intel integrated + an old AMD Radeon HD 8670M with no CUDA/ROCm support) — all STT inference is CPU-only, which caps how large a model is practical

**Next session should start with:** Run `tests/test_stt_indic_manual.py` to validate IndicConformer's Marathi accuracy; then connect Claude API (needs `ANTHROPIC_API_KEY` set) and test TTS, to get the full Phase 1 loop working end-to-end

---

## 2026-08-30, ~20:41–20:52

**Session:** Project setup / tracking docs created
- Reviewed `Doc/project_info.md` (full TURION project overview — phases, guiding principles, cost summary, business considerations)
- Created `Doc/session_log.md` (this file) and `Doc/project_status.md` (status + checklist) to track progress across sessions
- No code written yet — Phase 1 (Voice Assistant) has not been started

**Next session should start with:** Begin Phase 1 setup — mic input + Whisper STT

---

<!-- Add new entries above this line, newest first. One file for all dates (not one file per date) — easier to scan chronologically. Suggested format:

## YYYY-MM-DD, HH:MM–HH:MM

**Session:** short title
- What was done
- Decisions made
- Blockers/questions

**Next session should start with:** ...
-->
