# Candidate Runtime Promotion Report

Generated at: `2026-06-12T00:00:00+00:00`
Tool version: `5.0` (manually edited)
Reviewer: `Project owner`
Review date: `2026-06-12`

## Changes applied

Runtime fixtures were manually edited to align with the demo story:

### app_fixtures/role_access_policies.json

| Role | Level | Required | Recommended | Optional |
|------|-------|----------|-------------|----------|
| Account Executive | L2 | HR Platform, Slack | Salesforce, Gong, Sales Slack Channels | Zoom, Google Drive |
| Software Engineer | L2 | HR Platform, Slack | GitHub, Engineering Slack Channels, CI/CD Dashboard | Developer Documentation, Staging Environment |
| HR Coordinator | L1 | HR Platform, Slack | HR Shared Drive, Onboarding Tracker | Zoom |
| Manager | L3 | HR Platform, Slack | Manager Dashboard, Approval Queue, Team Access Review | Reporting Dashboard |

All demo roles use `policy_version: "runtime-v1"`.

### app_fixtures/department_standards.json

| Department | Standard Systems |
|------------|-----------------|
| Sales | HR Platform, Slack, Salesforce, Gong, Sales Slack Channels |
| Engineering | HR Platform, Slack, GitHub, Engineering Slack Channels, CI/CD Dashboard |
| HR | HR Platform, Slack, HR Shared Drive, Onboarding Tracker |

### app_content/onboarding_tasks.json

Government-specific references (GSA, 18F, OGE 450, CHRIS, OLU, Employee Express, SF forms, federal building, oath of office) removed. Tasks now contain only generic company onboarding steps.

## Promoted files

- `app_fixtures/role_access_policies.json`
- `traceability/role_access_policies.traceability.json`
- `app_fixtures/department_standards.json`
- `traceability/department_standards.traceability.json`
- `app_content/onboarding_content.json`
- `traceability/content__onboarding_content.traceability.json`
- `app_content/training_content.json`
- `traceability/content__training_content.traceability.json`
- `app_content/hr_policies.json`
- `traceability/hr_policies.traceability.json`
- `app_content/onboarding_guides.json`
- `traceability/onboarding_guides.traceability.json`
- `app_content/onboarding_tasks.json`
- `traceability/onboarding_tasks.traceability.json`
- `app_content/role_skill_matrices.json`
- `traceability/role_skill_matrices.traceability.json`
- `app_content/security_practices.json`
- `traceability/security_practices.traceability.json`
- `app_knowledge/source_chunks.json`
- `traceability/source_chunks.traceability.json`
- `app_content/systems_and_access.json`
- `traceability/systems_and_access.traceability.json`
- `app_content/training_modules.json`
- `traceability/training_modules.traceability.json`
