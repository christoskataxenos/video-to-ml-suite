# Video to ML Suite — Upgrade Plan v2.0
**Document Type**: Engineering Upgrade Report  
**Author**: Christos Kataxenos  
**Date**: 2026-04-26  
**Status**: Approved for Implementation  

---

## Executive Summary

The Video to ML Suite is a functional, high-performance toolkit for computer vision dataset creation. The current version (v1.1) was built with ML engineers and researchers in mind. The v2.0 upgrade addresses a critical gap: **making the tool accessible to absolute beginners** who want to enter the world of Machine Learning, while **not restricting experienced users** who already know what they are doing.

The upgrade is structured around three pillars:

1. **Dual-Mode UX** — Expert Mode (unchanged) + Guided Mode (wizard-driven, error-proof)
2. **In-Tool Guided Workflows** — Step-by-step panels inside each module for Guided Mode
3. **Full Internationalization (i18n)** — Native Greek and Native English support, with auto-detection and persistent toggle

The installer (EXE) is already in place. No changes to the C++ engine or the ML pipeline logic are required.

---

## Problem Statement

### Who is being left out

The current tool works well for users who already understand:
- What a YOLO dataset is
- Why Train/Val splitting matters
- What keyframe interpolation means
- What `.yaml` files are and where they come from

However, a large and growing audience — students, domain experts, researchers from non-CS fields — wants to use computer vision tools but is blocked by the steep technical learning curve. They download the tool, open it, see four LAUNCH buttons, and quit.

### Observed failure points (per tool)

| Tool | Problem |
|---|---|
| **Dashboard** | All 4 modules are equally accessible — no order enforced. Beginners launch them in the wrong sequence. |
| **Frame Extractor** | 5 configuration sections visible at once. Terms like "ML Export Mode", "Train Split", "Classes" have no explanation. |
| **Image Annotator** | Opens to a completely black canvas. Keyboard shortcuts (K, I, D, A, S) are not discoverable. "Keyframe Interpolation" is not explained. |
| **Dataset Inspector** | A single button on a black screen. No explanation of what a `dataset.yaml` is or where to find it. |
| **Training Launcher** | "Epochs", "yolov8n.pt (Nano)" — technical terms without any context for a beginner. |

### The language problem

The current UI mixes Greek and English strings inconsistently. A non-Greek speaker cannot read sidebar instructions. A Greek speaker sees some UI elements in English without translation. This is unprofessional and exclusionary.

---

## Goals of v2.0

| Goal | Priority |
|---|---|
| Beginners can complete a full dataset pipeline without making critical errors | Critical |
| Beginners learn what ML concepts mean while they use the tool | High |
| Expert users experience zero friction or regression | Critical |
| The UI is fully available in Greek or English (native, not mixed) | High |
| Language preference persists across sessions | Medium |
| Guided Mode remembers completed steps (bypass available) | Medium |

---

## Pillar 1: Dual-Mode Dashboard

### What needs to change

The Dashboard (`orchestrator.py`) gains a **mode toggle** in the top-right area of the UI:

```
[ EXPERT MODE ]  |  [ GUIDED MODE ]
```

The selected mode is saved to `config.json` and persists between sessions.

### Expert Mode (no changes)

The current dashboard remains exactly as-is. Four LAUNCH buttons, free access, no restrictions. This is the default for returning users who set their mode to Expert.

### Guided Mode — Dashboard behavior

In Guided Mode, the dashboard becomes a **progress tracker**. The four modules are displayed as sequential steps. Each step has a visual state:

| State | Visual | Behavior |
|---|---|---|
| `locked` | Greyed out, no LAUNCH button | Cannot be opened until previous step is marked complete |
| `ready` | Highlighted, LAUNCH button active | Current step — user should do this now |
| `completed` | Checkmark icon, dimmed | Done. "Reopen" button available for bypass |
| `bypassed` | Dashed border | User skipped it (had prior work) |

A **progress bar** across the top of the dashboard shows overall pipeline completion (e.g., `Step 2 of 4 — Image Annotation`).

### Bypass mechanism

