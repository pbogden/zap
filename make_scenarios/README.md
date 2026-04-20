# Make Scenario Blueprints

This directory is where exported Make scenario blueprints live once they've
been built. Each subdirectory corresponds to one demo stage.

```
make_scenarios/
├── stage1_blog_notify/
├── stage2_lead_capture/
└── stage3_case_study_approval/
```

---

## What goes here

Make allows any scenario to be exported as a `.json` blueprint file that
another Make account can import directly — recreating the scenario structure,
module configuration, and data mappings in one step. Once you've built the
Stage 1, 2, and 3 scenarios by following the setup docs, export each one and
add it here. Students can then import rather than build from scratch.

---

## How to export a blueprint from Make

1. Open the scenario in Make
2. Click the **three-dot menu** (⋯) in the bottom toolbar
3. Select **Export Blueprint**
4. Save the `.json` file into the appropriate subdirectory here

Name the file consistently, e.g.:
- `make_scenarios/stage1_blog_notify/blueprint.json`
- `make_scenarios/stage2_lead_capture/blueprint.json`
- `make_scenarios/stage3_case_study_approval/blueprint.json`

---

## How to import a blueprint into Make

1. In Make, click **Create a new scenario**
2. Click the **three-dot menu** (⋯) in the bottom toolbar
3. Select **Import Blueprint**
4. Upload the `.json` file

After importing, you'll need to:
- Reconnect any service credentials (Slack, Gmail, HubSpot, etc.) —
  these are not stored in the blueprint for security reasons
- Copy the webhook URL from the Custom Webhook trigger module and add
  it to your `.env` file

---

## Setup docs

If blueprints aren't available yet, the stage docs walk through building
each scenario from scratch:

- [Stage 1 — Blog → Slack + LinkedIn](../docs/stage1.md)
- [Stage 2 — Lead Capture → HubSpot + Email](../docs/stage2.md)
- [Stage 3 — Case Study Request → Approval Workflow](../docs/stage3.md)
