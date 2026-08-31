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
- **AI compute board (only needed once this moves off the laptop):** Raspberry Pi 5 (₹8,000–10,000) for lighter AI workloads, or NVIDIA Jetson Orin Nano (₹25,000–35,000) if heavier on-device vision processing is needed

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
- **Mixed-language text is split by script per word** (`_split_by_script` in `speak.py`) and each chunk is routed to the right engine — e.g. "मी TURION आहे" speaks "मी" and "आहे" in the Marathi voice and "TURION" in the English voice, rather than the whole sentence going through one engine (which mispronounces whichever language it doesn't match). Marathi vs. Hindi still can't be auto-distinguished from Devanagari text alone (same open problem noted under STT) — Devanagari defaults to Marathi; pass `lang="hi"` explicitly when the text is known to be Hindi.
- **Roads not taken:**
  - **WinRT** (`Windows.Media.SpeechSynthesis`) — the modern Windows voice API that could reach the OneCore Hindi voice installed via Settings (invisible to classic SAPI/`pyttsx3`/`win32com`, confirmed by direct query). Got a working proof-of-concept (`winrt-Windows.Media.SpeechSynthesis` + reading the raw PCM stream and playing it via `sounddevice`, since `MediaPlayer` doesn't work reliably from a plain console script), but abandoned once Piper turned out to have an actual **native Marathi** voice available — better than Hindi-reading-Marathi regardless of API. Packages uninstalled.
  - **AI4Bharat Indic Parler-TTS** (`ai4bharat/indic-parler-tts`) — a proper Marathi-trained generative TTS model, likely the best quality option, but **incompatible with this setup**: it pins `transformers<=4.46.1`, which needs `tokenizers<0.21` — an old version with no Python 3.14 wheel, and its Rust source build fails (PyO3 doesn't support 3.14 yet). Installing it would also have downgraded the already-working `transformers` used by IndicConformer (STT), risking breaking that. Not revisited unless Python is downgraded or PyO3/tokenizers adds 3.14 support.
- **Model loading is slow** (~35s for STT, ~5s for TTS, on this no-GPU CPU) — not a bug, just the cost of 600M+ parameter models on this hardware. Fixed by preloading both models at `turion/main.py` startup (`preload()` functions in `transcribe_indic.py` / `speak.py`) instead of on first use, so the delay happens once up front with a clear "Loading..." message rather than confusingly mid-conversation. Per-turn latency after that is small (STT ~0.36x real-time, TTS ~0.16x real-time) — most of what feels like "lag" during stub-mode testing was actually just the stub reply's own spoken length, not processing overhead.

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