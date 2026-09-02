# TURION — Complete Project Overview

## What TURION Is
TURION is a long-term, phased project to build an embodied, multimodal AI agent — a system that can hear, see, speak, reason, and eventually control a physical robot body. It starts as a simple software voice assistant and grows step by step toward a stationary robotic arm, and ultimately (long-term, aspirational) a bipedal (human-like walking) humanoid robot.

The name TURION is consistent with the builder's other ventures: TURION Studios (animation/content) and TURION_AI_Trader (AI trading bot).

## Builder's Background & Constraints
- Strong hardware / VLSI / electronics background (works as a Physical Design engineer). No prior software/coding experience.
- Business goal: eventually build and sell TURION as a product/software, not just a personal project.
- Budget-conscious — prefers free/open-source tools wherever they are genuinely sufficient, and only pays for APIs where there's no good free alternative.
- Prototype-first approach: build something working and simple first, validate it, then expand — rather than designing the full end-state system upfront.
- Plans to use Claude Code (an AI coding agent) to actually write and run the code, since the builder cannot code independently yet.

## Guiding Principles (apply to every phase)
1. **One module, one job.** Sound detection, speech-to-text, vision, decision-making, and voice output should be separate, independent modules that pass simple structured data (JSON) to each other — not one another's business logic.
2. **Cheap/free by default, paid only where it earns its cost.** Local, open-source models (Whisper, YOLO, Coqui TTS, etc.) do the perception/classification work. A paid LLM API (Claude) is used only for the "brain" — genuine reasoning and natural conversation — not for routine detection tasks.
3. **Event-driven, not always-polling the API.** The system should listen/watch continuously using free local tools, and only call the paid Claude API when something actually requires a decision or a conversational reply. This is the single biggest lever for keeping a 24x7 system affordable.
4. **Hardware control is layered:** a compute board (Raspberry Pi / Jetson) handles AI/perception; a microcontroller (Arduino/ESP32) handles real-time motor/actuator control. They are not the same job and not the same board.
5. **Build and validate one phase before starting the next.** Each phase below should be a working, testable milestone on its own.

---

## Phase 1 — Voice Assistant (Software Only)
**Goal:** A working loop of listen → transcribe → think (Claude API) → speak.
- Mic input (laptop built-in or Bluetooth earbuds mic) — no new hardware needed yet
- Speech-to-Text: Whisper (local, free)
- Decision layer: Claude API (Haiku for cheap testing, Sonnet for better quality later)
- Text-to-Speech: free/local engine (Coqui TTS, pyttsx3, or similar)
- Runs entirely on the builder's laptop
- No camera, no robot, no persistent memory yet
- (Full detailed spec already written separately as the Phase 1 project doc for Claude Code.)

## Phase 2 — Vision
**Goal:** Add sight to the assistant.
- Camera input (laptop webcam initially; later a dedicated USB webcam, ₹1,500–5,500 depending on quality)
- Object detection: YOLO (local, free)
- Face detection/recognition: InsightFace or face_recognition (local, free)
- Optional later upgrade: stereo vision (two cameras) for depth perception, using OpenCV stereo calibration — useful once the system needs to judge how far an object is (e.g., for an arm to reach it)
- Vision output feeds into the Decision Layer as structured data (e.g., `{"face": "known", "object": "cup", "distance_cm": 40}`), same as audio does

## Phase 3 — Memory / Personalization
**Goal:** Let the assistant remember context across interactions.
- A simple local database (SQLite is enough at this scale) to store preferences, recent conversation history, routines
- Keep context sent to Claude API concise — only relevant recent history, to control token cost

### Planned combination: person identification (confirmed with builder 2026-09-01)
Immediate near-term sequencing the builder wants: **get the Claude API working first, then camera/vision (Phase 2), then combine both** into a person-identification capability — voice ID + face/image ID + object ID + "is this a human at all" detection, culminating in **recognizing the owner and family members specifically**, and remembering them persistently (ties Phase 2's face recognition into Phase 3's memory store).

**"Safety" for this feature means three things together, not one** (confirmed with builder):
- **Data privacy** — voice/face data of family members stays local only, never sent to the cloud (same principle already applied to STT). Only structured metadata (name, relationship) should ever reach the Claude API, never raw biometric data.
- **Access/security** — reliably distinguishing a known household member from an unrecognized/unknown person (the practical reason to build this at all).
- **Avoiding misidentification** — not confusing one person for another; a wrong match is worse than an "unknown, not sure" result for this use case, so the system should be built to prefer saying "I don't recognize this person" over a confident wrong guess.

Not started — Phase 1 (this API-first, then-camera sequencing) hasn't begun yet. Revisit this note when Phase 2 (vision) actually starts.

