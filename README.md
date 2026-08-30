# TURION

Embodied, multimodal AI agent — starts as a voice assistant, grows toward a robotic arm and eventually a humanoid. Full project overview: [Doc/project_info.md](Doc/project_info.md).

## Phase 1 — Voice Assistant Quickstart

1. Create and activate a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set your Claude API key as an environment variable (do not hardcode it anywhere):
   ```
   setx ANTHROPIC_API_KEY "your-key-here"
   ```
   (open a new terminal after running `setx` so it takes effect)
4. Run:
   ```
   python -m turion.main
   ```

See [Doc/project_status.md](Doc/project_status.md) for current progress and checklist.