At each locked step, a small `"I've already done this →"` link allows the user to mark a step as bypassed and unlock the next one. This prevents the guided mode from being a prison for partially experienced users.

### State persistence

`config.json` is extended with:

```json
{
  "mode": "guided",
  "language": "el",
  "completed_steps": ["extraction"],
  "bypassed_steps": ["inspection"]
}
```

---

## Pillar 2: In-Tool Guided Workflows

Each of the 4 tools gains a **Guided Mode panel** — a secondary view activated only when the app is in Guided Mode. Expert Mode users see the current UI unchanged.

### How the Guided Panel works

The Guided Panel replaces the left sidebar in Guided Mode. Instead of a reference list of features, it shows:

1. **"Why you are here"** — a 2–3 sentence explanation of this tool's purpose in the ML pipeline
2. **Numbered steps** — one action at a time, with the current step highlighted
3. **Contextual ML education** — a short "Did you know?" box explaining the concept behind the current action
4. **Smart defaults** — all settings pre-configured to safe, recommended values. The beginner only changes what they need to.
5. **"Done — Next Step →"** button — marks the step complete, returns to dashboard, unlocks the next module

The existing right-side content area (controls, canvas, etc.) remains. The panel guides the user's attention to what matters right now.

---

### Tool 1: Frame Extractor — Guided Steps

**Why you are here**: *"A computer vision model learns from images, not video. This tool converts your video into hundreds of individual frames (images) that we will label in the next step."*

| Step | Action | ML Education |
|---|---|---|
| 1 | Select your video file | *"Any .mp4, .mov, or .avi file works. Use a video where the object you want to detect is clearly visible."* |
| 2 | Confirm output folder | *"Frames will be saved here. The tool will create a YOLO-ready folder structure automatically."* |
| 3 | Enable ML Export Mode (pre-enabled) | *"This creates the train/val split — a crucial ML concept. We keep 80% of images for training and 20% for testing accuracy."* |
| 4 | Enter your class names | *"A 'class' is the object you want to detect (e.g. 'car', 'person', 'dog'). You can add more later."* |
| 5 | Press START EXTRACTION | *"The C++ engine will process your video at high speed. Wait for the completion message."* |

**Smart defaults in Guided Mode**:
- ML Export Mode: ON
- Train Split: 80%
- Format: jpg
- Width: 1280
- Batch Mode: OFF (single video)

---

### Tool 2: Image Annotator — Guided Steps

**Why you are here**: *"The model cannot learn from raw images alone — it needs to know where the object is in each image. We draw boxes around objects to teach it."*

| Step | Action | ML Education |
|---|---|---|
| 1 | Click "Open Dataset" | *"Select the folder that the Frame Extractor created. You will see your images load in the center."* |
| 2 | Draw a box on the first image | *"Click and drag to draw a rectangle around the object. A popup will ask you to name it — use the class name you defined earlier."* |
| 3 | Move to the next image (D key or NEXT button) | *"You need to label every image. The more consistent your boxes, the better the model learns."* |
| 4 | Use Keyframe Interpolation (optional) | *"If your object moves across multiple frames, use this shortcut: draw the box on Frame 1 (press K), move to Frame 20, adjust the box (press K again), then press I. The tool fills in all frames in between automatically."* |
| 5 | Finish labeling | *"Labels are auto-saved. When all images are labeled, click 'Done — Next Step →'."* |

**Guided Mode additions**:
- A **prominent onboarding overlay** on first open (dismissable): *"Your images are loaded. Start by drawing a box around the object on the first image."*
- Keyboard shortcut hints shown as **button labels** (not just sidebar text): the NEXT button shows `NEXT (D)` with a tooltip on hover
- An **annotation progress counter**: `"47 / 200 images labeled"`

---

### Tool 3: Dataset Inspector — Guided Steps

**Why you are here**: *"Before training, we verify that your dataset is healthy. A good dataset has balanced classes and no missing labels."*

