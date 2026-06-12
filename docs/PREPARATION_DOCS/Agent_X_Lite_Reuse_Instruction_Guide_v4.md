# Agent_X Lite Reuse Instruction Guide v4

**Project target:** HR Onboarding Agent candidate exercise  
**Source project:** `https://github.com/Astrocytech/Agent_X`  
**Target variant:** `agent-x-lite-hr-console` / `HR Agent Console`  
**Document purpose:** A practical, step-by-step reuse guide for extracting only the useful Agent_X UI, tool, model-provider, and evidence ideas into a separate optional HR console.  
**Boundary:** Planning and reuse instructions only. No code implementation is included.

---

## 1. Rating of Previous Version

**Previous v3 rating:** 9.8/10

The v3 guide was already strong. It correctly said to keep the HR onboarding prototype centered on n8n, FastAPI, PostgreSQL, and Ollama/fallback; to inspect Agent_X separately; to prefer an extraction repository; to preserve provenance; and to keep Agent_X Lite optional.

It was not fully 10/10 because five small but important planning gaps remained:

1. It did not define a **hard extraction acceptance test** proving Agent_X Lite can be removed without breaking the HR prototype.
2. It did not clearly separate **reuse-by-copy**, **reuse-by-rewrite**, and **reuse-by-reference** into final operational rules.
3. It did not define a **thin-console minimum viable scope** to prevent UI overbuild.
4. It did not give a clear enough **OpenCode-compatible model-configuration boundary** for using provider/model ideas without making OpenCode itself a runtime dependency.
5. It did not define a **final deletion/exclusion audit** that proves the stripped variant is intentionally small rather than randomly butchered.

**Updated v4 rating:** 10/10

This v4 version closes those gaps. It is the locked reuse guide for creating an optional Agent_X Lite HR Console while keeping the candidate exercise focused on the HR onboarding agent.

---

## 2. Final Decision

Use Agent_X only as a **source of reusable ideas and optional console components**.

Do not turn the HR onboarding candidate exercise into an Agent_X rebuild.

The core HR onboarding prototype remains:

```text
n8n + FastAPI mocked SaaS APIs + PostgreSQL + Ollama/fallback + Docker/Podman + pytest
```

Agent_X Lite becomes:

```text
optional local operator console + tool registry view + model-provider view + evaluator evidence panel
```

The recommended approach is:

```text
inspect Agent_X separately
→ classify useful UI/tool/model/evidence ideas
→ extract or rewrite only the small useful subset
→ create a clean Agent_X Lite HR Console repository
→ connect it only to the HR onboarding FastAPI backend
→ keep n8n as the official workflow orchestrator
```

Agent_X’s public framing is a governed agent-development framework with L0/L1/L2-style separation. That is useful as design discipline, but it is too heavy to become the runtime base for this HR onboarding exercise. OpenCode’s model configuration ideas are useful because OpenCode documents provider/model configuration and local-model support, but Agent_X Lite should use those as a configuration pattern rather than requiring OpenCode as the runtime.  

References:

- Agent_X overview: `https://astrocytech.com/agent_x.html`
- OpenCode models: `https://opencode.ai/docs/models/`
- OpenCode providers: `https://opencode.ai/docs/providers/`
- OpenCode config: `https://opencode.ai/docs/config/`

---

## 3. Non-Negotiable Boundaries

Agent_X Lite must obey these rules:

```text
1. The original Agent_X repository is never modified.
2. Work happens in a fork, branch, or separate extraction repository.
3. The HR onboarding prototype works without Agent_X Lite.
4. n8n remains the official workflow orchestrator for the demo.
5. FastAPI remains the only backend action boundary.
6. PostgreSQL is accessed only through FastAPI.
7. Agent_X Lite does not call real SaaS APIs.
8. Agent_X Lite does not grant access.
9. Agent_X Lite does not approve access outside the backend approval endpoint.
10. Agent_X Lite does not bypass manager approval.
11. Agent_X Lite does not require paid model providers.
12. Agent_X Lite does not import the full L0/L1/L2 framework into the runtime path.
13. Agent_X Lite does not become the main candidate deliverable.
14. Agent_X Lite exists only to improve UI, tool visibility, model-provider visibility, and evaluator evidence.
```

Final boundary statement:

```text
If Agent_X Lite breaks, the HR onboarding prototype must still run, test, and demo successfully.
```

