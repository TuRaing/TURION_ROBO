# TURION — Project Status

Last updated: 2026-08-30

## Current Phase
**Phase 1 — Voice Assistant (Software Only)** — *In progress: mic input + English STT working; Marathi STT built but not yet validated; Claude API and TTS not yet tested*

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
- [ ] Speech-to-Text — Marathi, via AI4Bharat IndicConformer (installed, code written, **not yet tested against real speech**)
- [ ] Claude API connected (needs `ANTHROPIC_API_KEY` set — see README.md)
- [ ] Text-to-Speech working (pyttsx3 installed, not yet tested; likely English-voice-only on this machine)
- [ ] Full loop tested end-to-end: listen → transcribe → think → speak
- [ ] Basic error handling (no mic input, API failure, etc.)
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

## Next Step
Validate IndicConformer's Marathi accuracy (`tests/test_stt_indic_manual.py`), then connect the Claude API and test TTS to complete the full Phase 1 loop.

---

## Doc Maintenance Policy
- `session_log.md` → updated every session (date/time, what was done, what's next)
- `project_status.md` → updated when phase/task status changes (checkboxes, current phase)
- `project_info.md` → updated whenever there's a new decision, scope change, or new info about the project itself (not just status) — it's the living overview doc, not a one-time write
