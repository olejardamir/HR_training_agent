# Data Preparation Report

Command: `/home/glompy/Desktop/OTHER_PROJECTS/HR_training_agent/tools/data_prep/run_data_prep.py --force --generate-json --generate-fixtures --generate-content`

## Summary

- Raw files found: 22
- Readable files: 22
- Unreadable files: 0
- Unsupported files: 0
- Duplicate sources: 0
- Near-duplicate sources: 0
- Detected topics: general_onboarding, hr_faq, it_ticketing, manager_approval, privacy_compliance_training, role_access_policy, role_specific_training, salesforce_setup, security_training, slack_profile_setup, systems_access_training
- Cleaned source files generated: 22
- Review packet files generated: 11

## Source Coverage Gaps

- No source support for topic: employee_profile_setup

## Source Coverage Matrix

| Expected topic | Support level | Supporting source IDs | Notes |
|---|---|---|---|
| general_onboarding | strong | src_3a2a06cb8b7c, src_0554e04f527e, src_7e07631ff1ab, src_08ea2735d9d8, src_5c5042e7ae18 + |  |
| security_training | strong | src_3a2a06cb8b7c, src_79d367a0c008, src_5542b3f65212, src_d90b516ce1da, src_bc71d90aeef0 + |  |
| privacy_compliance_training | strong | src_3a2a06cb8b7c, src_7e07631ff1ab, src_d476a7c48f15, src_5c5042e7ae18, src_79d367a0c008 + |  |
| role_specific_training | strong | src_3a2a06cb8b7c, src_0554e04f527e, src_7e07631ff1ab, src_08ea2735d9d8, src_d476a7c48f15 + |  |
| systems_access_training | strong | src_72b55285f6ff, src_9f74c55137dd, src_4bb6ac8681cc, src_6b02b499456a |  |
| employee_profile_setup | none |  | No usable source support in RAW_DATA. |
| slack_profile_setup | strong | src_3a2a06cb8b7c, src_c289345f25e7, src_9f74c55137dd, src_4bb6ac8681cc, src_6b02b499456a + |  |
| salesforce_setup | strong | src_9f74c55137dd, src_4bb6ac8681cc, src_6b02b499456a |  |
| manager_approval | strong | src_7cb5866f767a, src_09610df40185 |  |
| it_ticketing | strong | src_9f74c55137dd, src_4bb6ac8681cc, src_6b02b499456a |  |
| role_access_policy | strong | src_9f74c55137dd, src_4bb6ac8681cc, src_6b02b499456a |  |
| hr_faq | strong | src_3a2a06cb8b7c, src_0554e04f527e, src_7e07631ff1ab, src_08ea2735d9d8, src_79d367a0c008 + |  |

## Validation

Result: **PASS**

## Safety Confirmation

- DB insertion performed: **no**
- Final runtime fixture JSON generated: **no**
- RAG chunks generated: **no**
- Vector/RAG index built: **no**
- Runtime agent modified to use processed data: **no**

## Later-Use Readiness

Grade: **ready_for_review**

This grade does not imply runtime approval. All outputs are candidate-only and require human review before DB/RAG/runtime use.