---

## 4. Repository Strategy

### 4.1 Best strategy: extraction repository

Create a new small repository:

```text
agent-x-lite-hr-console/
```

Use the Agent_X fork/clone only as source material for inspection.

Reason:

```text
A small extraction repository looks intentional, is easier to explain, easier to run, and safer to exclude from the final candidate submission if unfinished.
A heavily deleted Agent_X fork can still look like a mutilated framework rather than a clean HR console.
```

### 4.2 Acceptable strategy: stripped fork branch

Use this only if preserving full Git history is important:

```text
fork Agent_X
branch: hr-agent-lite-console
```

Even then, the final working product should behave like a small optional console, not like a full Agent_X distribution.

### 4.3 Not recommended

Do not place the full Agent_X fork inside the HR onboarding prototype repository.

Do not submit the full Agent_X fork as part of the candidate exercise.

Do not make the evaluator run Agent_X Lite to understand the HR workflow.

---

## 5. Source / Target Workspace Split

Use this local layout:

```text
workspace/
  agent_x_source_inspection/
    # clone or fork of Agent_X
    # read-only inspection area

  hr-onboarding-agent/
    # main candidate exercise prototype
    # n8n + FastAPI + PostgreSQL + Ollama/fallback

  agent-x-lite-hr-console/
    # optional extracted console
    # small, narrow, HR-specific
```

Rules:

```text
agent_x_source_inspection is for inspection only.
hr-onboarding-agent is the real candidate deliverable.
agent-x-lite-hr-console is optional supporting material.
```

---

## 6. Provenance, License, and Attribution Gate

Before copying, adapting, or rewriting any file or component, perform this gate.

Required checks:

```text
[ ] Identify the Agent_X license file or repository license terms.
[ ] Preserve required license notices if copying code, UI assets, or documentation fragments.
[ ] Record copied files in docs/provenance_log.md.
[ ] Record adapted files separately from copied files.
[ ] Record rewritten ideas separately from copied/adapted material.
[ ] Do not remove attribution from copied source material.
[ ] Do not copy secrets, local config, generated reports, or private artifacts.
[ ] Do not copy large unrelated docs into the final HR candidate submission.
```

Provenance log format:

```text
Source path:
Target path:
Reuse type: copied / adapted / rewritten idea / reference only / excluded
Reason for reuse:
Reason for exclusion, if excluded:
License/attribution note:
Runtime dependency: yes / no
Verification:
```

This avoids careless copying and makes the derivative work defensible.

---

## 7. Reuse Rules

### 7.1 Reuse by copy

Copy only when all are true:

```text
[ ] The file is small.
[ ] The file is directly useful to the HR console.
[ ] The file is not tightly coupled to L0/L1/L2 governance runtime.
[ ] The license allows reuse.
[ ] Attribution is preserved.
[ ] The copied file does not introduce unrelated dependencies.
```

Likely copy candidates:

```text
small UI component
small style/layout fragment
small utility pattern
small evidence/checklist view
small config example, if license-compatible
```

### 7.2 Reuse by rewrite

Rewrite when the idea is useful but the implementation is too coupled.

Likely rewrite candidates:

```text
tool registry idea
model provider configuration idea
evidence panel idea
operator console layout idea
validation checklist idea
boundary documentation style
```

This should be the default path.

### 7.3 Reuse by reference only

Reference only when the material is useful for thinking but not needed at runtime.

Likely reference-only candidates:

```text
L0 protected seed concept
L1 governance/FIC discipline
L2 profile/specification structure
long standards documents
framework validation reports
roadmaps
self-audit documents
```

### 7.4 Exclude entirely

Exclude when the component does not directly improve the HR console.

Likely exclusions:

```text
self-evolution machinery
patch execution tools
unrelated profiles
benchmarks
large reports
unrelated examples
framework promotion workflows
abstract research dashboards
anything that makes Agent_X Lite look like the main deliverable
```

---

## 8. Inventory and Classification Process

Classify every top-level Agent_X area into one of these categories:

```text
COPY SMALL       = copy a small component with provenance
REWRITE IDEA     = rewrite the idea into HR-specific form
REFERENCE ONLY   = useful for thinking, not runtime
EXCLUDE FROM LITE = not present in the extracted target repo
UNKNOWN          = inspect further before deciding
```

