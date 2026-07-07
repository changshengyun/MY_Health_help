# Skill Research And Completion Rules

## 1. User Completion Questions

After completing a project task, the assistant should answer these two questions:

1. 眼下你最没把握的事情是什么？
2. 关于当前情况，我最大的遗漏是什么？我没有意识到什么？

These questions should be answered in the final response after implementation, validation, and status reporting.

## 2. Skill Search Notes

The user asked to search for usable skills and mentioned Cocoloop as a possible skill collection site.

Search results did not expose a clearly usable Cocoloop skill collection page. The useful public direction found during search was broader AI-agent skill registries and skill package research:

- `skills.sh` appears in recent skill-registry research as a public registry hosting many agent skills.
- Recent papers describe skills as `SKILL.md` packages with metadata and task instructions.
- Skill registry usage has supply-chain risk, so third-party skills should be inspected before installation.

## 3. Practical Skills Useful For This Project

| Need | Useful Skill/Capability | Why |
| --- | --- | --- |
| Frontend visual QA | browser / Playwright-style browser verification | Check layout, mobile overflow, navigation, and rendered text. |
| GitHub publishing | GitHub plugin / git CLI | Push changes, inspect repo state, handle PR workflows when available. |
| Reusable project-specific workflow | skill-creator | Create a custom skill for this health assistant project once the workflow stabilizes. |
| Debug retrospectives | debug-retrospective-writer | Record environment/debug cases only after user approval. |
| Spreadsheet export later | spreadsheets skill | Export training, meal, weight, and waist data to Excel/CSV reports. |

## 4. Candidate Custom Skill

If this project continues, the most useful custom skill would be:

```text
health-assistant-product-engineer
```

Scope:

- Preserve local SQLite data model.
- Maintain React + Vite frontend.
- Verify desktop and mobile layout after UI changes.
- Explain calorie estimation and nutrition logic in user-facing language.
- Avoid committing runtime SQLite changes unless explicitly requested.

