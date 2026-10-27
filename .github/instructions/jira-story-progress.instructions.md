---
description: "Jira assignment, status transitions and phase comments for the WIPC story delivery agents. Read explicitly whenever an agent starts, completes, blocks or hands off a story phase."
---
# Jira Story Progress Policy

## Scope and Permission
- The user has authorized progress updates on the selected WIPC story: assign it to the requesting user, start work using an available In Progress transition, and comment during every phase. This permission does not include editing requirements, deleting issues/comments, creating issues, changing priority/sprints or modifying unrelated stories.
- Use Atlassian MCP, not shell scripts, copied tokens or REST credentials. Resolve the site once and pass it with every site-scoped call. Load available tools before using them; discover operations not exposed as primary tools and use the read/write operation matching their risk tier.
- If no verified Jira key exists for a standalone local design/CSV task, ask for the WIPC key before updating Jira. Do not select an issue merely because its summary resembles a local file.

## Assignment and Start
1. Read the selected issue and verify its WIPC key/project. Read the authenticated user's identity through `atlassianUserInfo`; interpret "assign to me" as the human requesting the workflow, never the AI agent. If the request identifies another human, resolve that person explicitly rather than assuming the authenticated account represents them.
2. Verify that account can be assigned to this project using assignable-user metadata. Reuse the confirmed account ID in the handoff packet; never invent it from a display name or email. Assign the issue if it is not already assigned to that user, then re-read to verify. If ambiguous or not assignable, stop and ask.
3. Discover/list the issue's available transitions. If it is not already in an active In Progress state, use a returned transition ID leading to the project's In Progress status (or a single clearly equivalent in-progress-category destination). If several destinations fit or none is available, ask rather than inventing a transition ID or workflow mapping.
4. Re-read the issue before any later assignment/transition. Preserve an existing correct assignee/status and avoid repeating writes. If a human moved it to Done/Cancelled during execution, stop to confirm whether to reopen instead of undoing that action.

## Update Ownership and Idempotency
- With a coordinator, Story Delivery Workflow resolves identity, assigns the story, starts In Progress and posts one workflow-start comment. Each specialist owns its phase-start and phase-result comments. The coordinator records only workflow-level blocks/completion, not duplicate specialist updates.
- When run standalone, a specialist performs the assignment/start checks itself, then its own phase comments. Reuse `requester_account_id` and `jira_progress` receipts when handed off; verify rather than blindly trusting them.
- Use a stable marker in each comment: `[WIPC delivery | <story-key> | <phase> | attempt <n> | <start/result>]`. Phases are workflow, design, review, specification, automation and implementation. Increment the attempt only for a real rework/re-execution, not a network retry.
- Before posting, inspect the packet's comment receipts and read existing issue comments with the purpose-built comment operation (issue metadata alone may omit bodies). Reuse/update only a known comment written for that same marker, or avoid a duplicate; never overwrite another person's comment. Carry returned comment IDs/URLs forward.
- On an ambiguous timeout/write result, read the issue/comments to check whether the write succeeded before retrying. On a clear tool validation error, correct the input and retry once. Do not repeatedly create comments or reassign the story.

## Comments for Every Phase
Post a concise start comment with phase/attempt, scope, input artifacts and intended checks. After work, post a result comment with outcome, artifact paths, evidence, remaining blockers and next agent. Repository-relative paths must be labeled as local/unpushed; do not fabricate GitHub URLs or imply files are published.

| Phase | Result comment must include |
|-------|-----------------------------|
| Design | Design path, requirement count, validation performed, open decisions and handoff to reviewer |
| Review | GREEN/REWORK/BLOCKED, Blocker/Major counts, must-fix finding IDs, recommendations and writer/spec-writer routing |
| Specification | CSV/design paths, Ready/Blocked/NotApplicable and category counts, actual validator command/result |
| Automation | Test paths, UT mapping, commands, collected/passed/failed/skipped counts, expected RED or MISSING_IMPLEMENTATION baseline; confirm no production code was changed |
| Implementation | Changed source paths, RED-to-GREEN evidence, final test/quality-gate results and remaining exclusions |
| Workflow | Start identity/status verification; final phase summary and outstanding acceptance or deployment checks |

- Record blockers and questions in Jira even when a phase cannot finish. If Jira itself is unavailable, keep the intended update in the handoff response as pending, report the error and pause before the next phase; never claim it was posted or repeat completed artifact work just to retry synchronization.
- Keep the story In Progress across normal phases and review rework. Use optional Review/Blocked statuses only if the project exposes an unambiguous mapping and the workflow/user approves it. A phase result called GREEN does not mean Jira Done.
- Do not mark the story Done merely because logical-unit tests pass. Report remaining acceptance/HIL/safety/deployment obligations, and ask before a final Done transition unless the user has explicitly authorized completion and every story acceptance criterion is verified. Discover the transition and re-read after it.
- Do not post secrets, private keys, raw credentials, sensitive environment dumps or claims of unexecuted tests in comments.

## Source Revision and Handoff Safety
- Assignment, transitions and comments change Jira's `updated` timestamp. Keep `jira_revision` as the latest fetched timestamp for auditing, not as the sole approval fingerprint.
- Preserve a `requirements_snapshot` of the exact key, summary, description/acceptance criteria, relevant requirement custom fields and dependency information consumed by design/tests. Record which fields are compared; include labels only when they affect scope or variant selection.
- Re-read before each phase and compare those fields with the approved snapshot. Progress-only assignee/status/comment/timestamp changes do not invalidate design review. Any actual requirement or relevant dependency change, or any design edit, invalidates the corresponding review and downstream artifacts and returns to writer/reviewer before proceeding.
- Add `requester_account_id`, `requirements_snapshot` and `jira_progress` to every handoff. Progress receipts contain the current assignee/status, phase/attempt, successful transition/comment IDs or URLs, latest fetched timestamp, and pending/failed updates. Use actual returned values only; never treat a pending write as success.
- A local file-write prohibition or tests-only boundary remains in force. This policy allows only the Jira progress operations above; it grants no additional production-code or artifact-editing permission.