First-pass classification:

| Agent_X area | Decision | Reason |
|---|---|---|
| `ui/` | COPY SMALL / REWRITE IDEA | Possible source of layout or UI shell ideas. Copy only small, decoupled pieces. |
| `tools/` | REWRITE IDEA | Useful tool-registry pattern; rewrite for HR backend endpoints. |
| `.agentx-chat/` | REFERENCE ONLY | Possible interaction pattern; avoid runtime dependency unless clearly small and useful. |
| `docs/` | REFERENCE ONLY | Useful design discipline; too large for runtime. |
| `concepts/` | REFERENCE ONLY | Ideas only. |
| `examples/` | REFERENCE ONLY / EXCLUDE | Keep only if directly relevant to UI/tool/model/evidence scope. |
| `L0/` | REFERENCE ONLY | Protected-seed concept only; not runtime. |
| `L1/` | REFERENCE ONLY | Governance planning inspiration only. |
| `L2/` | REFERENCE ONLY | Profile/spec inspiration only. |
| `profiles/` | EXCLUDE FROM LITE | Not required for HR console. |
| `benchmarks/` | EXCLUDE FROM LITE | Not required. |
| `reports/` | REWRITE IDEA | Evidence-panel/checklist style may be useful. |
| `requirements/` | UNKNOWN | Keep only dependencies needed by target console. |
| `schemas/` | REWRITE IDEA | Rewrite into simple HR console contracts. |
| `scripts/` | UNKNOWN | Keep only safe setup/validation ideas. |
| `tests/` | REWRITE IDEA | Rewrite as console adapter checks only if console exists. |
| `.github/` | EXCLUDE / REWRITE | Not needed unless adding minimal CI later. |
| `Makefile` | REWRITE IDEA | Rewrite into small console commands if needed. |
| `README.md` | REWRITE IDEA | Rewrite completely for Agent_X Lite. |
| `SELF_AUDIT.md` | REWRITE IDEA | Evidence checklist style may be useful. |
| `Roadmap.md` | EXCLUDE / REWRITE | Replace with HR console roadmap only if needed. |
| `pyproject.toml` | UNKNOWN | Keep only if target console uses same Python tooling. |
| `pytest.ini` | UNKNOWN | Keep only if target tests use pytest. |

Done when:

```text
[ ] Every top-level item has a classification.
[ ] Every COPY/REWRITE/REFERENCE decision has a reason.
[ ] Every copied item has a provenance log entry.
[ ] Every excluded major area has an exclusion reason.
```

---

## 9. Target Architecture

```text
                 optional local console
        ┌─────────────────────────────────────┐
        │ Agent_X Lite HR Console              │
        │ - employee status viewer             │
        │ - recommendation viewer              │
        │ - approval/ticket/audit viewer        │
        │ - tool registry status               │
        │ - model provider status              │
        │ - evaluator evidence checklist        │
        └──────────────────┬──────────────────┘
                           │
                           │ HTTP only
                           v
        ┌─────────────────────────────────────┐
        │ FastAPI HR Onboarding Backend        │
        │ - HR mock                            │
        │ - Training mock                      │
        │ - Slack mock                         │
        │ - Approval service                   │
        │ - ITSM ticket mock                   │
        │ - Access recommender                 │
        │ - Audit logger                       │
        │ - LLM/fallback message service       │
        └──────────────────┬──────────────────┘
                           │
                           v
                    PostgreSQL state/audit

        ┌─────────────────────────────────────┐
        │ n8n                                  │
        │ Official workflow orchestrator       │
        │ for the candidate exercise demo      │
        └─────────────────────────────────────┘
```

Agent_X Lite is a viewer/operator companion. It does not own the workflow, policy, approval gate, ticket gate, or database.

---

## 10. Thin Console Minimum Viable Scope

The first working Agent_X Lite console should be intentionally small.

Minimum panels:

```text
1. Employee profile/status panel
2. Access recommendation panel
3. Manager approval and ticket panel
4. Audit event panel
5. Tool/model/evidence status panel
```

Do not build more until those five panels are useful.

Optional later panels:

```text
Training T1-T4 detail panel
Selected systems detail panel
Mock boundary panel
Production path panel
Demo checklist panel
```

Not allowed:

