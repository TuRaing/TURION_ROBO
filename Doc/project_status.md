# TURION — Project Status

Last updated: 2026-08-31, 22:48

## Current Phase
**Phase 1 — Voice Assistant (Software Only)** — *Everything except the real Claude API works and is validated: mic input, English + Marathi STT, and English + Marathi + Hindi TTS (mixed-language text routed by script automatically). Both STT and TTS models preload at startup so per-turn latency is low. Only blocker: Claude API needs funding (min. $5) — main loop runs in STUB mode (fake replies) until then, fully testable for free.*

## Phase Overview

| Phase | Description | Status |
|---|---|---|
| 1 | Voice Assistant (listen → transcribe → think → speak) | 🟡 In progress |
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
- [ ] Claude API connected — **blocked on funding**, not code. Anthropic Console requires a $5 minimum credit purchase to even generate an API key (confirmed 2026-08-31, no free trial credit offered). `turion/brain/claude_client.py` now has an `is_configured()` check — when no key is set, `think()` returns a clearly-labeled stub reply (echoes back what was heard) instead of crashing, so the rest of the pipeline is fully testable for free. Swapping in a real key later needs zero code changes.
- [x] Text-to-Speech — English (pyttsx3), Marathi (Piper, speaker 8), and Hindi (Piper, "pratham") all working. Mixed-language replies are split by script per word and each part routed to the right voice automatically (`turion/voice_output/speak.py`). Both STT and TTS models preload at `main.py` startup (~40s, once) so per-turn latency stays low afterward.
- [x] Full loop wired end-to-end: listen → transcribe (Marathi) → think (stub) → speak — runs via `turion/main.py`, confirmed working in stub mode with per-stage timing (`(debug)` lines) to diagnose latency
- [x] Basic error handling — mic errors and Claude API errors are caught per-turn so one bad turn doesn't crash the assistant; missing API key no longer crashes either, falls back to stub mode
- [ ] Phase 1 validated as a working milestone — **pending real Claude API credit** (this is genuinely the only remaining item)

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

## Next Step
Get Claude API funded (min. $5 credit purchase, whenever affordable) and set `ANTHROPIC_API_KEY` — that is the only thing left in Phase 1.

---

## Doc Maintenance Policy
- `session_log.md` → updated every session (date/time, what was done, what's next)
- `project_status.md` → updated when phase/task status changes (checkboxes, current phase)
- `project_info.md` → updated whenever there's a new decision, scope change, or new info about the project itself (not just status) — it's the living overview doc, not a one-time write
