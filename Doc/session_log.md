# TURION — Session Log

Log of every Claude Code working session on this project: date, time, what was discussed/done, and what's next. Newest entry on top.

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