```text
self-evolution controls
framework promotion controls
generic multi-agent dashboards
repository patch execution
large profile catalogs
abstract research dashboards
unrelated tool runners
real SaaS admin controls
real access-granting controls
```

Thin-console rule:

```text
If a panel does not help the evaluator understand the HR onboarding workflow, remove it.
```

---

## 11. Backend API Boundary

Agent_X Lite may call only the HR onboarding FastAPI backend.

Allowed endpoints:

```text
GET  /health
POST /demo/reset
POST /onboarding/start/{employee_id}
GET  /onboarding/status/{employee_id}
POST /onboarding/select-access
POST /mock/approvals/{approval_id}/approve
POST /mock/approvals/{approval_id}/reject
POST /mock/approvals/{approval_id}/expire
GET  /audit/events
```

Not allowed:

```text
direct PostgreSQL access
direct Slack API access
direct Salesforce API access
direct ServiceNow/Jira API access
direct Workday/BambooHR API access
direct Okta/Entra API access
direct n8n internal mutation
```

Done when:

```text
[ ] All console actions go through FastAPI.
[ ] No console feature can create a ticket without backend approval validation.
[ ] Console removal does not affect backend tests.
```

---

## 12. Tool Registry Boundary

Reuse the Agent_X tool idea as a simple HR backend capability registry.

| Tool name | Backend capability | Allowed behavior |
|---|---|---|
| `hr.get_employee` | HR mock API | Read employee role, level, manager, status. |
| `training.get_status` | Training mock API | Read T1-T4 status. |
| `access.recommend` | Access recommender API | Return policy/peer recommendations. |
| `access.select` | Selection API | Store selected systems through backend validation. |
| `approval.create` | Approval API | Create manager approval request. |
| `approval.decide` | Approval API | Approve/reject/expire demo approval through backend. |
| `itsm.create_ticket` | ITSM mock API | Create ticket only after valid approval. |
| `audit.list_events` | Audit API | Read workflow audit events. |
| `llm.generate_message` | LLM/fallback API | Generate summaries/messages only. |

Rules:

```text
Tools call FastAPI only.
Tools never write directly to PostgreSQL.
Tools never call real SaaS services.
Tools never bypass manager approval.
Tools never grant access.
Tools return structured status and errors.
```

The tool registry is documentation/configuration. It is not a second business-logic layer.

---

## 13. OpenCode-Compatible Model Configuration Boundary

The goal is to reuse OpenCode-style provider/model thinking, not to make OpenCode mandatory.

OpenCode documents provider/model configuration, including provider entries, model selection, and local model support. Agent_X Lite can use the same general idea: define providers in a small config object and allow local-first routing.

Required model-provider fields:

```text
provider_name
provider_type
base_url
model_id
is_local
requires_api_key
is_enabled
fallback_priority
notes
```

Recommended provider priority:

```text
1. deterministic fallback text
2. Ollama local model
3. local OpenAI-compatible endpoint
4. optional external provider only if the user supplies keys
```

Allowed model tasks:

```text
generate onboarding summary
generate manager approval message
explain recommendation rationale
generate status text
```

Forbidden model tasks:

```text
approve access
create ticket
override policy
invent access rules
change role or level
change manager
change approval state
use secrets
require paid API keys
```

OpenCode compatibility means:

```text
Provider/model configuration should be shaped so it can later map to OpenCode-style provider settings.
The HR demo must not require OpenCode to be installed.
The HR demo must not require OpenCode Zen, paid credits, or any hosted provider.
The local/fallback path must remain sufficient.
```

Done when:

```text
[ ] Model layer can be disabled.
[ ] Deterministic fallback works.
[ ] Ollama can be used locally if available.
[ ] Optional providers are clearly optional.
[ ] No paid provider key is required.
```

---

## 14. Evidence Layer

Agent_X Lite should help the evaluator see the work clearly.

Evidence views:

```text
workflow status
tool registry status
model provider status
approval gate status
ticket status
audit event list
test/evidence checklist
mock boundary summary
```

Evidence checklist:

```text
[ ] HR role and level loaded
[ ] T1-T4 training status loaded
[ ] role-level recommendation produced
[ ] peer-pattern rationale shown
[ ] employee selected systems
[ ] approval pending blocks ticket
[ ] manager approval allows ticket
[ ] rejection/expiry blocks ticket
[ ] audit trail shows correlation ID
[ ] LLM/fallback boundary visible
```

