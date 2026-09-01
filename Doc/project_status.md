# TURION — Project Status

Last updated: 2026-09-01, 23:51

## Current Phase
**Phase 1 — Voice Assistant (Software Only) — COMPLETE.** *Claude API funded and confirmed working 2026-09-01; TURION had its first real end-to-end conversation (mic → IndicConformer STT → Claude Haiku 4.5 → Piper TTS). Both STT and TTS models preload at startup so per-turn latency is low. Console now labels which module handles each step (STT/Claude/TTS engine) so it's visible while running.*

**Wake-word activation ("Hi Sisu") — integrated, awaiting live voice test.** Custom model trained via openWakeWord, installed into the main project, and wired into `main.py` (`input("Press Enter...")` replaced with continuous listening via `turion/wake_word/listen.py`). Everything verified structurally (imports, model loading, preload) but **not yet tested against the builder's actual voice** — that's the next thing to check, first thing. Full details in `project_info.md`.

## Phase Overview

| Phase | Description | Status |
|---|---|---|
| 1 | Voice Assistant (listen → transcribe → think → speak) | ✅ Done |
| 2 | Vision (object/face detection) | 🔲 Not started |
| 3 | Memory / Personalization | 🔲 Not started |
| 4 | Physical Robot Arm | 🔲 Not started |
| 5 | Proactive Behavior & Device Control | 🔲 Not started |
| 6 | Bipedal Humanoid (long-term, aspirational) | 🔲 Not started |

Legend: 🔲 Not started · 🟡 In progress · ✅ Done

---

## Checklist — Phase 1 (Voice Assistant)