| Step | Action | ML Education |
|---|---|---|
| 1 | Load the dataset.yaml | *"This file was created automatically by the Frame Extractor. It describes your dataset structure. It is located in your output folder."* |
| 2 | Review class distribution | *"Check that each class has a similar number of images. If 'car' has 500 images and 'person' has 10, the model will be much better at detecting cars than people."* |
| 3 | Check for warnings | *"The inspector will flag any images without labels. These are 'blind spots' — the model will learn nothing from them."* |
| 4 | Confirm dataset is healthy | *"If everything looks good, proceed. If not, return to the Annotator and fix the flagged images."* |

**Guided Mode additions**:
- The **"LOAD DATASET.YAML" button** shows a helper text below it: *"Look for dataset.yaml in the folder you chose during Frame Extraction."*
- A **file path hint** pulled from `config.json` (`output_path`): *"Expected location: ./frames/dataset.yaml"* — with a one-click "Load from default path" button

---

### Tool 4: Training Launcher — Guided Steps

**Why you are here**: *"You have images and labels. Now the model learns. This step can take minutes or hours depending on your hardware."*

| Step | Action | ML Education |
|---|---|---|
| 1 | Confirm dataset.yaml path (auto-filled) | *"This points to your labeled dataset. The training engine reads it to find your images and labels."* |
| 2 | Choose model size | *"Start with Nano — it trains fast and is perfect for learning. Use Medium when you need higher accuracy in production."* |
| 3 | Set Epochs (default: 50) | *"An 'epoch' is one complete pass through all your training images. 50 epochs is a safe starting point. More epochs = more learning, but diminishing returns after a point."* |
| 4 | Press START TRAINING | *"Training output will appear below. Watch for 'mAP' — this is your model's accuracy score. Higher is better. A score above 0.7 is a good result."* |

**Smart defaults in Guided Mode**:
- Dataset YAML: auto-filled from `config.json` `output_path`
- Model Size: yolov8n (Nano)
- Epochs: 50

**Model size selector in Guided Mode** shows plain-language descriptions instead of technical names:

```
[ Nano   — Fast training, good for learning    ] ← default
[ Small  — Balanced speed and accuracy         ]
[ Medium — High accuracy, slower training      ]
```

---

## Pillar 3: Internationalization (i18n)

### Architecture

A single `shared/strings.py` module holds all UI strings as a nested dictionary:

```python
STRINGS = {
    "dashboard_title": {
        "el": "ΒΙΝΤΕΟ ΠΡΟΣ ΜΗΧΑΝΙΚΗ ΜΑΘΗΣΗ",
        "en": "VIDEO TO ML SUITE"
    },
    "btn_launch": {
        "el": "ΕΚΚΙΝΗΣΗ",
        "en": "LAUNCH"
    },
    "guided_why_extractor": {
        "el": "Ένα μοντέλο μηχανικής μάθησης μαθαίνει από εικόνες...",
        "en": "A computer vision model learns from images, not video..."
    },
    # ... all strings for all tools
}
```

A global `get_string(key)` function reads the active language from `config.json` and returns the correct string. All UI labels, descriptions, tooltips, and educational texts call this function.

### Language Toggle

A `🇬🇷 / 🇬🇧` toggle button is always visible in the top-right corner of the Dashboard. Clicking it:
1. Updates `config.json` → `"language": "en"` (or `"el"`)
2. Triggers a UI refresh — all labels re-render in the new language

On first launch, the language is auto-detected via Python's `locale.getdefaultlocale()`. If the system locale is `el_GR`, Greek is selected. Otherwise, English is the default.

### Scope of translation

Every visible string in every window is translated. This includes:
- Window titles
- Button labels
- Sidebar content
- Step descriptions
- ML education texts
- Error messages
- Log messages
- Tooltip texts

---

## File Change Summary

