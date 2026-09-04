# TURION — Session Log

Log of every Claude Code working session on this project: date, time, what was discussed/done, and what's next. Newest entry on top.

---

## 2026-09-04, 16:00–18:40

**Session:** Physical embodiment design — from full humanoid ambition down to a real, printable Sisu head STL
- Builder saw a GPT-generated full bipedal "SISU Humanoid Companion" concept (40-50 DOF, dexterous hands, LiDAR) and initially wanted to build toward it. Explained why that's out of reach for a solo hobbyist (real ones are $100M+ company R&D; cheapest mass-produced humanoid still runs ₹15-75 lakh) — reconfirmed it stays Phase 6's long-term aspiration, not a near-term build.
- Researched a "realistic silicone face" alternative the builder floated: genuine hyper-realistic silicone masks (ImmortalMasks/SPFX-tier) are real but niche/international, ~₹68,000-85,000+, custom-order with ~6-week lead time — vs. cheap ₹700-4,000 "realistic" masks on Indian Amazon, which turned out to be latex costume masks, not true silicone. Flagged the real trade-off either way: no motors means a fully static face (no blinking/lip movement), which can look more uncanny on a hyper-realistic face than a stylized one.
- Builder chose to scope down to **just the face** (not a full body) in the already-designed stylized "Sisu" cartoon style, mounted on the pan-tilt turret neck from the previous session. Confirmed head size at **16cm tall** (compact end of a 15-18cm range the builder picked, vs. a real head's ~22-23cm), since it only needs to fit a small servo turret.
- Built an actual printable **STL model**, not just a 2D concept: `hardware/sisu_head/build_sisu_head.py` (Python, `trimesh`+`manifold3d`, installed in an isolated venv so it never touched the main TURION `.venv`) constructs the head as a boolean-cut ellipsoid shell — two eye holes (camera + dummy lens), two ear bumps with mic holes, a mouth slot for the speaker grille, and an open bottom sized for the neck mount. Exported, confirmed **watertight**, ~150g in PLA. Rendered a 4-angle preview to sanity-check the shape before handing it over. Output lives in `hardware/sisu_head/` (`sisu_head.stl`, `build_sisu_head.py`, `sisu_head_preview.png`).

**Next session should start with:** get `sisu_head.stl` actually printed (local Fablab or a print-on-demand service), then source real camera/mic/speaker modules to confirm the hole sizes in the script match before final assembly. Also still open from before: live-test presence-triggered listening, webcam purchase decision, Phase 3 Memory, Sarvam AI TTS trial.

---

## 2026-09-04, 15:40–15:53

**Session:** Built presence-triggered listening — the top item from yesterday's "camera+mic future ideas" list
- Clarified three design decisions with the builder before writing code: (1) trigger on *any* face, known or unknown, not known-only — builder picked the broader option; (2) on trigger, Sisu speaks first to grab attention (not silent recording) — builder picked this over jumping straight to recording; (3) a 2-minute per-person cooldown so someone standing in frame doesn't re-trigger every poll.
- Built `turion/vision/presence.py` (polls the camera every 4s for a face while idle, applies the cooldown, returns the scene text) and `turion/activation.py` (races it against the wake word — made `wait_for_wake_word()` cancellable via a `stop_event` param in `turion/wake_word/listen.py` so only one side ever holds the mic). Refactored `scene_context.py` to expose `get_scene_state()` (name + text) alongside the existing `get_scene_context()` (text only), so presence detection's cooldown key doesn't have to re-parse the Marathi sentence.
- On a presence trigger, deliberately reused `think()`'s existing known/unknown `scene_line` logic (built 2026-09-03 for conversational vision) by feeding it a synthetic "nobody's spoken yet, greet them" prompt instead of writing a second hardcoded greeting — keeps the two activation paths (wake-word turn vs. presence turn) from drifting apart in tone/behavior.
- Wired into both `turion/main.py` and `turion/gui/app.py`. Syntax-checked (`py_compile`) but **not live-tested** — this needs the phone camera and mic running together to confirm the race/cancellation works as designed, and to gauge whether continuous 4s camera polling is too heavy for this CPU-only laptop's already-running wake-word listener.

**Next session should start with:** live-test presence-triggered listening for real (say "Hi Sisu" and separately just step into frame, confirm both work and don't fight each other for the mic), then the still-open items from before (webcam purchase, Phase 3 Memory, Sarvam AI TTS trial).

---

## 2026-09-03 23:00 – 2026-09-04 15:40

**Session:** Diagnosed and ordered a replacement laptop battery; narrowed down the camera-hardware decision; designed a motion-triggered pan-tilt camera turret concept, including a friendly robot-face design direction
- **Laptop battery diagnosed as genuinely failing:** `powercfg /batteryreport` showed Full Charge Capacity at 11,877 mWh against a 48,840 mWh design capacity — only ~24% of original, stuck at 8% for days. Laptop is a Dell Inspiron 3537; the battery's Windows-reported "name" (49VTP27J) turned out to be a serial-like identifier, not the actual interchangeable part number (learned this the hard way after it didn't match any listing's compatibility list) — the real match key is the laptop model itself plus the genuine part-number family (XCMRD, FW1MN, MR90Y, etc., confirmed via multiple listings).
- Priced a repair alternative (individual 18650 cell replacement, 6 cells needed) before recommending against it: unbranded loose cells run ~₹116 each (~₹700 for 6, before labour), branded cells (Samsung 3000mAh) ~₹279 each (~₹1,674 for 6 — already *more* than a full replacement pack) — plus real safety risk in DIY lithium pack disassembly. Full replacement pack was clearly the better call.
- Caught a real near-miss: a battery link the builder found himself (MYLAP J1KND) had fast delivery but was for a completely different, incompatible Dell Inspiron sub-series (N5010/N5030/N5110/3520/M5110/N4050) — flagged before purchase rather than after.
- Compared aftermarket (Lapcare XCMRD, ₹1,627, 1-year warranty, cell brand undisclosed — normal for this price tier) against genuine Dell Original (Flipkart, ₹1,939, only 90-day warranty despite being genuine) — recommended the aftermarket option specifically because of the warranty gap, a real counter-intuitive finding worth remembering. **Builder ordered it**, arriving the next day.
- **Camera hardware:** compared phone-stand options (Ambrane/Elfora ~₹250-300, then reconsidered for insufficient height/grip, found a taller clamp-style overhead arm mount ~₹795) against buying a dedicated USB webcam outright — leaned toward the webcam given today's recurring IP Webcam server friction. Between Kreo Owl Lite (₹1,999, autofocus, 400-day warranty, no night vision) and BigPassport (₹1,499, wider FOV, night vision, no autofocus, 6-month warranty) recommended Kreo for the autofocus (matters more for face-recognition accuracy than night vision, which is a rare-use edge case for a normally-lit home). Checked five links the builder found himself — three were dead ends (720p, 0.3MP, unrated "Generic" brand). No final webcam purchase confirmed yet.
- **Camera+mic future ideas discussed** (not built): presence-triggered listening (skip waiting for the wake word once a known/any person is detected nearby), speaker detection via lip movement when multiple people are in frame, combined facial-expression + voice-tone emotion sensing, and synced video+audio session recording. Presence-triggered listening flagged as the most immediately buildable once the camera has a fixed mount.
- **Designed a motion-triggered pan-tilt camera turret concept** (idea from the builder: something that detects sound/motion and physically turns the camera toward it): PIR motion sensor → ESP32 → 2x SG90 micro servo (pan + tilt) turning the camera toward detected movement. Priced the real parts (all in stock on Amazon India): 2x SG90 ~₹250-310, pan-tilt bracket ~₹150-240, PIR sensor ~₹75-250, ESP32 ~₹400-620 — total ~₹1,000-1,700. A true sound-direction version (mic array with direction-of-arrival, e.g. ReSpeaker) was priced too but isn't readily available through mainstream Indian retail (Amazon/Robu both came up empty) — parked as a future import-only upgrade, motion-only is the practical starting point.
- **Servo vs. stepper motor, decided: servo.** For this light a load (a phone/webcam), a stepper motor's extra precision/torque over a wide range is unneeded complexity and cost (needs a separate driver board, more wiring, manual step-tracking) — servos give direct "go to this angle" control over one wire and are the standard choice for hobby pan-tilt camera mounts. Consistent with Phase 4's existing servo choice (MG996R) for the arm.
- **Designed a "Sisu face" concept for the turret** — the builder rejected an initial technical/mechanical-bracket-looking design and asked specifically for an anthropomorphic robot face: two round eyes (one is the actual camera, both drawn identical/symmetric), two ear-shaped mic housings on the sides, and a rounded mouth that doubles as the speaker grille — sitting on a deliberately plainer/more mechanical pan-tilt neck below, so the friendly face contrasts with the functional base. This is now the working visual-identity direction for TURION/Sisu's physical embodiment, not just a camera-mount bracket.
- **Process lesson (not a TURION fact, but worth remembering for future sessions):** a design widget shown via a spawned subagent's own tool call does not become visible to the user in the parent conversation — `show_widget` must be called directly in the main turn, not delegated.

**Next session should start with:** finalize the webcam purchase (or confirm sticking with the phone) now that the battery situation is resolved, then either start building the pan-tilt turret (parts list is ready) or continue Phase 3 (Memory) / the still-outstanding Sarvam AI TTS trial.

---

## 2026-09-03, ~09:27–23:00

**Session:** Face detection + named recognition built, synced into the live voice loop, and given real conversational behavior; a business idea explored at length on the side; started shopping for real camera/stand hardware
- Chose **InsightFace** over `face_recognition` for the same reason YOLO-World was chosen over `dlib`-adjacent options earlier: `face_recognition` depends on `dlib`, which has no Windows wheels and needs compiling from source — InsightFace installed clean and runs on `onnxruntime`, already a project dependency. Built `turion/vision/face_detection.py`, live-tested against the phone camera: 88.4% confidence on a real face, same `detect_auto_orient()`-style 4-rotation handling as object detection.
- Built `turion/vision/face_recognition_db.py` for *named* recognition — stores each person as multiple angle-embeddings (front/left/right ~45°) in a local, gitignored JSON file (`data/known_faces.json`, biometric data, kept private same as `logs/`), matching new faces against all stored angles via cosine similarity. Discussed and set the realistic scope explicitly: front-to-~45° works, a full 90° side profile is genuinely hard for any 2D face recognition system and wasn't attempted. `tools/enroll_and_test_face.py` built and ready but the actual enrollment run was deferred.
- **Long tangent, kept out of the main thread:** builder asked about running "continuous AI" cost (answered with real per-day/month numbers from the day's own measured token usage), then about self-hosting a custom LLM (not worth it at this scale — hardware payback would take 4-7+ years vs. Claude's ~₹1,000-1,500/month actual cost), then revealed a real, separate ambition: a powerful multi-user (5-person) desktop, which turned into a full business-idea exploration — renting GPU compute time to small YouTube/Instagram creators who can't afford proper editing hardware. Worked through it properly: a ₹3.3-4L build (RTX 4090 24GB + Ryzen 9 9950X + 128GB RAM, priced against real 2026 India retail), the concurrency ceiling (5-8 users for light CPU-bound editing, 1 at a time for GPU-bound rendering), a pivot from hosting customer footage (real liability) to compute-only with auto-deleting scratch storage, and a pivot from a flat ₹8,000/month rate (prices out the actual target customer) to per-hour billing (~₹100-150/hr, landing under ₹1,000/month for a light user) — each step was the builder's own correction, not offered unprompted. Written up as a separate artifact ("Render Slot") per the builder's explicit request to keep it out of TURION's own session so the two don't tangle.
- Tangent continued into a cheaper MVP build (RTX 4060 Ti 16GB + Ryzen 7 9700X + 64GB RAM, ~₹1.3-1.9L one-time incl. power backup/internet setup, ~₹6-7K/month running) and real employee-discount research: AMD's own program is ~20-25% but only helps the CPU (not the GPU, which is NVIDIA); NVIDIA's own employee discount is only ~10% and reselling to non-employees is against their policy, so that route is effectively closed unless the builder works there directly.
- Learned and saved to memory: builder's name is **Tushar Ingavale** (inferred first from their email, confirmed directly).
- **Closed the loop on face recognition**, live: enrolled Tushar via the phone's front camera at all 3 angles (front 85.2%, left 78.3%, right 57.5% detection confidence), then a fresh test photo was correctly recognized as "Tushar" at 86.5% similarity.
- Builder sent 7 real photos of himself (different times/settings) directly in chat for a batch recognition test — 5 matched (41-66%), 2 didn't; traced to a genuinely different hairstyle in those two (one fully shaved, one short hair) from how he looked at enrollment — a real, general face-recognition limitation, not a bug, and not worth fixing right now (declined re-enrollment). Also ran a negative-match test with a photo of his mother — correctly NOT recognized as "Tushar" — with an explicit, respected privacy boundary: her photo was never displayed or sent to any external service (including Claude's own vision API, which was offered but declined since it would leave the laptop), only the local match result was reported.
- **Synced the camera with the live voice loop**, live-verified: `turion/vision/scene_context.py` gives Sisu a one-line "who's in front of the camera" glance each turn. First version did both face + object detection and measured 8.66s (too slow, phone still handheld, each detector needs its own 4-rotation orientation check) — cut to face-only (~4.5s warm) and moved the fetch into a background thread that starts the moment the wake word fires, running parallel to recording+STT in both `main.py` and `gui/app.py`, so the cost is mostly hidden rather than added on top of every turn. Confirmed end to end: camera recognized "Tushar", and Sisu's reply naturally opened with "नमस्कार तुषार!" using the injected context.
- **Gave Sisu real conversational vision behavior**, requested directly by the builder: (1) a `describe_camera_view` tool Claude can call (via Anthropic's tool-use API) when someone actually asks what something is, fetching a fresh frame and getting a real description rather than a bare YOLO label — verified with a real desk-scene description. (2) Known vs. unknown person handling — address a known person by name, ask an unknown one their name/language *in Hindi specifically*, then continue in whatever language they respond in. The first version of the name-greeting instruction lived as a static paragraph in `SYSTEM_PROMPT` and was unreliable (skipped the name in ~1 of 3 replies once the tool-use instructions were added alongside it); rewriting it as a per-turn directive built fresh right next to the scene fact fixed it completely (3/3 and 2/2 correct in testing afterward) — a real, measured lesson about prompt structure: burying an instruction among many others makes a small/cheap model less likely to follow it, keeping it local to the relevant fact makes it reliable.
- Went shopping for real hardware to fix today's recurring friction (the IP Webcam server going down repeatedly, hand fatigue from holding the phone, inconsistent photo sharpness): compared phone-stand options (settled on needing taller/sturdier clamp-style over a simple flat desk mount), then reconsidered the whole phone-based approach — priced real USB webcam options instead (Kreo Owl Lite ₹1,999 with autofocus/400-day warranty vs. BigPassport ₹1,499 with wider FOV/night vision but no autofocus and only 6-month warranty), checked five webcam links the builder found himself (three were dead ends — 720p, 0.3MP, and an unrated "Generic" brand — two were reasonable). No final hardware purchase decided yet.

**Next session should start with:** deciding on camera hardware (USB webcam vs. keep the phone + get it a proper stand) to resolve today's recurring friction, then Phase 3 (Memory — a real local database, beyond the single JSON file used for faces today), re-adding object detection to the scene-sync once the camera is fixed in position (cheaper without the 4x-rotation cost), or the still-outstanding Sarvam AI TTS trial (deferred three sessions running now).

---

## 2026-09-02, ~20:12–22:46

**Session:** Kicked off Phase 2 (Vision) — camera input, then a full real-world comparison of object detection options
- Built `turion/vision/camera_input.py` (`get_frame()`/`preload()`, reading the phone's IP Webcam `/shot.jpg` snapshot, address from a `TURION_CAMERA_URL` env var) and a first `turion/vision/object_detection.py` (plain YOLOv8n). Both live-tested against the real phone camera.
- **Orientation bug:** the phone's frames came out rotated differently shot to shot (upright, 90°, 180° all seen from the same phone across a debugging session) — no fixed rotation could work, and IP Webcam has no orientation-lock setting. Fixed with `detect_auto_orient()`, which tries all 4 rotations per frame and keeps whichever orientation YOLO is most confident about.
- **`frame=None` bug:** briefly got what looked like a real detection ("bus", "person") when the phone was actually unreachable — traced to `ultralytics` silently running on its own bundled demo image when passed `frame=None` instead of raising. Both detect functions now raise explicitly on `frame=None`.
- Builder caught a real accuracy gap: a black, insulated-flask-shaped bottle on a shelf was never detected at any confidence — plain YOLOv8n is stuck with COCO's 80 fixed classes and this object didn't match closely enough. This turned into a full, evidence-based comparison exercise rather than a quick fix:
  1. **YOLO-World** (open-vocabulary, same `ultralytics` package, no new heavy dependency) — small size still missed the bottle at first.
  2. **Moondream** (`vikhyatk/moondream2`, free/local, CPU-only 2B-param vision-language model) — considered as a middle option, but hit a known bug (`transformers` >= 5 incompatibility with its remote code) that would need downgrading `transformers` to 4.x — too risky since the existing, working Marathi STT (IndicConformer) also depends on `transformers`. Set aside, documented in `tools/test_moondream.py`.
  3. **Claude vision** — asked to list every object in the same photo; got a rich ~20-24 item natural-language list each time, but never correctly named the black bottle across three separate attempts (best guess: "spray can"), at ~1600+200 tokens per single image.
  4. **A direct small/medium/large/extra-large YOLO-World comparison, all on the identical photo** — motivated partly by whether investing in bigger models now is worth it for the eventual Jetson-based robot (bigger models tested today on this CPU-only laptop will just run faster later on Jetson's GPU, no rewrite needed — same reasoning as the original Jetson-vs-Pi decision). Confidence on the black bottle: small 76.7%, **medium 93.6% (highest)**, large 81.9%, extra-large 36.1% (worst, despite being the biggest/slowest). "Bigger is better" was a real testable assumption and it was wrong.
  5. Also found that more **specific class vocabulary** ("black steel bottle"/"insulated flask" instead of just "thermos"/"flask") was what actually got the object caught at all — open-vocabulary detection is sensitive to exact phrasing, not just model size.
- **Result:** `object_detection.py` now uses YOLO-World medium as the production default, with a curated `CLASSES` list. Confirmed final architecture: local YOLO-World runs continuously for free/instant detection; Claude vision stays reserved for when a conversation actually needs deeper reasoning about what's seen — the "peripheral vs. focused vision" design from earlier in the day, now backed by real measured numbers.
- Also noticed but not yet acted on: handheld test photos were visibly blurry vs. one steadier shot that came out sharp — motion blur, expected to resolve once the phone is on a permanent stand rather than handheld.
- All of the above (5 tool scripts, 2 production modules, and full writeups) committed and pushed across several commits; `project_status.md` and `project_info.md` both updated with the full comparison story.

**Next session should start with:** Phase 2 (Vision) — face detection/recognition (InsightFace or face_recognition), continuing from the object detection just built. Sarvam AI's TTS trial (deferred from the previous session) is still outstanding too.

---

## 2026-09-02, ~14:12–20:12

**Session:** Marathi voice-quality troubleshooting — tried tuning Piper, then researched cloud alternatives
- Builder asked how to make Sisu's pronunciation clearer. Checked `speak.py`: already on Piper's best available quality tier for Marathi (`mr_IN-google-medium` — no higher-quality Marathi model exists in Piper's voice repo), using `speaker_id=8` with no speed/expressiveness tuning.
- Built `tools/test_voices.py` (+ `run_voice_test.bat`) — plays all 9 speakers in the Marathi voice model back to back on a real test sentence, then compares 3 speaking speeds on the chosen one, so the builder could judge by ear rather than guessing from code. Builder picked speaker_id 5 as clearest; applied to `speak.py` and pushed.
- Builder then reported none of the 9 speakers actually sounded good — Piper's single Marathi voice model has hit its ceiling (confirmed via Hugging Face: no alternate Marathi dataset/quality tier exists in `rhasspy/piper-voices`).
- Researched paid cloud TTS as the remaining lever, with real pricing: Azure (~₹135/100K chars, general-purpose Marathi voices), Google Cloud TTS (~₹135/100K chars), ElevenLabs (~₹850/100K chars, strong globally but not Indic-specialized), OpenAI TTS (~₹125/100K chars, voices tuned for English, "supports" Marathi but not trained for it). **Recommended Sarvam AI (Bulbul v3)** instead — an India-specific TTS company, ~₹300/100K chars, trained specifically on Indian languages and code-mixed speech (handles English words inside Marathi sentences in one generation pass — directly the pronunciation problem this project has hit repeatedly), and ranked highest for naturalness in an independent blind listening study against ElevenLabs and Cartesia. ₹100 free credit available to trial at zero cost.
- Also discussed building a fully custom/self-trained voice model instead of any of the above — recommended against it for this project's scale: needs 10-20+ hours of clean single-speaker studio audio (or a lower-control free dataset), real GPU training cost, and likely many days of dependency/debugging pain (matching the wake-word Colab training experience), for a result not obviously better than what Sarvam already offers off-the-shelf for ~₹300-500/month.
- Builder decided to defer the actual Sarvam trial to next session, paired with starting Phase 2 (Vision/camera) rather than doing it now.

**Next session should start with:** Phase 2 (Vision) — object/face detection via camera — together with trialing Sarvam AI's TTS using its free credit.

---

## 2026-09-02, ~09:27–14:12

**Session:** Built the desktop app (mobile-app-style window, replacing the black terminal), fixed its black-window bug, then found and fixed a deeper class of festival-date bugs the user's live testing surfaced
- Built `turion/gui/index.html` (dark theme, status orb + conversation bubbles) and `turion/gui/app.py` (pywebview window running the same listen→transcribe→think→speak loop as `main.py` in a background thread, updating the UI via `evaluate_js`). Preserves the required "load once, stay running, only visually react after Hi Sisu" architecture — no repeated reloads between turns.
- **Bug: window rendered solid black.** Two causes, both fixed: (1) `webview.create_window(url=str(HTML_PATH))` passed a raw Windows path, not a valid URL — fixed with `HTML_PATH.as_uri()`. (2) `.app { height: 100vh }` combined with `overflow: hidden` on `html/body` is a known WebView2 quirk where `100vh` can compute to 0 inside the embedded webview — fixed by using `height: 100%` to match the parent chain instead. User confirmed the UI now renders correctly and a full live conversation worked end-to-end in it.
- **Live in the new app, user caught a real date bug:** Sisu said the next Ekadashi was 6 September 2026; the real date is 7 September. Root cause: the "tithi kshaya" safety net added last session (checking sunrise + 9 AM/3 PM/9 PM as a fallback) was too eager — Ekadashi began at 9 PM on the 6th, so the 9 PM checkpoint flagged the 6th even though the correct traditional rule (tithi at *sunrise*) says the 7th. The net was meant only to catch true kshaya days (a tithi that never touches any sunrise); applied unconditionally, it over-fired on the completely normal case of a tithi simply starting in the evening. Fixed by making it strictly a fallback: search sunrise-only across the whole window first, and only use the intraday net if that finds nothing at all in the window.
- That fix alone changed Sankashti Chaturthi from 29→30 September — which directly contradicted the user's own real-world correction from last session ("chaturthu 29 sep la aahe"). Investigating why revealed the actual issue: **not every tithi-based observance uses the same reference time of day.** Cross-checked every festival in the list against real published 2026 dates via web search and found several were quietly wrong under a sunrise-only rule:
  - **Ekadashi** — correctly sunrise-vyapini (confirmed 7 Sep now matches).
  - **Sankashti Chaturthi** — actually moonrise-vyapini (fast breaks after sighting the moon that evening). Added a real astronomical moonrise calculation (`almanac.risings_and_settings` for the Moon, paralleling the existing sunrise function) since moonrise — unlike solar noon — shifts across the whole 24h clock through a lunar month, so no fixed hour is a safe proxy. Fixed: 29 September, matching the user's original correction and the published "Angarki Chaturthi" (Tuesday) sources.
  - **Ganesh Chaturthi** — actually madhyahna-vyapini (midday; puja happens at midday per tradition). Sunrise-only gave 15 Sep; real date is 14 Sep. Fixed with a fixed-noon check (solar noon barely shifts through the year, so unlike moonrise this proxy is safe).
  - **Dussehra/Vijayadashami** — actually aparahna-vyapini (afternoon, the 3rd of 5 traditional daylight divisions). Sunrise-only gave 21 Oct; real date is 20 Oct. Fixed with a real sunrise+sunset-based afternoon calculation (not a fixed clock hour, since afternoon clock time shifts with day length).
  - **Diwali/Lakshmi Puja** — actually pradosh-vyapini (shortly after sunset). Sunrise-only gave 9 Nov; real date is 8 Nov. Fixed using real computed sunset + 1 hour.
  - **Holi** — a different kind of bug: the code was searching for the *Purnima* tithi, which is actually Holika Dahan (the bonfire night), not the "Holi" most people mean (the color-play day, Dhulandi, one tithi later — Krishna Pratipada). Sunrise-search on the wrong tithi gave 3 Mar; fixed by searching for Krishna Pratipada instead, giving the correct 4 Mar.
  - Janmashtami, Raksha Bandhan, Navratri-start, and Gudi Padwa were re-verified and confirmed already correct under plain sunrise (Gudi Padwa specifically re-confirmed still resolving via the tithi-kshaya fallback, unaffected by any of the above changes).
  - All final dates cross-checked against real published 2026 sources: Janmashtami 4 Sep, Ganesh Chaturthi 14 Sep, Ekadashi 7 Sep, Sankashti 29 Sep, Navratri-start 11 Oct, Dussehra 20 Oct, Diwali 8 Nov, Holi 4 Mar, Gudi Padwa 19 Mar — all exact.
- This turned a one-line user-reported bug into a full audit of `turion/brain/festivals.py`'s astronomical assumptions — worth doing given the user's explicit, repeated insistence that fasting/festival-day accuracy matters (a wrong day means fasting or celebrating on the wrong day).

**Next session should start with:** Phase 2 (Vision) — object/face detection via camera. The desktop app and festival calendar are now both live-validated with nothing outstanding.

---

## 2026-09-02, ~08:19–09:27

**Session:** Built and debugged a computed Hindu festival calendar for Sisu, through two real accuracy bugs
- Live testing had shown Sisu hallucinating a specific (wrong) Ganesh Chaturthi date — same root cause as the earlier date hallucination, just extended to future festivals rather than today. Built `turion/brain/festivals.py` to compute real dates via `jyotishganit`'s direct panchanga API rather than trusting Claude's guess.
- **Bug 1 (caught immediately via web search verification):** first version's search windows were wider than one lunar cycle, so they could match a tithi's *previous* month occurrence instead of the intended one — Ganesh Chaturthi, Dussehra, and Diwali all came out ~29 days early. Fixed by narrowing every window under 29 days; re-verified against real published 2026 dates, most landed exact.
- User specifically flagged that Sankashti Chaturthi (a fasting day) was 1 day off, and pushed back on accepting that as fine — correctly pointing out fasting days matter more than casual festival dates (wrong day means fasting on the wrong day). This reprioritized chasing full accuracy rather than settling.
- **Bug 2:** switched the daily reference check from a fixed clock hour to the actual computed astronomical sunrise (Skyfield's `almanac.sunrise_sunset`) — the traditionally correct rule. This alone broke Gudi Padwa worse (jumped to the wrong *year*, 2027). Debugging revealed a real, documented phenomenon: "tithi kshaya" — a lunar day short enough to start and end within one solar day, missing every sunrise entirely (confirmed: "Shukla Pratipada" was skipped between Amavasya on 19 March and Shukla Dwitiya on 20 March 2026). Fixed with a pragmatic safety net: check sunrise, then 9 AM/3 PM/9 PM as a fallback.
- Final result confirmed against real published 2026 dates and the user's own knowledge: Gudi Padwa, Ganesh Chaturthi, Janmashtami, Dussehra, and Sankashti Chaturthi all exact. Raksha Bandhan remains 1 day off, accepted as a residual gap rather than chased further.
- Added `get_next_ekadashi_sankashti()` for the two recurring (twice-monthly/monthly) fasting observances, computed as "next occurrence from today" rather than a cached yearly list, since that's the actual shape of what a voice assistant gets asked.
- Discussed and declined switching to `drik-panchanga` for its built-in tithi end-time precision, given its undocumented/risky Windows install — judged not worth the risk for the accuracy gained, especially now that the sunrise+multi-check approach closed most of the gap anyway.
- Documented the full two-bug debugging story in `project_info.md` (useful if this is ever extended to more festivals or another region).

**Next session should start with:** The desktop-app UI redesign (mobile-app-style window instead of the black terminal) — discussed earlier this session, still not started. After that, Phase 2 (Vision).

---

## 2026-09-02, ~06:52–07:57

**Session:** Live-tested the wake-word integration — worked, and fixed a real chain of bugs found through actual use
- User ran `turion/main.py` and said "Hi Sisu" live — **it worked**: heard the wake word, recorded, transcribed, replied, spoke, went back to listening. First real always-on TURION conversation.
- Established a fast debug loop: read `logs/conversations.jsonl` after each attempt to see the actual transcribed text and actual reply, without needing to re-listen to audio or guess. This surfaced several real, fixable issues in quick succession:
  1. Replies defaulted to **Hindi instead of Marathi**, especially for short/unclear transcriptions — fixed via explicit system-prompt instruction, plus telling Claude to ask for a repeat on unclear input rather than guessing/giving a generic greeting
  2. **Emoji** (🙏, 😊, 👋) in replies got mispronounced by Piper's Marathi voice — user described the resulting audio as sounding like "smiling face" nonsense. The prompt instruction not to use emoji wasn't reliably followed (Haiku is small/cheap), so added a regex backstop that strips emoji from every reply before logging/speaking, independent of what the model does
  3. **English brand/site names in Latin script** (e.g. "Weather.com", "Google Weather") mid-Marathi-sentence — same mispronunciation problem, fixed via prompt instruction to spell loanwords phonetically in Devanagari and describe actions instead of naming specific Latin-script apps
  4. Assistant introduced itself as **"TURION"** — user wants it to say **"Sisu"** in conversation (matching the wake phrase), with TURION staying the name of the overall project. Fixed via system prompt.
  5. Assistant **hallucinated "December 12, 2024"** when asked today's date — LLMs have no built-in clock. Now appends the real current date/time to the system prompt on every call; confirmed correct afterward.
  6. Once, the wake word itself ("हय शिसु") got transcribed as if it were the command — traced to user pausing after saying "Hi Sisu" instead of continuing straight into the question; noted as a usage pattern, not fixed in code (though the possible stream-handoff-gap contributing factor from the integration doc is still an open question)
- **Detour:** user asked several conceptual questions about whether they could avoid API cost via local command routing (confirmed yes, matches the project's existing local-first principle, scoped as future Phase 5 work) and whether repeated testing "trains" Claude — clarified that Claude is a fixed, pre-trained model that doesn't learn from usage; what's actually happening is prompt/instruction engineering (this session's whole bug-fixing loop), and that persistent personalization would be Phase 3 (Memory), a local database, not model training
- **Added Hindu Panchanga** (tithi/nakshatra/yoga/karana/vaara) to Sisu's context, via `jyotishganit` (chosen over `drik-panchanga` and `PyJHora` after comparing — both of those had installation friction patterns matching this session's earlier fragile-library pain; `jyotishganit` installed clean). Calculated for Pune coordinates as a Marathi-speaker approximation, cached per calendar day. Confirmed working live.
- **Tuned for speed/smoothness** at the user's request: `record_until_silence()`'s silence-wait reduced 1.5s → 1.0s, system prompt now asks for 1-2 sentence replies by default, `max_tokens` capped at 150 (was 300). STT transcription time itself (~8s per turn observed) is CPU-hardware-bound and wasn't addressed.
- Documented everything in `project_info.md`/`project_status.md`, marking wake-word as fully live-validated (not just structurally verified) for the first time.

**Next session should start with:** Phase 2 (Vision) — object/face detection via camera. Phase 1, including wake-word activation, is now complete and validated with nothing outstanding.

---

## 2026-09-01, ~23:35–23:51 (continuing into overnight, unattended by user)

**Session:** Wired the trained wake-word model into TURION's main loop
- Brief detour first: user asked several questions about whether voice could control the whole laptop/other tools (via Claude Code directly, or via TURION+Claude API tools) — clarified Claude Code itself has no general desktop mouse/keyboard control (only within the Browser pane), and that full device/tool control for TURION is Phase 5 territory, best done as local rule-based command routing for simple actions (to save API tokens) with Claude reserved for genuinely conversational requests — consistent with the project's existing "local-first, paid API only for reasoning" principle. Documented as context but not started.
- User asked Claude to proceed with wake-word integration overnight while they slept, to test in the morning — found the downloaded model files in `Downloads\`, moved them into the repo at `turion/wake_word/models/`
- Installed `openwakeword` in the main project's `.venv` (Python 3.14) — installed cleanly with no compatibility issues, confirming the earlier Colab pain was almost entirely from *training*-specific dependencies, not openWakeWord's own lightweight runtime (onnxruntime + scipy + scikit-learn)
- Hit and fixed two small setup issues: the pip package doesn't bundle its required preprocessing models (melspectrogram/embedding — fixed via `openwakeword.utils.download_models()`), and the repo's `.gitignore` had a broad `models/` rule that was silently excluding the small trained wake-word model too (added a negation exception)
- Wrote `turion/wake_word/listen.py` (model preload + continuous-listening `wait_for_wake_word()`) and updated `turion/main.py` to replace `input("Press Enter to talk...")` with it — verified the whole thing imports and preloads without error, but **has not been tested against a real spoken "Hi Sisu"** — that needs the builder's own voice, first thing tomorrow
- Documented everything in `project_info.md`/`project_status.md`, including the known unknowns (whether the 0.5 detection threshold is well-tuned; the model was trained with only 100 examples, well below openWakeWord's recommended 1,000+, so retraining with more examples is the fallback if live detection quality disappoints)

**Next session should start with:** Run `turion/main.py` (or the Desktop shortcut) and say "Hi Sisu" out loud — confirm it actually triggers, and judge whether the sensitivity needs tuning. If it works, Phase 2 (Vision) is next.

---

## 2026-09-01, ~20:58–23:32

**Session:** Built a double-click launcher, added conversation logging, then trained a custom wake word ("Hi Sisu") through a long dependency-debugging marathon
- Added `run_turion.bat` + a Desktop shortcut so the builder doesn't need to manually open PowerShell/cd/type the run command each time
- Added `turion/conversation_log.py` — every turn (transcribed user text + Claude's reply) now appends to `logs/conversations.jsonl` (gitignored, personal content) so past conversations are reviewable later
- Builder asked for TURION to be always-on with a spoken wake phrase instead of "press Enter to talk". Researched wake-word engines: **Picovoice Porcupine's free tier for custom wake words was permanently discontinued 2026-06-30** ("no non-commercial tier planned") — ruled out immediately, not a close call. **openWakeWord** (fully free, open-source, runs 15-20 models simultaneously on a Raspberry Pi 3 core) was the clear remaining choice.
- Worked through picking the actual wake phrase with the builder — tried "TURION" itself first (pronunciation issues with "gy"-type sounds collapsing into "j" in the English-phoneme synthetic training pipeline meant candidates like "Gyanu" didn't work cleanly), considered Sisu (Finnish, meaning resilience/grit) vs. Gyanu (Sanskrit-rooted, meaning knowledge, but too close to a common Indian nickname — higher false-trigger risk) vs. a few Sanskrit alternatives (Dhriti, Chetana). **Landed on "Hi Sisu"** — clean pronunciation, "Hi" prefix reduces false-trigger risk like "Hey Siri" does. TURION stays the assistant's name; this is only the activation trigger.
- **Trained the model via openWakeWord's official Colab notebook** — meant to be a <1-hour, no-code process, but the notebook (last maintained ~April 2026) had drifted badly out of sync with Colab's current Python 3.13 environment. Walked through the Colab UI screenshot-by-screenshot (same pattern as the Anthropic Console and Windows settings work earlier) and fixed, in sequence: a PyPI package (`piper-phonemize-cross`) that no longer exists at all (swapped for the maintained fork `piper-phonemize-fix`); an unnecessary torchvision pin with no matching wheel; a stale-partial-install guard that kept skipping reinstall after failed attempts (needed explicit `rm -rf` between retries); `torch.load()`'s new `weights_only=True` default breaking two different old-format checkpoints in two unrelated packages; `pkgutil.ImpImporter` being removed in Python 3.12+ breaking `webrtcvad`'s `pkg_resources` import chain (monkey-patched); the system `pkg_resources` itself being fundamentally incompatible with Python 3.13 (worked around by patching `webrtcvad.py` to stop importing it entirely, since it was only used for a version string); and two separate `torchaudio` APIs (`set_audio_backend`, `info`) removed in the current torchaudio version, patched out of `torch_audiomentations`'s IO module (the second one replaced with an equivalent `soundfile.info()` call).
- **Training succeeded** — confirmed live via progress bar (`Training: 21% 2132/10000 [01:04<03:10, 41.35it/s]`). Final model downloaded: `hi_si_su.onnx` + `hi_si_su.tflite`, ~200KB each — confirms wake-word models are genuinely tiny regardless of the huge (~16GB) training data, which stays on Colab and isn't needed on the robot.
- User asked whether Claude could work through the night on the remaining integration work (mirroring the earlier Indic-TTS overnight session) — confirmed yes for the code/install/setup portions (installing `openwakeword` in the main `.venv`, writing the always-listening loop) but the live "does it actually trigger on my voice" test needs the builder specifically. Documented everything in `project_info.md`/`project_status.md` before deciding how to proceed with that overnight work.

**Next session should start with:** Integrate the trained wake-word model into `turion/main.py` (install `openwakeword`, replace "press Enter to talk" with continuous listening + wake-word trigger), then validate live with the builder's voice. After that, Phase 2 (Vision) is the next open item.

---

## 2026-09-01, ~20:15–20:44

**Session:** Funded the Claude API and ran TURION's first real conversation — Phase 1 complete
- Helped diagnose an unrelated Windows annoyance first: a "tick" sound on every physical keypress, turned out to be Ease of Access → Keyboard → Filter Keys accidentally enabled (likely from holding right Shift for 8s) with "Beep when keys are pressed" checked — found via Volume Mixer (showed "System Sounds" as the source, ruling out Sound Scheme and third-party apps) then checking each Ease of Access toggle in turn. Fixed.
- Confirmed a debit card works for Anthropic Console billing (needs international/online payments enabled; USD; Visa/Mastercard safer than RuPay) and estimated $5 lasts roughly 1-2+ months at the builder's usage level on Haiku 4.5 (`shared/claude-api` skill pricing table)
- Walked through funding Anthropic Console: card had defaulted to a $20 purchase (not the intended $5) plus 18% Indian GST added at checkout — both normal, not errors. Guided creating the first API key (renamed from the default "bro-onboarding-api-key" to "TURION")
- User saved the raw key to `D:\TURION_ROBO\chavi\Cloude_API_KEY.txt` — **inside the git repo**. Caught this before any commit; added `chavi/` to `.gitignore` (user wanted to keep the local backup rather than delete it) so it can never be accidentally pushed
- Set `ANTHROPIC_API_KEY` via `setx`, verified it works with a direct test call through `turion.brain.claude_client`
- Added per-step module visibility to `main.py`/`speak.py` console output at the user's request (e.g. `Thinking... (module: Claude API, model: claude-haiku-4-5-20251001)`, `(module) TTS: Piper [mr] -> "..."`) — answers "how do I know which module is running" directly in the running output rather than requiring code-reading
- **User ran `turion/main.py` themselves and had TURION's first real conversation** — full pipeline confirmed working live: mic → IndicConformer STT → Claude Haiku 4.5 → Piper TTS
- User reported the reply's audio sounded choppy ("तुटक") with the voice switching between a male and female speaker mid-sentence — traced to the script-splitting design in `speak.py` (each language switch was a separate audio clip with an audible gap, and pyttsx3's male English voice was alternating with Piper's female Marathi voice). **Removed script-splitting** — `speak()` now always uses one consistent voice for the whole reply (default Marathi Piper), accepting imperfect pronunciation of embedded English words in exchange for continuous, consistent audio. Deleted the now-dead `_split_by_script`/`_is_devanagari` helpers.
- Documented all of this in `project_info.md` and marked **Phase 1 fully complete** in `project_status.md`

**Next session should start with:** Phase 2 (Vision) — nothing is blocking anymore. Everything from here is new work: camera input, object/face detection, and eventually the person-identification capability captured this morning.

---

## 2026-09-01, ~07:00–08:49

**Session:** Reviewed overnight Indic-TTS results; settled the TTS/interpreter question; decided Phase 4 compute board (Jetson); captured a new person-ID vision
- Sent longer (~28s) Indic-TTS audio samples (male + female) since the overnight ones were too short (~2s) to judge — user found pronunciation less natural than Piper's Marathi voice, with a "Hindi touch" accent. Confirmed only 2 built-in speakers exist (no others), checked AI4Bharat's GitHub for a newer release (none — same 2023 "v1" as before) and for other AI4Bharat voice projects (IndicVoices/-R are datasets, not usable TTS models)
- Explained why the accent issue can't be fixed by "swapping the voice module" alone: FastPitch (the acoustic model) is what determines pronunciation, not HiFi-GAN (the vocoder) — a real fix needs either a different independently-trained model or fine-tuning, not a simple swap
- User asked about a one-time-purchase, fully local alternative to ElevenLabs (for privacy + no subscription) — found a couple of small Gumroad products but flagged them as unverified, Hindi-only (no Marathi), likely just repackaged XTTS v2; recommended against spending money on them
- **User revealed the actual motivation** behind wanting broad language coverage: a future "universal interpreter" capability — TURION asking any Indian person what language they speak and translating between people. Documented as a distinct future capability in `project_info.md`, not Phase 1 scope
- Re-checked Indic Parler-TTS specifically for a "one consistent voice across languages" fit: it supports 21 languages with 69 named speaker identities that stay consistent across all of them — exactly the requirement, already solved by the model. Only blocker is CPU speed (already measured: 34.2x real-time), which should stop mattering once this feature is built on GPU-capable hardware later
- User asked why not use mobile-phone-class hardware for the robot instead of a laptop-class board — explained the real blockers (no GPIO for motor control, Android doesn't run the existing PyTorch stack easily, no robotics ecosystem) and surfaced RK3588-based SBCs (Orange Pi 5 / Radxa Rock 5) as genuine middle ground (phone-class NPU, but Linux + GPIO)
- Published a comparison artifact (spec table + cost breakdown): **https://claude.ai/code/artifact/a3121061-7981-4c50-ac34-e8d5f9827f06** — Jetson Orin Nano vs Orange Pi 5/Rock 5, plus whole-Phase-4-robot cost estimates (Jetson build ₹28,500–48,500 vs Rockchip build ₹20,500–34,500)
- Talked through the tradeoff from a few angles (immediate need vs. future-proofing vs. cost) — **user decided on Jetson Orin Nano**, explicitly prioritizing avoiding future rework (can't code independently, so redoing an integration later costs more than the price gap now) over the project's usual "prototype cheap, expand later" default. Documented as a deliberate, reasoned exception in `project_info.md`
- User outlined a near-term plan: get the Claude API working first, then Phase 2 (camera/vision), then combine both into a person-identification capability (voice + face + object + human detection, culminating in recognizing owner/family members with persistent memory). Clarified "safety" for this means three things together: data privacy (biometric data stays local), access/security (know vs. unknown person), and avoiding misidentification (prefer "don't recognize" over a confident wrong guess). Documented under Phase 3 in `project_info.md`

**Next session should start with:** Fund the Claude API (min. $5) and run `turion/main.py` for TURION's first real conversation — still the only blocker on Phase 1 itself. Everything else discussed today is future-phase planning, captured in docs, not blocking.

---

## 2026-08-31, ~23:07–23:54 (overnight, unattended by user)

**Session:** Got AI4Bharat Indic-TTS working end-to-end for Marathi — a long debugging chain, but a real success
- User asked to go ahead with the Indic-TTS setup overnight rather than waiting until morning, explicitly confirming: (a) the session would stay open so work could continue, and (b) build it fully in parallel — never touch the working main project (`D:\TURION_ROBO\.venv`, Python 3.14). Confirmed both throughout.
- Recreated the isolated-Python-environment approach from the Parler-TTS experiment, but hit a new wall: `Trainer`'s setup.py has a **buggy version check** (`sys.version_info > (3, 11)` is `True` for any 3.11.x patch due to Python tuple comparison) that rejects 3.12 *and* 3.11 — actually needs exactly **3.10**. Set up portable Python 3.10 (embeddable zip + get-pip + virtualenv, same workaround as before since the real installer still fails on this machine) at `D:\indic_tts_env`.
- Cloned the two forked libraries Indic-TTS needs (`gokulkarthik/TTS`, `gokulkarthik/Trainer`) into `D:\indic_tts_src`.
- Hit and fixed, in order: missing C headers on the embeddable Python (fixed by pulling the official `python` NuGet package — a plain zip, no installer — and copying `include`/`libs` into the venv's actual expected location, `<venv>\Scripts\Include`/`libs`, which is non-standard for a venv built on an embeddable base); a broken old `pyworld==0.2.10` pin with no wheel (relaxed to `>=0.3.5`); a numpy/scipy/numba three-way version conflict (kept `numpy==1.21.6` for numba, pinned `scipy==1.7.3` and `soundfile==0.12.1` to match); an **import-order-dependent DLL crash** where importing `librosa`/`numba` before `torch` breaks torch's own DLL loading on Windows (worked around by writing a standalone script that imports `torch` first, then calls `TTS.utils.synthesizer.Synthesizer` directly instead of the buggy-order CLI entry point); a hardcoded bad `speakers_file` path in the downloaded checkpoint's `config.json` (edited it); and a Devanagari-to-console encoding crash (fixed with `PYTHONIOENCODING=utf-8`, same class of issue seen with PowerShell earlier this project).
- Downloaded the Marathi checkpoint (1.41GB) from GitHub Releases — hit "disk full" on D: again mid-extraction, moved everything to C: (which had more room) instead of re-doing the WSL cleanup.
- **It worked.** Generated Marathi audio with both bundled speakers ("male": 1.85x real-time, "female": 1.5x real-time) — far faster than Indic Parler-TTS's 34.2x, though slower than Piper's 0.16x. Same limitation as Piper: embedded English words (e.g. "TURION") aren't in the single-language vocabulary and get silently dropped.
- Sent both audio samples to the user to review in the morning. Documented the full fix chain in `project_info.md` (useful if Indic-TTS is ever revisited for a non-Piper language). Kept the working environment (unlike Parler-TTS's, which was deleted) since it took real effort and could be reused.
- **Not integrated into `speak.py`** — this was a feasibility test only; Piper stays the production Marathi/Hindi/English TTS. Disk space is tight again (D: ~2GB free) — flagged for a cleanup pass if it becomes a problem.

**Next session should start with:** Review the Indic-TTS audio samples and decide whether it's worth integrating anywhere, then — unrelated to this thread — fund the Claude API (min. $5) and run `turion/main.py` for TURION's first real conversation, still the only blocker on Phase 1 itself.

---

## 2026-08-31, ~22:52–23:04

**Session:** Discussion + research — building a custom Indian-language model (ruled out), broader TTS language coverage
- User asked what it would take to build a custom in-house speech model covering all Indian languages, from scratch. Explained honestly: this is what AI4Bharat itself already spent years and institutional funding building — realistically needs lakhs of hours of labeled audio, weeks of multi-GPU training, and ML-specialist engineers; a solo/hobby budget could not replicate it. Realistic alternative: fine-tune an existing open model for a specific need (days, ~₹5,000–50,000) rather than building from scratch.
- Explained what IndicConformer actually is (Conformer = CNN+Transformer hybrid architecture, AI4Bharat-trained, 600M params) since the user asked directly.
- Asked about faster alternatives to Piper for Indian languages — confirmed Piper's Marathi voice is a single package (9 speakers, all female — speaker 8 already chosen) with nothing new added since last check. Total Indian-language coverage in Piper is only 7 languages (hi, mr, bn, te, ml, ur, ne) — missing Tamil, Kannada, Gujarati, Punjabi, Odia, Assamese, Sanskrit, etc.
- Researched two candidates for broader coverage: **Meta MMS-TTS** (1,107 languages total, VITS-based so likely fast, untested) and **AI4Bharat's separate "Indic-TTS" project** (distinct from the already-tested Indic Parler-TTS — easy to confuse) — 13 Indian languages, FastPitch+HiFi-GAN architecture (lightweight/fast, unlike Parler-TTS's slow generative approach). This looks genuinely promising.
- User wants to test Indic-TTS tomorrow rather than tonight — documented the plan so it isn't lost. Setup will likely need another isolated Python environment (same pattern as the Parler-TTS experiment), est. 1-2 hours.

**Next session should start with:** Test AI4Bharat's Indic-TTS (13 Indian languages) for speed/quality. Then, unrelated to this thread: fund the Claude API (min. $5) and run `turion/main.py` for TURION's first real conversation — still the only blocker on Phase 1 itself.

---

## 2026-08-31, ~22:11–22:48

**Session:** Actually tested Indic Parler-TTS; found and fixed a disk-space crisis along the way
- User asked to go ahead and install Indic Parler-TTS in the isolated `D:\parler_tts_env` (Python 3.12) prepared last session
- Install succeeded cleanly (tokenizers built fine on 3.12, unlike 3.14)
- Hit a gated-repo error even with `HF_TOKEN` set — this model needs its own separate access grant on Hugging Face (per-model, not per-account); user accepted terms on the model page and it worked
- Hit "No space left on device" downloading the 3.75GB model file — **discovered C: drive had ~0GB free and D: only ~3GB**. Investigated: an unused WSL Ubuntu install was consuming ~20GB. User confirmed they don't use WSL; removed it (user ran `wsl --unregister Ubuntu` themselves — Claude's auto-mode classifier blocks running destructive commands like this directly). Freed C: to ~22GB, D: to ~4GB. This was a real, general problem worth having found regardless of the TTS experiment — likely also explains the earlier Python 3.12 MSI installer failures
- Re-ran the test successfully: voice quality was genuinely good, but **generation took 34.2x real-time** (~140s to produce 4s of Marathi audio) — confirms this model needs a GPU to be practical; not viable on this hardware. User agreed, staying with Piper.
- Cleaned up afterward: deleted `D:\parler_tts_env`, `C:\Python312_portable`, and the downloaded model caches (~4GB) — nothing from this experiment persists in the project or on disk
- Documented the full experiment outcome in `project_info.md` and `project_status.md`, including the disk-space finding as a standalone note (worth checking periodically going forward)

**Next session should start with:** Fund the Claude API (min. $5) and run `turion/main.py` for TURION's first real conversation — this remains the only blocker on Phase 1

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
