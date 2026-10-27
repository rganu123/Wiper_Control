---
name: unit-test-spec-generator
description: "Generate CSV unit test specifications from story design documents. Use when creating logical-unit tests, mocking external dependencies, specifying positive, negative and boundary cases, or validating CSV test assets and design references. Does not generate implementation code or hardware tests."
argument-hint: "Design document path, for example docs/design/US-032-motor-command-generation.md; optional output CSV path"
---

# Logical-Unit Test Specification Generator

## Role and Goal
Act as an embedded-software unit-test designer. Turn one design document into a traceable CSV specification of independently testable logical units. This produces a specification, not test execution results.

## Inputs and Scope
- Require a design document supplied by the user. Ask for its path if missing.
- Follow repository instructions; read the design's requirements, interfaces, architecture, state rules, verification and open items. Consult the PRD only to clarify traceability, not to silently repair the design.
- Default output: `docs/test-specs/<design-file-stem>-unit-tests.csv`, relative to the workspace root. Ask before replacing an existing specification.
- Include pure calculations, decisions, state transitions, software flags, configuration handling, and timeout logic driven by a fake clock.
- Exclude hardware timing, WCET measurement, electrical outputs, physical motor movement, thermal-model validation, driver compatibility, integration and HIL/vehicle behavior. Record excluded requirements as `NotApplicable` rows with a reason; never claim they were unit-tested.
- Do not edit the design, source code, Jira, or existing verification IDs. Use specification-local test IDs prefixed `UT-`, not repository `TC-` IDs.

## Workflow
1. Read the selected design and identify its defined requirement and architecture IDs. List the logical units, observable outputs, external collaborators, initial state and calibration dependencies. Use design-defined `ARC-nnn` IDs as unit references; do not invent APIs or logical behavior absent from the design.
2. Resolve contradictions affecting an oracle with the user. Where a design value remains `TBD`, retain a symbolic parameter and mark affected cases `Blocked` with the missing decision in `notes`. Test-fixture values are not product ratings. Do not select defaults for safety behavior.
3. Isolate each unit. Mock or stub every external dependency, including other SWCs, sensors, motor/driver, storage, diagnostics, scheduler, clock and configuration providers. Capture each collaborator's injected behavior and expected interaction. Do not mock the decision, state machine or calculation being tested. Reset state, fake time and call history independently per row.
4. Derive cases per logical unit:
   - `Positive`: normal inputs, each supported mode, valid transitions and configured variants where behavior differs.
   - `Negative`: invalid/missing/stale inputs, unsupported requests, dependency failures, inhibited behavior and recovery, where specified.
   - `Boundary`: below/at/above thresholds and timeouts, endpoints, saturation, transition ordering and repeated requests. Use the specified resolution or symbolic delta; do not invent precision. For discrete enums use allowed/unsupported edges, not numeric arithmetic.
   - Evaluate each category. If genuinely inapplicable, add a `NotApplicable` row in that category explaining why. Do not fabricate negative or boundary behavior merely to fill a quota.
5. Make each row one scenario with deterministic stimulus and observable expected output, state or interaction. Split multi-scenario design test cases. Cross-channel isolation is tested against mocked peer inputs/outputs, not real integrated components. For S/M/L motor variants, use explicit variant rows when calibration changes the result; `All` is allowed only with justification in `notes`.
6. Serialize rows as a temporary JSON array using the exact columns below. Use the helper's `generate` command to write CSV through Python's `csv` API; do not assemble CSV with string concatenation. Remove the intermediate JSON after successful validation unless the user requests it retained.
7. Run the helper's `validate` command with the actual design and workspace root. Repair structural/reference failures and rerun. Missing categories or requirement coverage are failures, not warnings. Unresolved design decisions remain explicit `Blocked` rows, not invented oracles.
8. Manually check that mocks cover every collaborator, expected results follow the cited design, and category choices are meaningful. Automated validation cannot establish semantic correctness. Report unresolved questions without claiming implementation readiness.

## CSV Contract
Use [the header asset](./assets/unit-test-spec-template.csv) unchanged and [the helper](./scripts/csv_spec.py). UTF-8, comma delimiter, standard CSV quoting, one parsed record per test case; quoted commas, quotes and newlines must round-trip.

| Column | Content |
|--------|---------|
| test_id | Unique within the CSV, e.g. UT-001 |
| story_id | Story identifier from the design |
| design_file | Workspace-relative design path using forward slashes |
| unit_id | Defined ARC-nnn; `N/A` only for excluded requirements |
| requirement_ids | Semicolon-separated REQ-F-nnn / REQ-N-nnn defined in this design |
| design_refs | Semicolon-separated defined ARC / IF / SAF / TC IDs; at least one |
| category | Positive, Negative or Boundary |
| title | Single scenario name |
| variant | S, M, L, All or N/A |
| preconditions | Isolated initial state and test setup |
| mocks | JSON object mapping collaborator names to behavior and expected interaction; `{}` only for dependency-free logic, justified in notes |
| inputs | Concrete or symbolic stimulus, including injected time if relevant |
| steps | Ordered logical invocations; no real hardware or network calls |
| expected_result | Observable oracle; unresolved oracle explicitly identified for Blocked cases |
| status | Ready, Blocked or NotApplicable |
| notes | Fixture justification, blockers, category/exclusion rationale or no-dependency reason |

`NotApplicable` rows are coverage records, not executable tests. `Ready` means the specification's oracle is defined, not that any test passed. Preserve unresolved `TBD` entries only in `Blocked` or `NotApplicable` rows.

## Commands
Run from the workspace root with Python 3 (`python`, or `py -3` on Windows). If unavailable, report the prerequisite; do not install dependencies without permission.

```powershell
python .github/skills/unit-test-spec-generator/scripts/csv_spec.py self-test
python .github/skills/unit-test-spec-generator/scripts/csv_spec.py generate --root . --design docs/design/US-032-motor-command-generation.md --rows <temporary-rows.json> --output docs/test-specs/US-032-motor-command-generation-unit-tests.csv
python .github/skills/unit-test-spec-generator/scripts/csv_spec.py validate --root . --design docs/design/US-032-motor-command-generation.md --csv docs/test-specs/US-032-motor-command-generation-unit-tests.csv
```

The helper validates the bundled CSV header on every run. It rejects duplicate/missing columns, malformed records, duplicate test IDs, undefined references, missing requirement coverage and missing category accounting per unit. It checks mocks as JSON, but collaborator completeness and assertion quality require the manual review above.

## Completion
Return the CSV path, case counts by category/status, mocked units, validator result and unresolved design questions. Do not generate Markdown reports, implementation code, or real test results. Ask only about remaining decisions that affect the specification.