## Phase 4 — Physical Robot Arm (Fixed/Stationary)
**Goal:** First physical body — a desk-mounted robotic arm for simple household tasks (e.g., picking up/moving objects).
- **Motors:** Servo motors (e.g., MG996R) for joints; ready-made, not custom-designed
- **Motor driver / control board:** Arduino or ESP32 handles real-time motor commands; Raspberry Pi/Jetson (running the AI) sends high-level commands to it over serial/USB
- **Power chain:** Battery (LiPo recommended — best energy density for its weight) → voltage regulator/buck-boost converter (to supply each component's required voltage, e.g., 5V for Pi, different voltage for motors) → motor driver → motors
- **Sensors for this phase:**
  - Camera (already have from Phase 2)
  - Microphone (already have from Phase 1)
  - Force-sensitive resistors (FSR) on the gripper fingers — to sense grip strength/whether an object is held (needs an ADC module like MCP3008 if wired to a Raspberry Pi directly, since Pi has no built-in ADC; Arduino has built-in analog pins so this is simpler if FSRs are wired through Arduino)
  - Optional: ultrasonic sensor (HC-SR04) for accurate distance-to-object measurement, since a single 2D camera alone is not reliable enough for judging distance
- **AI compute board — decided: NVIDIA Jetson Orin Nano** (confirmed with builder 2026-09-01), over both Raspberry Pi 5 (₹8,000–10,000) and Orange Pi 5 / Radxa Rock 5 (₹13,000–21,000, RK3588-class). Full comparison (specs, tradeoffs, whole-robot cost estimates) published as an artifact — see `Doc/session_log.md` 2026-09-01 entry for the link.
  - **Reasoning:** the builder explicitly prioritized *avoiding future rework* over minimizing upfront cost — cannot write/port code independently (no software background), so re-doing an integration later (e.g. converting models to Rockchip's RKNN format, or discovering mid-project that a cheaper board isn't enough) is a much bigger cost than the ₹8,000–14,000 price gap now. This is a deliberate, one-time exception to the "prototype cheap, expand later" principle — justified because TURION's actual bottleneck (model speed) is already proven, not hypothetical: Indic Parler-TTS measured at 34.2x real-time on CPU-only hardware this session, and Jetson's CUDA support means the exact PyTorch code already written and working keeps running unmodified, with GPU acceleration, rather than needing a parallel NPU-specific conversion effort for every model.
  - **What Jetson unlocks specifically:** Raspberry Pi 5 and Rockchip boards both lack a real GPU, so they're in the same boat as the current dev laptop for TTS — Piper (fast, multi-voice, but not the higher-quality native-Marathi Indic Parler-TTS) would remain the only practical option there. Jetson's on-device GPU is what makes Indic Parler-TTS's consistent-cross-language voices (see the "universal interpreter" note below) actually usable in real time — not yet re-tested on real Jetson hardware, but the CPU numbers make this the clear expectation.
  - **Whole-robot cost estimate (Jetson build):** ₹28,500–48,500 total for Phase 4 (servos, frame, sensors, power, camera, plus the board) — the compute board itself is roughly a quarter to a third of that, not the dominant cost.

## Phase 5 — Proactive Behavior & Device Control
**Goal:** Move from "answers when asked" to "notices and acts on its own."
- Smart home device control (IoT smart plugs, etc.) as a natural extension of the arm/actuator control built in Phase 4
- Scheduled/triggered behaviors (e.g., noticing a pattern and proactively saying something), built on top of the memory system from Phase 3

## Phase 6 (Long-Term, Aspirational) — Mobility Toward a Bipedal Humanoid
**Goal:** Eventually move from a fixed arm to a robot that can walk like a human. This is explicitly a long-term, much harder goal than Phases 1–5, and should only be approached after Phase 4 is working and well understood.
- Bipedal walking requires constant real-time balance correction — this is one of the hardest unsolved problems in robotics even for large, well-funded companies (Boston Dynamics, Tesla, 1X, etc.)
- **Sensors needed:** a full IMU (gyroscope + accelerometer, e.g., MPU6050 for a cheap option or BNO055 for more accuracy) for orientation/tilt, plus foot pressure/force sensors (multiple per foot) for ground contact and weight distribution
- **Motors/actuators needed:** high-torque servo-actuators or BLDC motors — ordinary hobby servos (SG90/MG996R) used for the arm are not strong enough to support a whole body's weight and movement
- **Control:** balance correction needs very fast, real-time control loops (e.g., PID control), often on a dedicated real-time microcontroller (e.g., STM32) because even a Raspberry Pi can be too slow for this
- **Budget reality:** actuators alone for legs can run ₹15,000–50,000+ per joint; this phase is estimated at 10–50x the cost and complexity of Phase 4
- Total sensor count at this stage can reach 20–30+ across the whole body, versus roughly 4–6 in Phase 1–4

---

## Tech Stack & Repo Structure (decided 2026-08-30)

**Language split — by hardware layer, not mixed:**
- **Python** — all AI/"brain" code: audio (Whisper), vision (YOLO), memory (SQLite), decision layer (Claude API), TTS, and the high-level hardware-command code that runs on the compute board (Raspberry Pi/Jetson) in Phase 4+.
- **C/C++ (Arduino framework)** — microcontroller firmware (Arduino/ESP32/STM32) for real-time motor/actuator control, starting Phase 4. This is a separate program on separate hardware, never mixed into the Python codebase.
- The two sides talk only via structured JSON messages over serial/USB (per Guiding Principle #1) — this is what keeps them conflict-free as the project grows into embedded phases.

**Repo structure (scaffolded now so no restructuring is needed later):**
```
TURION_ROBO/
├── Doc/                     # planning & tracking docs
├── turion/                  # main Python package — the "brain"
│   ├── audio/                 # Phase 1: mic capture + Whisper STT
│   ├── voice_output/          # Phase 1: TTS
│   ├── brain/                 # Phase 1: Claude API decision layer
│   ├── vision/                 # Phase 2: YOLO, face recognition
│   ├── memory/                 # Phase 3: SQLite
│   ├── hardware/               # Phase 4+: Python side of serial/JSON comms to firmware
│   └── main.py                 # main loop: listen -> transcribe -> think -> speak
├── firmware/                 # Phase 4+: Arduino/ESP32/STM32 code (C/C++, PlatformIO)
│   └── arm_controller/
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```
`firmware/` is reserved empty until Phase 4 begins.

---

## Language Profile (confirmed 2026-08-31)
The builder's expected day-to-day use of TURION: **mostly Marathi, regularly English, occasionally Hindi**. This shapes STT and TTS language coverage decisions below and going forward — Marathi is the priority, not an afterthought.

## Speech-to-Text: Dual Engine for English + Marathi (decided 2026-08-30)

The builder speaks both English and Marathi with TURION. One STT model doesn't cover both well, so Phase 1 uses two local, free engines rather than one:

- **English → OpenAI Whisper (`small` model, local).** Accurate out of the box. Uses `initial_prompt="The assistant's name is TURION."` so the wake word isn't misheard as a common word, and `condition_on_previous_text=False` to reduce runaway hallucination.
- **Marathi → AI4Bharat IndicConformer (`ai4bharat/indic-conformer-600m-multilingual`, local).** Generic Whisper's Marathi accuracy was poor even at CPU-feasible sizes (Marathi is a low-resource language for it). IndicConformer is purpose-built for Indian languages and gave much better results at a comparable model size.
- Mixing both languages in a single sentence (code-switching) is not reliably handled by either engine — this is a hard, unsolved problem for most speech recognition systems, not specific to TURION. Speak one language per utterance for now.

**Why not paid cloud STT (Google Cloud Speech-to-Text / Azure AI Speech)?** Both have excellent Marathi accuracy and were seriously considered (checked 2026-08-30 pricing: Google ~$0.016–0.024/min with 60 free min/month; Azure ~$1/hour real-time with 5 free hours/month — light testing usage would likely fit inside Azure's free tier). Ruled out specifically because the builder wants voice data to stay local for **privacy** — every utterance would otherwise leave the machine and go to a third-party server. Local/free also matches Guiding Principle #2. Revisit this only if local Marathi accuracy proves insufficient after tuning.

**Hardware constraint this decision was made under:** the dev laptop has no usable GPU for AI inference — Intel integrated graphics plus an old AMD Radeon HD 8670M (2016-era, no CUDA/ROCm support). All STT runs on CPU only, which is why the `small`-sized Whisper model was chosen over `medium`/`large` (CPU inference time scales up fast with model size), and why IndicConformer's 600M-parameter size was acceptable — it's in the same practical range.

**Validated 2026-08-31** with live speech across easy and hard test scripts (see `tests/marathi_test_script.txt` and `tests/marathi_test_script_hard.txt`). Findings:
- IndicConformer's model repo on Hugging Face is gated (auto-approve terms, not manual review) — needs a free HF account + access token once to download; inference itself is fully offline afterward.
- **RNNT decoding gave clearly better accuracy than CTC** and is now the default.
- Accuracy is strong on common vocabulary and even long, grammatically complex ordinary sentences (often perfect). It's noticeably weaker on technical/uncommon words (e.g. "कृत्रिम बुद्धिमत्ता" / artificial intelligence, "संशोधन" / research) and occasionally drops a word or clause, more often near the end of a longer utterance. This is judged good enough for everyday voice-assistant commands — perfect accuracy isn't realistic for any free/local (or even paid) STT system, and Claude can generally infer intent from a slightly imperfect transcript, the way a person would.
- **Important setup finding:** microphone input quality matters a lot. Using Bluetooth earbuds (realme Buds Air7 Pro) as the input device measurably hurt accuracy (Bluetooth call-mode/HFP audio is compressed and narrowband) and at one point caused a Windows audio-driver glitch where the mic stopped registering input entirely, until a restart. **Always use the laptop's built-in Realtek mic for TURION's voice input** — Windows lets input and output devices be set independently (Settings → System → Sound), so Bluetooth earbuds can still be used for private listening/output without hurting input accuracy. After switching to the built-in mic (post-restart), a 10-digit spoken phone number was transcribed with 100% accuracy.

---

## Text-to-Speech: Marathi/Hindi voice output (resolved 2026-08-31)
`turion/voice_output/speak.py` originally used only `pyttsx3` (classic Windows SAPI5), which can only speak English on this machine (Microsoft David/Zira) and silently mangles Devanagari text entirely. Fixed with a multi-engine setup:

- **Marathi → Piper TTS**, voice `rhasspy/piper-voices: mr/mr_IN/google/medium` (trained on the open OpenSLR-64 Marathi dataset), **speaker id 8** — chosen by listening to all 9 available speakers in that voice. Local, free, MIT-licensed, fast (~0.16x real-time generation on this CPU — 6x faster than the audio it produces).
- **Hindi → Piper TTS**, voice `hi_IN-pratham-medium` (male) — chosen over 2 other Hindi voices after listening. Confirmed this voice's Marathi pronunciation is poor (it's Hindi-trained, not Marathi), so it's used only for actual Hindi text, not as a Marathi substitute.
- **English → pyttsx3** (unchanged, already worked).
- **Mixed-language replies are spoken entirely in one voice (default Marathi Piper), not split by script — reversed 2026-09-01 after hearing it live.** Originally built a per-word script router (`_split_by_script` in `speak.py`) that sent each word to the matching engine, e.g. "मी TURION आहे" → "मी"/"आहे" in Marathi Piper, "TURION" in pyttsx3. Technically correct per-word, but **sounded worse as a whole reply**: heard live during TURION's first real conversation (2026-09-01, once the Claude API was funded) — every engine switch is a separate audio clip, so consecutive chunks played with audible gaps ("तुटक"/choppy), and alternating pyttsx3's male English voice into the female Marathi Piper voice mid-sentence was jarring. Removed the splitter; `speak()` now always uses one voice for the whole reply — English words get spoken with a Marathi accent (imperfect pronunciation) but the audio is continuous and voice-consistent, which the builder preferred by a clear margin. Marathi vs. Hindi still can't be auto-distinguished from Devanagari text alone (same open problem noted under STT) — pass `lang="hi"` explicitly when the text is known to be Hindi.
- **Roads not taken:**
  - **WinRT** (`Windows.Media.SpeechSynthesis`) — the modern Windows voice API that could reach the OneCore Hindi voice installed via Settings (invisible to classic SAPI/`pyttsx3`/`win32com`, confirmed by direct query). Got a working proof-of-concept (`winrt-Windows.Media.SpeechSynthesis` + reading the raw PCM stream and playing it via `sounddevice`, since `MediaPlayer` doesn't work reliably from a plain console script), but abandoned once Piper turned out to have an actual **native Marathi** voice available — better than Hindi-reading-Marathi regardless of API. Packages uninstalled.
  - **AI4Bharat Indic Parler-TTS** (`ai4bharat/indic-parler-tts`) — a proper Marathi-trained generative TTS model. On Python 3.14 (this project's main environment) it's **incompatible**: pins `transformers<=4.46.1`, which needs `tokenizers<0.21` — no Python 3.14 wheel, Rust source build fails (PyO3 doesn't support 3.14). **Actually tried it** (2026-08-31) in a separate, isolated Python 3.12 environment (`D:\parler_tts_env`, kept outside this repo specifically so it couldn't risk the working `transformers` version IndicConformer/STT depends on) — installed and ran successfully. Voice quality was genuinely good. But: **~140s to generate 4s of Marathi audio (34.2x real-time)** — this model is built for GPU and is roughly 200x slower than Piper on this CPU-only hardware. Confirmed not viable for a live voice assistant; environment and downloaded models (~4GB) deleted afterward. Would only be worth revisiting with a GPU.
- **Model loading is slow** (~35s for STT, ~5s for TTS, on this no-GPU CPU) — not a bug, just the cost of 600M+ parameter models on this hardware. Fixed by preloading both models at `turion/main.py` startup (`preload()` functions in `transcribe_indic.py` / `speak.py`) instead of on first use, so the delay happens once up front with a clear "Loading..." message rather than confusingly mid-conversation. Per-turn latency after that is small (STT ~0.36x real-time, TTS ~0.16x real-time) — most of what feels like "lag" during stub-mode testing was actually just the stub reply's own spoken length, not processing overhead.

## Broader Indian-language TTS coverage (2026-08-31/09-01)
Piper (current TTS engine) only covers 7 of India's languages: Hindi, Marathi, Bengali, Telugu, Malayalam, Urdu, Nepali. No Tamil, Kannada, Gujarati, Punjabi, Odia, Assamese, Sanskrit, etc. Not an issue for now (builder uses Marathi/English/occasional Hindi), but worth knowing if TURION ever needs to support more Indian languages.

- **Meta MMS-TTS** (`facebook/mms-tts-<lang>`) — part of Meta's Massively Multilingual Speech project, 1,107 languages total. Same VITS architecture family as Piper, so likely fast — **not tested**, deprioritized once Indic-TTS (below) proved out.

- **AI4Bharat Indic-TTS** — **tested successfully overnight 2026-08-31→09-01**, working end-to-end for Marathi. 13 Indian languages: Assamese, Bengali, Bodo, Gujarati, Hindi, Kannada, Malayalam, Manipuri, Marathi, Odia, Rajasthani, Tamil, Telugu. FastPitch (acoustic) + HiFi-GAN (vocoder) — lightweight, non-autoregressive. **Real-time factor ~1.5–1.85x** (both bundled Marathi speakers, "male" and "female") — far faster than Indic Parler-TTS's 34.2x, though slower than Piper's 0.16x. Genuinely usable.
  - Set up in an isolated environment at `D:\indic_tts_env`, kept fully separate from the main project (same reasoning as the Parler-TTS experiment) — cloned forks `gokulkarthik/TTS` and `gokulkarthik/Trainer` into `D:\indic_tts_src`, checkpoints in `C:\indic_tts_checkpoints\mr\` (downloaded from GitHub Releases, not Hugging Face — `v1-checkpoints-release` tag, has a `.zip` per language).
  - **Getting it working required fixing a long chain of environment issues** (all specific to this old, unmaintained Coqui-TTS-based fork, worth recording in case Indic-TTS is revisited for another language):
    1. `Trainer`'s setup.py has a buggy Python-version check (`sys.version_info > (3, 11)` is `True` for any 3.11.x patch release due to Python tuple comparison, not just true 3.12+) — rejects all of 3.11 and 3.12, actually needs **3.10**.
    2. The portable/embeddable Python distribution (used because the real installer fails on this machine, see Parler-TTS notes) has no C headers/import libs, so any package needing to compile a C/Cython extension fails with `Python.h: No such file or directory`. Fixed by downloading the official `python` NuGet package (a plain zip, no installer needed) and copying its `include`/`libs` folders into the **venv's** own expected location (`<venv>\Scripts\Include` and `<venv>\Scripts\libs` — not the base Python install's folders; a `virtualenv`-created venv from an embeddable base has non-standard `sysconfig` paths).
    3. `requirements.txt` pins `pyworld==0.2.10`, which has no Windows wheel and fails to build from source (`AttributeError: 'dict' object has no attribute '__NUMPY_SETUP__'`, a known old-numpy-build-pattern incompatibility with modern setuptools). Relaxed to `pyworld>=0.3.5`, which has a prebuilt wheel.
    4. Numpy/scipy/numba version chain conflicts: `numba==0.55.1` (pinned) requires `numpy<1.22`, but an unpinned `scipy` resolved to a build needing a newer numpy ABI, and the newest `soundfile` needs numpy's modern type-hint support. Resolved by keeping `numpy==1.21.6` (the original pin) and adding explicit pins `scipy==1.7.3` and `soundfile==0.12.1` to match that numpy era.
    5. **Import-order-dependent DLL conflict on Windows:** if `librosa`/`numba`/`llvmlite` get imported before `torch`, torch's own `c10.dll` then fails to initialize (`OSError: [WinError 1114]`) — but the identical imports succeed if `torch` is imported first. `TTS.bin.synthesize`'s own import chain triggers the bad order. Worked around by writing a small standalone script that does `import torch` as the very first line, then uses `TTS.utils.synthesizer.Synthesizer` directly instead of the CLI entry point.
    6. The downloaded `config.json` has an absolute `speakers_file` path baked in from AI4Bharat's own training machine (`models/v1/mr/fastpitch/speakers.pth`), which doesn't exist locally — edited the config to point at the actual checkpoint location.
    7. Printing Devanagari progress text crashes on Windows' default console codepage (same class of issue seen earlier with PowerShell) — fixed by setting `PYTHONIOENCODING=utf-8`.
  - **Same limitation as Piper:** each language checkpoint only knows its own script's vocabulary — an embedded English word like "TURION" gets silently dropped, character by character. Would need the same script-splitting approach already built into `speak.py` if this were integrated for real use.
  - **Quality (user-reviewed 2026-09-01):** pronunciation was judged less clear/natural than Piper's Marathi voice — has a noticeable non-Marathi ("Hindi") accent quality. Likely because all 13 Indic-TTS languages share the same training pipeline/architecture (FastPitch is the acoustic/pronunciation model; HiFi-GAN is just the vocoder and isn't the source of the accent, so swapping only the vocoder wouldn't fix this), giving a somewhat generic "pan-Indian" character rather than each language sounding distinctly native — unlike Piper's Marathi voice, trained independently on a dedicated Marathi dataset (OpenSLR-64).
  - **Not yet integrated into `turion/voice_output/speak.py`** — this was a feasibility test only, run in the isolated environment. Piper remains the production TTS for Marathi/Hindi/English (better quality there). Revisit Indic-TTS specifically if/when a non-Piper language (Tamil, Kannada, Gujarati, Odia, Assamese, Bodo, Manipuri, Rajasthani) is actually needed — Piper's own voice catalog doesn't cover any of those.

**Playbook for adding a new TTS language later** (agreed with the builder 2026-09-01): when a specific new Indian language is actually needed —
1. First search for a **dedicated, independently-trained voice** for that language specifically (the way Piper's Marathi voice was found) — fast (VITS-class) and usually better quality than a shared multilingual model.
2. If none exists, fall back to **Indic-TTS** if that language is one of its 13 — slower (~1.2–1.9x real-time) and a more generic accent, but works today with no extra training.
3. Only consider fine-tuning or training a new voice from scratch if neither of the above exists or the quality genuinely isn't good enough for the use case — real effort (data + compute + days), not a quick option.

### Why this matters: a future "universal interpreter" capability (revealed by the builder 2026-09-01)
The real motivation behind wanting broad Indian-language coverage: eventually, when TURION encounters any Indian person, it should be able to **ask them what language they speak, then translate between that person and whoever it's helping** — a live interpreter, not just a Marathi/English/Hindi assistant for the builder personally. This reframes why the STT/TTS language-coverage research above matters — it's not just "nice to have," it's groundwork for a real planned capability.

What this would need, when actually built (not started — noted here for when the time comes):
- **Language detection** — ask the person directly, or auto-detect from their speech (Whisper and IndicConformer already return a detected-language signal in some modes; would need to formalize this)
- **Translation** — Claude itself can do this well as part of its normal reasoning; no separate translation model needed
- **STT + TTS per language** — this is where the Piper-first/Indic-TTS-fallback playbook above directly applies, language by language, as real need arises

**One consistent voice across languages, for this specific feature:** the builder specifically wants one clean voice usable across many Indian languages for the interpreter feature (not a different voice per language). Re-checked **Indic Parler-TTS** (`ai4bharat/indic-parler-tts`, already tested — see above) with this in mind: it actually supports **21 languages** (Assamese, Bengali, Bodo, Dogri, English, Gujarati, Hindi, Kannada, Konkani, Maithili, Malayalam, Manipuri, Marathi, Nepali, Odia, Sanskrit, Santali, Sindhi, Tamil, Telugu, Urdu — plus untested Chhattisgarhi/Kashmiri/Punjabi), with **69 named voices that stay consistent across languages** (e.g. describe "Rohit" speaking and get the same voice identity in Marathi, Hindi, Tamil, etc.) — exactly this requirement, already solved by the model itself. The only blocker found was speed (34.2x real-time on this CPU-only laptop). **This is likely a non-issue by the time the interpreter feature is actually built**, since it's explicitly future work layered on a working Phase 1–3 assistant — plausibly running on Jetson Orin Nano (Phase 4 compute board, has a real GPU) by then, where Indic Parler-TTS's speed should stop being a blocker. Plan: **use Indic Parler-TTS for the interpreter feature specifically**, once on GPU-capable hardware; Piper stays the fast CPU-friendly choice for the builder's own day-to-day Phase 1 use.

This is **not Phase 1 scope** (Phase 1 is the builder's own personal voice assistant, in Marathi/English/occasional Hindi). Treat it as a distinct future capability — likely layered on top of Phase 1–3 once the core assistant is solid, rather than a phase of its own. Revisit this note when it's time to scope it properly.

---

## Wake Word Detection — trained model ready, not yet integrated (2026-09-01)
Builder wants TURION to stay always-on and only activate on a spoken trigger phrase, rather than the current "press Enter to talk" flow — the standard "wake word" pattern (Hey Siri / OK Google).

**Engine chosen: openWakeWord** (`github.com/dscripka/openWakeWord`) — fully free, open-source, no account needed, runs efficiently even on weak hardware (reportedly 15-20 models simultaneously in real-time on a single Raspberry Pi 3 core). The other option researched, **Picovoice Porcupine**, was ruled out immediately: its free tier for custom wake words was **permanently discontinued 2026-06-30** ("no non-commercial tier planned" per Picovoice's own statement) — not a close call, just no longer available.

### Choosing the wake phrase
Went through several rounds before settling: **TURION** itself (too hard to pronounce cleanly in the English-phoneme-based synthetic training pipeline — "gy"-type sounds in candidates like "Gyanu" kept collapsing into "j"), then candidates for a short, evocative, separate activation phrase (Sisu — Finnish for grit/resilience; Gyanu — from Sanskrit ज्ञान/knowledge, rejected as too close to a common Indian nickname pattern, higher false-trigger risk) — **landed on "Hi Sisu"** (`hi_si_su` in the training tool's phonetic-underscore format): clean, reliable pronunciation (confirmed by ear), and the "Hi" prefix (mirroring "Hey Siri") further reduces accidental-activation risk versus a bare single word. TURION remains the assistant's name; "Hi Sisu" is only the activation trigger.

### Training process and the debugging chain
Used openWakeWord's official quick-start Colab notebook (`automatic_model_training_simple.ipynb`) — meant to be a no-code, <1-hour process (type the wake word, click Run all). In practice, the notebook (last maintained ~April 2026) has drifted badly out of sync with Colab's current environment (Python 3.13, newer torch/numpy/setuptools) — same category of "old ML notebook vs. current ecosystem" pain as the Indic-TTS session, but across three separate installed packages this time. Full fix chain, in the order encountered (useful if retraining for a different word/language later):

1. **`piper-phonemize-cross` (pip package) no longer exists on PyPI at all** — "from versions: none". Replaced with the maintained fork **`piper-phonemize-fix`** in the notebook's own install cell.
2. **`torchvision` pinned to an unavailable version** (`==0.20.0`, no wheel for Python 3.13) — not actually needed by this pipeline (never imported), so the whole torch/torchvision/torchaudio pin line was commented out; Colab's preinstalled torch stack was used instead.
3. **Stale partial-install guard**: the notebook's install cells are gated by `if not os.path.exists("./piper-sample-generator")` — a folder left behind by an earlier *failed* attempt made the notebook skip reinstalling on retry, silently reproducing the same error. Fix: `!rm -rf piper-sample-generator` (and later `my_custom_model`, `my_model.yaml`) before re-running, whenever retrying after a mid-install failure.
4. **`torch.load()` defaults changed in PyTorch 2.6+**: `weights_only` defaults to `True` now (a security change), which breaks loading older full-pickle checkpoints (`UnpicklingError: Weights only load failed`). Hit this **twice**, in two unrelated files that both load old checkpoints this way — `piper-sample-generator/generate_samples.py` (the base TTS voice model) and `dp/model/model.py` inside the DeepPhonemizer package (used for generating adversarial/negative training phrases). Both fixed the same way: add `weights_only=False` to the `torch.load(...)` call (safe here since both checkpoints are from trusted sources — rhasspy and DeepPhonemizer's own releases).
5. **`pkgutil.ImpImporter` removed in Python 3.12+**: `webrtcvad`'s import chain (via `pkg_resources`) crashed with `AttributeError: module 'pkgutil' has no attribute 'ImpImporter'`. Fixed with a monkey-patch cell run before the import: define a dummy `ImpImporter` class and assign it to `pkgutil.ImpImporter` if missing.
6. **The system-level `pkg_resources` at `/usr/lib/python3/dist-packages/` is fundamentally incompatible with Python 3.13's import system** (multiple further `AttributeError`s cascading through its namespace-package handling — `find_module`, etc.) — patching it call-by-call proved to be an endless chase. Instead, patched `webrtcvad.py` directly: it only used `pkg_resources` for a trivial `__version__` string, so commented out the `import pkg_resources` line and hardcoded `__version__ = '2.0.10'` instead — sidesteps the broken module entirely.
7. **`torchaudio.set_audio_backend()` removed** in current torchaudio (2.11) — `torch_audiomentations/utils/io.py` called it at module level for legacy setup that's no longer needed. Patched out (replaced with `pass`).
8. **`torchaudio.info()` also removed** — same file's `get_audio_metadata()` used it to read a WAV file's sample count/rate. Replaced the function body with an equivalent `soundfile.info(file_path)` call (`soundfile` was already a dependency) — more stable than chasing torchaudio's changing API surface further.

None of these are edits to openWakeWord's own code — all were in its (older, less actively maintained) dependencies. **Training succeeded once all of the above were applied**, confirmed live (`Training: 21% 2132/10000 [01:04<03:10, 41.35it/s]` — real progress, not stalled).

### Result
Trained model downloaded successfully: **`hi_si_su.onnx`** and **`hi_si_su.tflite`**, ~200KB each — confirms the earlier claim that deployed wake-word models are tiny; none of the multi-GB training data (the ~16GB ACAV100M feature file, MIT RIR reverb data, AudioSet/FMA background audio) ships with or is needed by the final model — that's training-only, stays on Colab, already discarded.

### Integration (done same night, 2026-09-01 late) — pending live voice test
Installed `openwakeword` in the main project's `.venv` (Python 3.14) — **installed cleanly, no compatibility issues at all**, unlike the fragile training-time dependency chain in Colab (that chain's pain was almost entirely from the *training* packages — speechbrain, audiomentations, onnx2tf, etc. — not from openWakeWord's own runtime/inference dependencies, which are just `onnxruntime` + `scipy` + `scikit-learn`, all lightweight).

- Model files moved into the repo at `turion/wake_word/models/hi_si_su.onnx` (203KB) and `.tflite` (207KB, kept for a possible future ARM deployment even though unused today) — **had to fix `.gitignore`**: the existing broad `models/` rule (meant for large re-downloadable Whisper-style models) was silently excluding this small, non-reproducible trained model too; added a `!turion/wake_word/models/` negation.
- `openwakeword.utils.download_models()` fetches required preprocessing models (`melspectrogram.onnx`, `embedding_model.onnx`) into the package's own resources folder on first use — not bundled with the pip package itself, easy to miss.
- New module `turion/wake_word/listen.py`: `preload()` loads the model at startup (same pattern as STT/TTS preloading); `wait_for_wake_word()` opens a continuous `sounddevice.InputStream` (int16, 16kHz, 1280-sample/~80ms chunks — openWakeWord's expected format) and blocks until the "hi_si_su" prediction score crosses 0.5.
- `turion/main.py` updated: `input("\nPress Enter to talk...")` replaced with `wait_for_wake_word()` — TURION is now designed to run always-on, triggering on "Hi Sisu" instead of a keypress. Verified the whole module imports and the wake-word model preloads without error.

**Not yet done: live voice validation.** Everything above was verified structurally (imports clean, model loads, `predict()` returns scores on dummy audio) but **not yet tested against a real spoken "Hi Sisu"** — that needs the builder's own voice and can't be done by Claude alone. Also unverified: whether the 0.5 detection threshold is well-tuned (the model was trained with only 100 examples per the notebook's `number_of_examples` slider, well below the recommended 1,000-50,000 — may need retraining with more examples, or threshold adjustment, if it proves too trigger-happy or too unresponsive in practice), and whether there's an awkward handoff gap between the wake-word listening stream closing and the actual command-recording stream opening (two separate `sounddevice.InputStream`s, opened sequentially).

### Live voice testing (2026-09-02 morning) — worked, found and fixed several real issues
The builder tested live and it **worked end-to-end** — "Hi Sisu" reliably triggered listening, through several rounds of real conversation. Reviewing `logs/conversations.jsonl` after each attempt (a fast, effective debug loop — actual transcribed text + actual reply, both visible without re-listening to audio) surfaced a chain of real bugs, all fixed in `turion/brain/claude_client.py`:

1. **Replied in Hindi instead of Marathi** by default, especially for short/ambiguous transcriptions. Fixed by explicitly stating "reply in Marathi by default" in the system prompt, and — instead of guessing at unclear input — asking Claude to say the input was unclear and request a repeat.
2. **Emoji in replies got mispronounced by Piper** — the Marathi-only voice tries to sound out emoji characters, producing garbled audio the builder described as something like "smiling face" sounds. The system-prompt instruction not to use emoji wasn't reliably followed (Haiku is a small/cheap model), so added a regex backstop in `think()` that strips emoji from every reply before it's logged or spoken, regardless of what the model outputs.
3. **English brand/website names in Latin script mid-Marathi-sentence** (e.g. "Weather.com", "Google Weather") — same mispronunciation problem as emoji, since the Marathi voice can't read Latin script correctly. Fixed via system-prompt instruction: spell English loanwords phonetically in Devanagari instead, and describe actions rather than naming specific Latin-script apps/sites.
4. **Assistant introduced itself as "TURION"** rather than "Sisu" — builder wants the spoken persona to match the wake phrase ("Hi Sisu"), with TURION reserved as the name of the overall project/robot. Fixed via system prompt: "You are Sisu... introduce yourself as Sisu in conversation."
5. **Hallucinated a wrong date** ("December 12, 2024") when asked "what's today's date" — LLMs have no built-in clock; the actual system prompt sent had never included the real date. Fixed by appending the real current date/time (`datetime.now()`, system local time) to the system prompt on every `think()` call.
6. **The wake word itself sometimes got captured as the "command"** (e.g. transcribed text came back as literally "हय शिसु") — root cause was user behavior, not a bug: pausing after saying "Hi Sisu" instead of continuing straight into the actual question. Documented as a usage note (say the wake phrase and the question in one breath) rather than a code fix, though see the "awkward handoff gap" open question above — still not fully ruled out as a contributing factor.

**Bonus feature added the same session:** Hindu Panchanga (tithi/nakshatra/yoga/karana/vaara) via the `jyotishganit` library (`pip install jyotishganit` — clean install, no dependency drama, unlike the earlier astrology-adjacent library evaluation below), calculated for Pune coordinates as a Marathi-speaker approximation, cached per calendar day (the calculation takes a few seconds), appended to the system prompt alongside the date. Confirmed working live — correctly answered "what's today's tithi."

**Speed/smoothness tuning (same session, builder-requested):** `record_until_silence()`'s default `silence_duration` reduced 1.5s → 1.0s (shorter fixed pause before STT starts); system prompt tightened to ask for 1-2 sentence replies by default (longer replies cost more spoken-aloud time); `max_tokens` capped at 150 (was 300) to bound worst-case latency/cost. STT transcription time itself (~8s observed for one turn) is CPU-hardware-bound on this no-GPU laptop and wasn't addressed — consistent with the project's already-accepted hardware constraint.

**Comparison libraries considered for Panchanga, not used:** `drik-panchanga` (low commit count, Windows install undocumented — same risk pattern as several fragile old libraries fought this session) and `PyJHora` (34MB, requires manually copying ephemeris files from GitHub post-v3.6.6 — exactly the kind of manual-setup friction this session kept hitting elsewhere). `jyotishganit` avoided both problems.

---

## Cost Summary (Software/API side only — hardware costs are itemized per phase above)

| Item | Type | Notes |
|---|---|---|
| Claude Pro/Max subscription | Fixed monthly (~$20+) | For the builder's own personal chat use only — **cannot** be used to power TURION's code; not usable via API |
| Claude API | Usage-based (pay-per-token) | Required for TURION's actual "brain" calls from code. Model pricing (per million tokens, input/output): Haiku 4.5 ~$1/$5, Sonnet 5 ~$2/$10, Opus 5 ~$5/$25 |
| Whisper (Speech-to-Text, English) | Free, local | Open-source, runs on-device |
| AI4Bharat IndicConformer (Speech-to-Text, Marathi) | Free, local | Open-source, runs on-device — chosen over paid cloud STT for privacy (see decision above) |
| YOLO / face detection | Free, local | Open-source |
| TTS — pyttsx3 (English), Piper (Marathi/Hindi) | Free, local | Paid alternatives (ElevenLabs, OpenAI TTS, Google/Azure) exist if quality needs to improve later |

**Estimated monthly API cost by usage level (Claude Sonnet, illustrative):**
- Light testing (~20–30 interactions/day): ~₹150–250/month
- Moderate testing (~50–100/day): ~₹600–1,200/month
- Intensive dev/testing (~150–300/day): ~₹2,000–4,000/month
- With Haiku instead of Sonnet: roughly half of the above
- A well-designed **event-driven** 24x7 system (only calling the API when a real interaction happens, not continuously) is estimated at ~₹1,500–6,000/month for typical home use — a naive design that sends every camera frame/audio second to the API could run into ₹50,000+/month and should be avoided entirely

**Cost-control techniques:**
- Use the cheapest model (Haiku) by default; upgrade to Sonnet only where reasoning quality genuinely matters
- Prompt caching for repeated system prompts (large savings on repeated context)
- Batch API for any non-real-time bulk processing (50% cheaper, not usable for live conversation)
- Keep all classification/detection work on free local models; reserve the paid API strictly for genuine reasoning/conversation

## Business Considerations
- Because the builder has no software background, a sustainable path to a sellable product requires either: (a) a technical co-founder, (b) hiring freelance developers for production-quality work once a prototype is validated, or (c) the builder learning enough basics to evaluate others' work — "having someone else build 100% of it with no understanding" is not a durable business model
- Code generated with AI assistance (Claude Code, etc.) is not automatically proprietary or exclusive — differentiation will need to come from the specific integration, hardware, execution, and business relationships, not from the existence of the code alone
- The humanoid/service robotics market is large and fast-growing (independent market research estimates roughly 28–38% CAGR through the early 2030s across several sources), but it is also capital-intensive and dominated by a handful of large players — a realistic entry point for an individual/small team is a narrow, specific software/integration niche rather than competing directly on full humanoid hardware
- Decision was explicitly made to keep TURION scoped to legitimate household/task-automation use cases only — not to build alternate-use variants of the product


## Immediate Next Step
Build and validate **Phase 1** (Voice Assistant) end-to-end before starting any other phase. A detailed, standalone project brief for Phase 1 has already been prepared for use with Claude Code.

*(Status as of 2026-08-30: mic input and English STT are working; Marathi STT (IndicConformer) is built but not yet validated against real speech; Claude API and TTS are not yet connected/tested. See `Doc/project_status.md` for the live checklist.)*