| File | Change Type | Description |
|---|---|---|
| `shared/strings.py` | **NEW** | i18n dictionary + `get_string()` helper |
| `config.json` (schema) | **EXTENDED** | Adds `language`, `mode`, `completed_steps`, `bypassed_steps` |
| `orchestrator.py` | **MODIFIED** | Dual-mode dashboard, language toggle, step state management |
| `generator/app.py` | **MODIFIED** | Guided Mode panel + smart defaults + i18n |
| `labeler/app.py` | **MODIFIED** | Guided Mode panel + onboarding overlay + progress counter + i18n |
| `inspector/app.py` | **MODIFIED** | Guided Mode panel + auto-path hint + i18n |
| `trainer/app.py` | **MODIFIED** | Guided Mode panel + plain-language model selector + i18n |
| `shared/guided_panel.py` | **NEW** | Reusable Guided Mode panel widget (CTkFrame subclass) |

> **No changes** to: `engine/` (C++), `CMakeLists.txt`, `Dockerfile`, installer scripts, `requirements.txt`

---

## Implementation Phases

### Phase 1 — i18n Foundation (1–2 days)
- Create `shared/strings.py` with all current strings translated to both languages
- Integrate `get_string()` into `orchestrator.py` and all 4 tools
- Add language toggle to Dashboard
- Add auto-detect on first launch
- Test: switch language, restart app, verify persistence

### Phase 2 — Dual-Mode Dashboard (1–2 days)
- Add mode toggle to Dashboard
- Implement step state machine in `orchestrator.py`
- Implement visual states (locked / ready / completed / bypassed)
- Implement progress bar
- Implement bypass mechanism
- Test: full guided flow from step 1 to step 4

### Phase 3 — In-Tool Guided Panels (3–4 days)
- Create `shared/guided_panel.py` reusable widget
- Implement Guided Panel for Frame Extractor (smart defaults, 5 steps)
- Implement Guided Panel for Image Annotator (onboarding overlay, progress counter)
- Implement Guided Panel for Dataset Inspector (auto-path hint)
- Implement Guided Panel for Training Launcher (plain-language model selector)
- Test: each tool in Guided Mode with a beginner tester

### Phase 4 — Integration & Polish (1 day)
- End-to-end test: beginner user completes full pipeline in Guided Mode
- End-to-end test: expert user sees no changes in Expert Mode
- Verify language toggle works in all windows
- Fix any regressions

**Total estimated effort**: 6–9 developer-days

---

## Testing Checklist

- [ ] Beginner tester (no ML background) completes full pipeline unaided in Guided Mode
- [ ] Expert tester confirms Expert Mode is identical to v1.1
- [ ] Language toggle switches all strings in all windows correctly
- [ ] Language persists after app restart
- [ ] Mode persists after app restart
- [ ] Completed steps persist after app restart
- [ ] Bypass correctly unlocks the next step
- [ ] Smart defaults produce a valid, trainable dataset without manual configuration
- [ ] Guided Mode "Done — Next Step →" button correctly updates dashboard state
- [ ] Auto-path hint in Inspector correctly reads from `config.json`

---

## Decision Log

| Decision | Alternatives Considered | Reason |
|---|---|---|
| Two modes (Expert + Guided) instead of one unified mode | Single guided mode with optional skip; full redesign of dashboard | Expert users must experience zero friction. A second mode is cleaner than a skip-heavy unified flow. |
| Guided bypass via "I've already done this" link | Hard lock with no bypass; require redo of previous step | A returning beginner may have valid prior work. Forcing redo destroys trust. |
| `shared/strings.py` dictionary for i18n | `.po`/`.mo` gettext files; JSON file per language | CustomTkinter has no gettext integration. A Python dict is simple, fast, and requires no extra dependencies. |
| Language auto-detect from OS locale on first launch | Always default to English; show a language selection screen | Silent auto-detect is less intrusive. Toggle is always available to correct it immediately. |
| Guided Panel as a separate widget replacing the sidebar | Separate window; modal dialog; overlay | Sidebar replacement keeps the layout familiar. It's additive, not disruptive. |
| Smart defaults pre-configured in Guided Mode | Ask beginner to configure everything; add a "recommend settings" button | The safest defaults (ML Export ON, 80% split, Nano model, 50 epochs) are known and safe. Asking beginners to configure them adds unnecessary risk of error. |

---

*End of Upgrade Plan — Video to ML Suite v2.0*
