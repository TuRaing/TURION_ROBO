# TURION — Session Log

Log of every Claude Code working session on this project: date, time, what was discussed/done, and what's next. Newest entry on top.

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