- [x] Set up dev environment (Python 3.14, `.venv`, dependencies)
- [x] Mic input working (auto-stop on silence, noise-level calibrated per recording)
- [x] Speech-to-Text integrated — English, via Whisper `small` (accurate)
- [x] Speech-to-Text — Marathi, via AI4Bharat IndicConformer, RNNT decoding — validated with live speech across easy and hard test scripts. Good on common vocabulary and even long/complex ordinary sentences (sometimes perfect); weaker on technical/uncommon words and occasionally drops a word/clause, especially near the end of longer utterances. Good enough for daily-use voice commands.
- [x] Claude API connected — funded 2026-09-01 ($5 via Anthropic Console, debit card, Indian GST applied). Key stored as a permanent `ANTHROPIC_API_KEY` environment variable (`setx`); a plaintext backup copy the builder kept at `D:\TURION_ROBO\chavi\` is gitignored so it can never be accidentally pushed. `turion/brain/claude_client.py`'s `is_configured()` fallback (stub mode) stays in the code for future free testing, but the real key is active now — using `claude-haiku-4-5-20251001`.
- [x] Text-to-Speech — English (pyttsx3), Marathi (Piper, speaker 8), and Hindi (Piper, "pratham") all working. **Mixed-language replies are spoken entirely in one voice (default Marathi Piper), not split by script** — the per-word script router was removed 2026-09-01 after hearing it live: switching engines mid-reply caused audible gaps and a jarring male/female voice alternation; one consistent (if occasionally mispronounced) voice sounded clearly better. Both STT and TTS models preload at `main.py` startup (~40s, once) so per-turn latency stays low afterward.
- [x] Full loop wired end-to-end and confirmed live with the real API: listen → transcribe (Marathi, IndicConformer) → think (Claude Haiku 4.5) → speak (Piper) — runs via `turion/main.py`. Console now prints which module handles each step (`(module) TTS: Piper [mr] -> "..."`, `Thinking... (module: Claude API, model: ...)`) so it's visible while running, not just inferred from behavior.
- [x] Basic error handling — mic errors and Claude API errors are caught per-turn so one bad turn doesn't crash the assistant; missing API key no longer crashes either, falls back to stub mode
- [x] **Phase 1 validated as a working milestone — DONE 2026-09-01.** First real end-to-end conversation confirmed working (transcribe ~8.35s, think ~1.97s, speak ~18s for that turn — timings will vary by reply length).

## Checklist — Setup / Tracking

- [x] Doc folder reviewed (`Doc/project_info.md`)
- [x] Session log created (`Doc/session_log.md`)
- [x] Project status file created (this file)
- [x] Local git repo + GitHub backup set up (https://github.com/TuRaing/TURION_ROBO, private)
- [x] Repo structure scaffolded (`turion/` package, `firmware/` placeholder)

---

## Notes / Decisions Log
- Builder has no prior coding experience — Claude Code will write/run the actual code.
- Budget-conscious: free/local tools by default (Whisper, YOLO, Coqui TTS); paid Claude API reserved for the reasoning/conversation layer only.
- Event-driven design required — do not poll the Claude API continuously (cost control).
- No usable GPU on the dev laptop (Intel integrated + old AMD Radeon HD 8670M, no CUDA/ROCm) — all local model inference is CPU-only. Caps practical Whisper model size (`small`, not `medium`/`large`) and factored into the Marathi-STT decision below.
- Marathi STT accuracy with generic Whisper (even at CPU-feasible sizes) is poor — it's a low-resource language for that model family. Decided to use AI4Bharat's IndicConformer (`ai4bharat/indic-conformer-600m-multilingual`) for Marathi instead, over paid cloud STT (Google/Azure), specifically to keep voice data local for privacy — full reasoning in `project_info.md`.
- IndicConformer is a gated model on Hugging Face (auto-approve — accept terms, no manual review) — needed a free HF account + access token (`HF_TOKEN` env var) to download once. After download, all inference is fully local/offline, so this doesn't compromise the privacy goal.
- RNNT decoding (vs. CTC) gave noticeably better Marathi accuracy in testing — RNNT is now the default in `transcribe_indic()`.
- pyttsx3 (TTS) has a Windows SAPI5 quirk: reusing one cached engine instance across multiple say()/runAndWait() calls in the same process silently drops audio on the second+ call. Fixed by creating a fresh engine per `speak()` call instead of caching it.
- **Root-caused the intermittent near-silent recordings (peak ~0.001):** user was wearing Bluetooth earbuds (realme Buds Air7 Pro), which (a) are lower audio quality for mic input than the laptop's built-in mic — Bluetooth call-mode (HFP) audio is compressed/narrowband — and (b) caused a Windows audio-driver glitch where even the built-in mic stopped registering any input, fixed by a restart. **For best Marathi STT accuracy, use the laptop's built-in Realtek mic for input** (Settings → System → Sound → Input), even if Bluetooth earbuds are used for output/listening — Windows lets input and output devices be set independently. Confirmed 2026-08-31: a 10-digit phone number read aloud came back 100% correct after switching to the built-in mic + a restart.
- **Marathi/Hindi TTS solved via Piper**, not the originally-planned WinRT route — Piper has an actual native-Marathi voice (better than Hindi-reading-Marathi), is fast (~0.16x real-time on CPU), and needed no risky changes to the working STT dependency stack. AI4Bharat's Indic Parler-TTS (would've been the highest-quality option) turned out to be incompatible with Python 3.14 + the current `transformers` version — full reasoning in `project_info.md`.
- Deep-dived a user report of "12-15s lag" after speaking: transcribe (~1s) and think (~0s, stub) were already fast; the ~8s was `speak()` — turned out to be the actual spoken *duration* of the (unnecessarily verbose) stub reply, not processing overhead. Shortened the stub reply text and confirmed a short realistic-length reply speaks in ~3.4s.
- **Actually tested Indic Parler-TTS** in an isolated Python 3.12 environment (see disk-space note below for the setup detour) — voice quality was genuinely good, but generation took **34.2x real-time** (~140s to produce 4s of audio) on this CPU-only laptop. Confirmed not viable for a live assistant; Piper remains the answer for Marathi/Hindi TTS. The Python 3.12 environment and downloaded models (~4GB) were deleted afterward — nothing from this experiment persists in the project.
- **Found and fixed a critical disk-space problem** while setting up the Parler-TTS test environment: C: drive had ~0 GB free (D: only ~3GB) — a nearly-full system drive that likely also contributed to the earlier Python 3.12 MSI installer failures. Root cause: an unused WSL Ubuntu install consuming ~20GB (`C:\Users\<user>\AppData\Local\wsl`). User confirmed they don't use WSL; removed it (`wsl --unregister Ubuntu`, run by the user directly — the harness blocks Claude from running destructive commands like this itself), freeing C: to ~22GB. Worth checking again periodically as model downloads accumulate.

- Piper only covers 7 Indian languages (hi, mr, bn, te, ml, ur, ne) — not an issue now, but researched broader options for later: Meta MMS-TTS (untested, deprioritized) and **AI4Bharat's separate "Indic-TTS" project (not to be confused with Indic Parler-TTS)** — 13 Indian languages.
- **AI4Bharat Indic-TTS tested successfully overnight (2026-08-31→09-01)**, unlike Indic Parler-TTS: **1.5–1.85x real-time** (usable, though slower than Piper's 0.16x) after fixing a long chain of environment issues specific to this old fork (buggy Python-version check, missing dev headers on the portable Python, a broken old `pyworld` pin, a numpy/scipy/numba version conflict, an import-order-dependent torch DLL crash on Windows, a hardcoded bad path in the checkpoint's config, and a console-encoding crash) — full list in `project_info.md`. **Not integrated into `speak.py`** — this was a feasibility test only; Piper remains production. Kept the working environment (`D:\indic_tts_env`, `D:\indic_tts_src`, `C:\indic_tts_checkpoints`) since it took real effort to get working and could be reused if another Indian language is needed later — unlike the Parler-TTS environment, which was deleted because it was unusable.
- **Disk space is tight again** (D: ~2GB free as of 2026-08-31 23:54) after this experiment — worth a cleanup pass at the start of the next session if it becomes a problem again; check `Get-PSDrive C, D` first.

- **Reviewed the Indic-TTS results (2026-09-01):** less natural than Piper, decided to leave it as a documented-but-unused fallback rather than integrate — Piper stays production for Marathi/Hindi/English.
- **Phase 4 compute board decided: Jetson Orin Nano** — over both Raspberry Pi 5 and Orange Pi 5/Rock 5, prioritizing avoiding future rework over upfront cost. Comparison artifact (specs + whole-robot cost estimates): https://claude.ai/code/artifact/a3121061-7981-4c50-ac34-e8d5f9827f06. Full reasoning in `project_info.md`.
- **New capability captured:** person identification (voice + face + object + human detection, culminating in recognizing owner/family members with persistent memory) — planned sequencing is API first, then Phase 2 camera/vision, then combine. Not started; documented under Phase 3 in `project_info.md`.
- **PHASE 1 COMPLETE (2026-09-01):** Claude API funded ($5, debit card + 18% Indian GST, ~$5.90 total). TURION's first real conversation confirmed working end-to-end. Reversed the TTS script-splitting design after hearing it live — see the TTS checklist entry above and `project_info.md` for the full reasoning. Added per-step module labels to `main.py`/`speak.py` console output at the builder's request, for visibility into which engine handles each stage.
- **Trained a custom wake word ("Hi Sisu") via openWakeWord (2026-09-01 evening)** — chosen over Picovoice Porcupine, whose free tier for custom wake words was permanently discontinued 2026-06-30. Training itself succeeded only after fixing 8 separate dependency-compatibility issues in the training Colab notebook (old packages vs. current Python 3.13/torch/numpy) — full blow-by-blow list in `project_info.md`, useful if retraining later. Result: `hi_si_su.onnx`/`.tflite`, ~200KB each.
- **Wake-word integrated into `main.py` overnight (2026-09-01→02)** — installed cleanly in the main `.venv` (no compatibility issues, unlike the training-side dependencies), model files committed at `turion/wake_word/models/` (had to add a `.gitignore` exception — the existing broad `models/` rule was silently excluding them), new `turion/wake_word/listen.py` module, `main.py`'s "press Enter to talk" replaced with continuous wake-word listening. Verified structurally (imports, model load, dummy prediction) but **not yet tested against the builder's real voice** — that's the first thing to check next session.

## Next Step
1. **Test live**: run `turion/main.py` (or the desktop shortcut) and say "Hi Sisu" — confirm it actually activates, and that the 0.5 detection threshold isn't too sensitive or too unresponsive. Retraining with more examples (100 was used vs. the recommended 1,000+) is the fallback if detection quality is poor.
2. Start Phase 2 (Vision) — object/face detection via camera.

---

## Doc Maintenance Policy
- `session_log.md` → updated every session (date/time, what was done, what's next)
- `project_status.md` → updated when phase/task status changes (checkboxes, current phase)
- `project_info.md` → updated whenever there's a new decision, scope change, or new info about the project itself (not just status) — it's the living overview doc, not a one-time write