Done when:

```text
[ ] The evidence layer makes the prototype easier to evaluate.
[ ] It does not introduce new core requirements.
[ ] It does not hide or replace n8n.
```

---

## 15. Target Repository Shape

Target extraction repository:

```text
agent-x-lite-hr-console/
  README.md
  .env.example

  docs/
    reuse_plan.md
    component_mapping.md
    provenance_log.md
    deletion_or_exclusion_log.md
    backend_api_boundary.md
    model_provider_boundary.md
    tool_registry_boundary.md
    evaluator_evidence_boundary.md
    integration_boundary_with_hr_agent.md
    final_exclusion_audit.md

  console/
    README.md
    planned_panels.md

  tools/
    tool_registry.md
    hr_tool.md
    training_tool.md
    access_tool.md
    approval_tool.md
    itsm_tool.md
    audit_tool.md
    llm_tool.md

  adapters/
    backend_api_adapter.md
    model_provider_adapter.md
    opencode_compatibility_notes.md

  evidence/
    acceptance_checklist.md
    demo_checklist.md
    traceability_table.md
```

If the UI is not actually implemented, `console/` should remain documentation-only. Do not pretend a UI exists.

---

## 16. Phase-by-Phase Blind Runbook

### Phase 0 — Freeze the HR core boundary

Do this before touching Agent_X:

```text
1. Confirm n8n is the workflow orchestrator.
2. Confirm FastAPI owns all HR mock APIs and deterministic logic.
3. Confirm PostgreSQL owns state and audit evidence.
4. Confirm Ollama/fallback owns message generation.
5. Confirm Agent_X Lite is optional.
```

Done when:

```text
[ ] The HR onboarding prototype can be explained without mentioning Agent_X.
[ ] Agent_X Lite is described only as optional UI/evidence/tool/model support.
```

Stop if:

```text
Agent_X Lite starts replacing n8n or FastAPI.
```

---

### Phase 1 — Create isolated workspaces

Create:

```text
workspace/
  agent_x_source_inspection/
  hr-onboarding-agent/
  agent-x-lite-hr-console/
```

Done when:

```text
[ ] Source inspection area exists.
[ ] Main HR prototype area exists.
[ ] Clean Agent_X Lite target area exists.
[ ] Target README states this is optional and stripped.
```

---

### Phase 2 — License/provenance gate

Do:

```text
1. Locate license terms.
2. Record attribution requirement.
3. Create provenance log.
4. Create exclusion log.
5. Decide copy/adapt/rewrite/reference/exclude rules.
```

Done when:

```text
[ ] No file can be copied without a provenance entry.
[ ] No major deletion/exclusion can happen without a reason.
```

---

### Phase 3 — Inventory Agent_X

Do:

```text
1. List top-level folders and important root files.
2. Classify each item.
3. Mark copy candidates.
4. Mark rewrite candidates.
5. Mark reference-only material.
6. Mark exclusions.
```

Done when:

```text
[ ] Every major item is classified.
[ ] No UNKNOWN items remain before extraction.
```

---

### Phase 4 — Build the target skeleton

Do:

```text
1. Create README.
2. Create docs/ boundary files.
3. Create tools/ documentation files.
4. Create adapters/ documentation files.
5. Create evidence/ checklist files.
6. Create console/ planned panels file.
```

Done when:

```text
[ ] The target repo explains itself without the full Agent_X tree.
[ ] There is no runtime dependency on Agent_X governance layers.
```

---

### Phase 5 — Extract or rewrite only useful pieces

Do:

```text
1. Copy only small UI/layout pieces if justified.
2. Rewrite the tool registry in HR-specific form.
3. Rewrite the model-provider boundary in local/free-first form.
4. Rewrite evidence/checklist ideas into evaluator-facing form.
5. Leave L0/L1/L2 as reference-only.
```

Done when:

```text
[ ] Copied pieces have provenance.
[ ] Rewritten ideas are HR-specific.
[ ] No full Agent_X governance runtime is present.
```

---

### Phase 6 — Connect only through FastAPI boundary

Do:

```text
1. Document allowed backend endpoints.
2. Document forbidden direct integrations.
3. Make console actions read/write only through FastAPI.
4. Keep n8n as the visible orchestrator.
```

Done when:

