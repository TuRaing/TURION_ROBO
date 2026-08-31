# TURION — Session Log

Log of every Claude Code working session on this project: date, time, what was discussed/done, and what's next. Newest entry on top.

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
