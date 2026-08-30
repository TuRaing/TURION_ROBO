# TURION — Project Status

Last updated: 2026-08-30

## Current Phase
**Phase 1 — Voice Assistant (Software Only)** — *Not started (planning/setup stage)*

## Phase Overview

| Phase | Description | Status |
|---|---|---|
| 1 | Voice Assistant (listen → transcribe → think → speak) | 🔲 Not started |
| 2 | Vision (object/face detection) | 🔲 Not started |
| 3 | Memory / Personalization | 🔲 Not started |
| 4 | Physical Robot Arm | 🔲 Not started |
| 5 | Proactive Behavior & Device Control | 🔲 Not started |
| 6 | Bipedal Humanoid (long-term, aspirational) | 🔲 Not started |

Legend: 🔲 Not started · 🟡 In progress · ✅ Done

---

## Checklist — Phase 1 (Voice Assistant)

- [ ] Set up dev environment (Python, dependencies)
- [ ] Mic input working (capture audio from laptop/Bluetooth mic)
- [ ] Speech-to-Text integrated (Whisper, local)
- [ ] Claude API connected (decision/brain layer — start with Haiku for cheap testing)
- [ ] Text-to-Speech working (Coqui TTS / pyttsx3 / similar)
- [ ] Full loop tested end-to-end: listen → transcribe → think → speak
- [ ] Basic error handling (no mic input, API failure, etc.)
- [ ] Phase 1 validated as a working milestone

## Checklist — Setup / Tracking (this session)

- [x] Doc folder reviewed (`Doc/project_info.md`)
- [x] Session log created (`Doc/session_log.md`)
- [x] Project status file created (this file)

---

## Notes / Decisions Log
- Builder has no prior coding experience — Claude Code will write/run the actual code.
- Budget-conscious: free/local tools by default (Whisper, YOLO, Coqui TTS); paid Claude API reserved for the reasoning/conversation layer only.
- Event-driven design required — do not poll the Claude API continuously (cost control).

## Next Step
Begin Phase 1: get mic input + Whisper STT working first, before wiring up the Claude API call.

---

## Doc Maintenance Policy
- `session_log.md` → updated every session (date/time, what was done, what's next)
- `project_status.md` → updated when phase/task status changes (checkboxes, current phase)
- `project_info.md` → updated whenever there's a new decision, scope change, or new info about the project itself (not just status) — it's the living overview doc, not a one-time write