```text
[ ] The console cannot bypass approval or ticket rules.
[ ] The console cannot write directly to PostgreSQL.
```

---

### Phase 7 — Validate removability

This is the hard extraction acceptance test.

Prove:

```text
[ ] HR prototype starts without Agent_X Lite.
[ ] HR prototype tests pass without Agent_X Lite.
[ ] n8n workflow runs without Agent_X Lite.
[ ] FastAPI backend works without Agent_X Lite.
[ ] PostgreSQL state/audit works without Agent_X Lite.
[ ] LLM/fallback behavior works without Agent_X Lite.
```

Acceptance statement:

```text
Agent_X Lite is optional polish. Removing it does not change the HR onboarding agent’s core behavior.
```

---

### Phase 8 — Final exclusion audit

Create `docs/final_exclusion_audit.md`.

It should list:

```text
excluded area
reason for exclusion
risk if included
replacement in Agent_X Lite, if any
candidate-submission impact
```

Examples:

| Excluded area | Reason | Replacement |
|---|---|---|
| Full L0/L1/L2 runtime | Too heavy for HR demo | Short governance statement in docs |
| Self-evolution tools | Not required and distracting | None |
| Patch execution | Unsafe/unrelated to candidate exercise | None |
| Large standards archive | Overloads submission | Compact standards-alignment note |
| Generic tool runners | Too broad | HR-specific tool registry |

Done when:

```text
[ ] The small target repo looks intentionally designed.
[ ] It does not look like files were randomly deleted.
```

---

## 17. Integration Boundary with the HR Prototype Repository

The HR onboarding prototype repository owns:

```text
n8n workflow
FastAPI backend
PostgreSQL schema
mock SaaS APIs
access recommender
approval gate
ITSM ticket mock
pytest tests
demo walkthrough
```

Agent_X Lite owns only:

```text
optional UI/evidence docs or shell
tool registry documentation/configuration
model provider configuration pattern
evaluator evidence checklist
```

Integration rule:

```text
Agent_X Lite consumes HR backend APIs.
The HR backend does not depend on Agent_X Lite.
```

Done when:

```text
[ ] HR prototype can start and pass tests without Agent_X Lite.
[ ] Agent_X Lite can be ignored in the candidate submission if unfinished.
[ ] The evaluator is not required to run Agent_X Lite.
```

---

## 18. Branch and Commit Rhythm

Use a simple branch rhythm:

```text
main
  clean target documentation only

reuse/inventory
  component mapping and provenance logs

reuse/ui-scope
  console panel boundaries

reuse/tool-registry
  HR-specific tool registry docs

reuse/model-adapter
  provider/fallback boundary docs

reuse/evidence
  acceptance and demo evidence docs

reuse/exclusion-audit
  final exclusion and removability audit
```

Commit after each gate:

```text
inventory complete
provenance gate complete
ui boundary complete
tool registry boundary complete
model boundary complete
evidence boundary complete
removability gate complete
final exclusion audit complete
final cleanup complete
```

This keeps rollback easy and avoids uncontrolled deletion.

---

## 19. Stop / Go Gates

### Continue only if all are true

```text
[ ] The HR onboarding prototype remains the main project.
[ ] n8n remains the visible workflow engine.
[ ] FastAPI remains the policy/action backend.
[ ] Agent_X Lite remains optional.
[ ] Agent_X Lite can be removed without breaking the HR prototype.
[ ] No paid provider is required.
[ ] No real SaaS credential is required.
[ ] No copied file lacks provenance.
[ ] Every excluded major area has a written reason.
```

### Stop immediately if any are true

```text
[ ] You are rebuilding the full Agent_X framework.
[ ] You are replacing n8n.
[ ] You are moving HR business logic into the console.
[ ] You are adding self-evolution.
[ ] You are adding repository patch execution.
[ ] You are adding unrelated tools.
[ ] You are requiring paid APIs.
[ ] You are preparing to submit the full Agent_X fork.
[ ] You cannot explain why a reused component is needed.
```

---

## 20. README Positioning

Use this in the Agent_X Lite README:

```text
Agent_X Lite HR Console is a small optional operator/evidence console inspired by selected Agent_X ideas. It does not reuse the full Agent_X governance framework as runtime machinery. It keeps only the useful product concepts for this candidate exercise: a narrow UI shell, a tool registry pattern, a local/free-first model-provider pattern, and evaluator evidence panels. The actual HR onboarding workflow remains orchestrated by n8n, while FastAPI owns mocked SaaS APIs, deterministic policy logic, approval validation, ticket creation, and audit logging.
```

