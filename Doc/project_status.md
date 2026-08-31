# TURION — Project Status

Last updated: 2026-08-31, 19:21

## Current Phase
**Phase 1 — Voice Assistant (Software Only)** — *In progress: mic input, English STT, Marathi STT, and TTS all validated and working. Claude API not yet connected (needs `ANTHROPIC_API_KEY`).*

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
- [ ] Claude API connected — code + startup check ready, blocked on `ANTHROPIC_API_KEY` being set (see README.md)
- [x] Text-to-Speech working — tested, runs cleanly. Confirmed this machine only has English voices installed (Microsoft David/Zira) — no Marathi voice, so replies are always spoken in an English voice regardless of reply language
- [ ] Full loop tested end-to-end: listen → transcribe → think → speak (blocked on API key + a live mic test)
- [x] Basic error handling — missing API key fails fast at startup with a clear message; mic errors and Claude API errors are caught per-turn so one bad turn doesn't crash the assistant
- [ ] Phase 1 validated as a working milestone

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
Set `ANTHROPIC_API_KEY`, then run the full loop (`turion/main.py`) end-to-end.

---

## Doc Maintenance Policy
- `session_log.md` → updated every session (date/time, what was done, what's next)
- `project_status.md` → updated when phase/task status changes (checkboxes, current phase)
- `project_info.md` → updated whenever there's a new decision, scope change, or new info about the project itself (not just status) — it's the living overview doc, not a one-time write
