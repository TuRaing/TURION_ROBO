# TURION — Project Status

Last updated: 2026-08-31, 20:15

## Current Phase
**Phase 1 — Voice Assistant (Software Only)** — *In progress: mic input, English STT, Marathi STT, and TTS (English voice only) all validated and working. Claude API not yet funded — main loop runs in STUB mode (fake replies) so the rest of the pipeline is testable for free.*

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
- [x] Text-to-Speech (English) working — tested, runs cleanly.
- [ ] Text-to-Speech (Marathi/Hindi) — **known gap, not built**. Only English SAPI5 voices (David/Zira) are usable from Python; a Hindi voice was installed via Windows Settings but lives in the newer OneCore voice system, invisible to `pyttsx3`/classic SAPI. Needs a WinRT-based rewrite of `speak.py` — deliberately deferred until after the API is funded. Full details in `project_info.md`.
- [x] Full loop wired end-to-end: listen → transcribe (Marathi) → think (stub) → speak — runs via `turion/main.py`, confirmed working in stub mode
- [x] Basic error handling — mic errors and Claude API errors are caught per-turn so one bad turn doesn't crash the assistant; missing API key no longer crashes either, falls back to stub mode
- [ ] Phase 1 validated as a working milestone — **pending real Claude API credit**

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

## Next Step
Get Claude API funded (min. $5 credit purchase, whenever affordable) and set `ANTHROPIC_API_KEY` — everything else in Phase 1 is ready and waiting. Marathi/Hindi TTS (WinRT) is the item after that.

---

## Doc Maintenance Policy
- `session_log.md` → updated every session (date/time, what was done, what's next)
- `project_status.md` → updated when phase/task status changes (checkboxes, current phase)
- `project_info.md` → updated whenever there's a new decision, scope change, or new info about the project itself (not just status) — it's the living overview doc, not a one-time write