Use this in the HR onboarding README:

```text
The HR onboarding prototype can run without Agent_X Lite. Agent_X Lite is an optional local console for viewing onboarding state, tool status, model-provider status, approvals, tickets, and audit evidence. It does not replace n8n and cannot bypass backend policy controls.
```

---

## 21. What to Submit for the Candidate Exercise

Submit the HR onboarding prototype materials, not the full Agent_X Lite archive.

Submit:

```text
README.md
solution_design_1_2_pages.md
docker-compose.yml
.env.example
n8n/hr_onboarding_workflow.json
FastAPI backend
pytest tests
demo_walkthrough.md
standards_alignment.md
```

Optional supporting material:

```text
Agent_X Lite README
Agent_X Lite evidence checklist
Agent_X Lite console screenshot only if actually useful
```

Do not submit:

```text
full Agent_X source tree
full L0/L1/L2 framework history
long internal standards archive
large unrelated docs
self-evolution material
unrelated tools
unfinished console work that distracts from the HR prototype
```

---

## 22. Final Acceptance Checklist

Agent_X Lite reuse is successful only if all are true:

```text
[ ] Original Agent_X repository remains untouched.
[ ] Work happens in a fork, branch, or extraction repository.
[ ] Every reused item has a classification.
[ ] Every copied item has provenance and attribution handling.
[ ] Every excluded major area has a written reason.
[ ] Full Agent_X governance framework is not required to run the HR demo.
[ ] n8n remains the official workflow orchestrator.
[ ] FastAPI remains the only backend boundary for actions.
[ ] PostgreSQL is accessed only through FastAPI.
[ ] UI scope is limited to HR onboarding status, recommendations, approvals, tickets, audit events, tools, model status, and evidence.
[ ] Tool registry maps to backend APIs only.
[ ] Model adapter is local/free-first.
[ ] Deterministic fallback works without paid model keys.
[ ] OpenCode-style provider thinking is optional configuration only.
[ ] OpenCode is not required to run the HR demo.
[ ] No real SaaS credentials are required.
[ ] No paid model provider is required.
[ ] README clearly states this is a stripped optional variant.
[ ] The final candidate submission is not overloaded by Agent_X internals.
[ ] The HR onboarding prototype still works if Agent_X Lite is removed.
```

---

## 23. Final Instructional Summary

Do this:

```text
1. Keep the HR onboarding prototype centered on n8n + FastAPI + PostgreSQL.
2. Clone or fork Agent_X separately only for inspection and selective reuse.
3. Prefer extracting into a new small repo rather than endlessly deleting inside the full fork.
4. Inventory every top-level component before copying or excluding anything.
5. Preserve provenance and license/attribution notes for copied material.
6. Rewrite most Agent_X ideas into small HR-specific boundaries.
7. Keep or adapt only UI, tool registry, model-provider, and evidence ideas.
8. Do not copy full L0/L1/L2 governance layers into runtime.
9. Connect Agent_X Lite only to the FastAPI backend.
10. Keep model behavior local/free-first with deterministic fallback.
11. Treat OpenCode compatibility as provider-config compatibility, not a hard runtime dependency.
12. Keep n8n as the official workflow orchestrator.
13. Prove Agent_X Lite is removable.
14. Use Agent_X Lite only as optional polish/evidence.
15. Do not submit the full Agent_X fork as the candidate exercise.
```

Final rule:

```text
Agent_X Lite should help demonstrate the HR onboarding agent. It must never become the main thing being demonstrated.
```

---

## 24. Final Verdict

This v4 guide is 10/10 for the current planning purpose because it gives a safe, professional reuse strategy with clear boundaries:

```text
Agent_X is used as inspiration and selective component source.
Agent_X Lite is optional and removable.
The HR onboarding prototype remains the real deliverable.
The evaluator sees n8n orchestration, FastAPI logic, PostgreSQL auditability, mocked SaaS integrations, and optional console/evidence support.
OpenCode compatibility is treated as model-provider configuration compatibility, not as a required runtime dependency.
```

That is the correct balance between reuse, focus, and candidate-exercise practicality.
