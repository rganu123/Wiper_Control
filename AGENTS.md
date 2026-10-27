# AGENTS.md

Instructions for AI agents building the system design of an automatic rain-sensing wiper control system.

## 1. Project Overview

Goal: design a wiper control system for a passenger car that automatically activates the wipers and selects wiper speed based on rain sensor input.

In scope:
- Rain sensor input processing (intensity, sensitivity setting)
- Wiper control logic on the BCM
- Front and rear wipers (headlamp washers not in scope)
- Wiper motor driver output (park, low, high, and automatic speed steps; see default design parameters in section 2)
- Driver inputs: wiper stalk (OFF/AUTO/INT/LOW/HIGH), sensitivity, washer
- Vehicle inputs over CAN: vehicle speed, ignition state, hood state, door state, ambient temperature/ice, reverse gear (rear wiper)
- Rain sensor over LIN
- Diagnostics and degraded modes

Out of scope:
- Mechanical linkage and motor design
- Rain sensor optics and internal sensor algorithms
- Source code implementation (design documents only)

## 2. Standards and Conventions

- Functional safety: ISO 26262. Assign an ASIL to every safety goal and carry it to derived requirements.
- Process: ASPICE V-model. Keep requirements, design, and test levels separate and traceable.
- Software architecture: AUTOSAR Classic terminology (SWC, port, runnable, RTE, BSW, ComStack, MCAL).
- Diagrams: Mermaid only, inside fenced `mermaid` blocks. Use SysML/UML-style structure. Mandatory types: context/block, state, sequence, and AUTOSAR component (SWC).
- Units: SI units, with explicit tolerances and timing (ms) for every quantitative requirement.
- Regulations: UNECE, FMVSS 104, and the OEM specification apply. Do not cite clause numbers or numeric limits from memory; mark them `TBD` until verified.
- Do not invent values. Where a value is not given, use the industry-standard default in the table below, tag it `Assumption`, and list it in the document's open-items table for OEM confirmation. If no default exists, mark `TBD`.
- If uncertain about any requirement, value, or scope not covered below, ask the user instead of assuming.
- Do not invent proprietary part numbers or supplier-specific signals.

Default design parameters (all `Assumption`, confirm with OEM):

| Parameter | Default |
|-----------|---------|
| Rain sensor bus | LIN 2.x, BCM as master; frame layout supplier-specific (`TBD`) |
| Automatic wiper speed steps | 3: intermittent (rain-dependent interval), low continuous, high continuous |
| Sensitivity levels | 4 (stalk or rotary adjustment) |
| Rain intensity to speed mapping | Monotonic, with hysteresis and debounce; thresholds `TBD` |
| Manual override | Driver stalk input always has priority over AUTO |
| Rear wiper | Single speed and intermittent; auto-wipe on reverse gear when front wiper is active |
| Ignition off | Wipers complete the current cycle and park, then stop |

ID schemes (unique, never reused):

| Prefix | Meaning |
|--------|---------|
| `REQ-F-nnn` / `REQ-N-nnn` | Functional / non-functional requirement |
| `ARC-nnn` | Architecture element |
| `IF-nnn` | Interface or signal |
| `SAF-nnn` | Safety goal, hazard, or safety requirement |
| `TC-nnn` | Test case |

## 3. Deliverables and File Map

Write one file per deliverable under `docs/`. Create the folder if missing.

| File | Content |
|------|---------|
| `docs/01-requirements.md` | Functional and non-functional requirements |
| `docs/02-architecture.md` | Context, block diagram, AUTOSAR software architecture |
| `docs/03-state-machine.md` | Wiper control state machine and logic |
| `docs/04-interfaces.md` | Sensor, CAN, motor driver, and diagnostic signals |
| `docs/05-safety-analysis.md` | HARA, ASIL, FMEA, safe states |
| `docs/06-test-plan.md` | Verification strategy and test cases |

## 4. Content Guidance

### 01-requirements
- Cover: automatic activation on rain detection, rain intensity to wiper speed mapping (multiple automatic speed steps), sensitivity levels, vehicle-speed compensation, ambient temperature/ice handling, hood/door-open inhibit, intermittent interval, washer and wipe-after-wash, park position, rear wiper behaviour including reverse gear, manual override priority, and wiper-off when ignition is off.
- Tie requirements to the applicable UNECE, FMVSS 104, and OEM requirements; mark clauses `TBD`.
- Non-functional: response time from detection to first wipe, cycle accuracy, availability, diagnostic coverage, EMC and temperature range (as TBD where unknown).
- Each requirement must be atomic, testable, and have a rationale and a verification method.

### 02-architecture
- Include a system context diagram (driver, rain sensor, BCM, front and rear motors, CAN, LIN) and a block diagram.
- Define AUTOSAR SWCs (for example: rain sensor input, mode manager, wiper controller, motor output, diagnostics), their ports, runnables with cycle times, and the RTE/BSW mapping.
- Record key design decisions and alternatives considered.

### 03-state-machine
- Model modes OFF, AUTO, INT, LOW, HIGH, plus park/wipe cycle, washer sequence, and degraded/fault mode.
- Provide a Mermaid `stateDiagram-v2` plus a transition table (guard, action, requirement ID).
- Specify priority rules between driver input and automatic activation, and hysteresis/debounce for the rain signal.

### 04-interfaces
- List every signal with ID, direction, source, destination, type, range, unit, resolution, cycle time, timeout, and default/invalid value.
- Cover rain sensor interface (LIN; frame layout `TBD`), stalk inputs, CAN signals (including ambient temperature, hood/door, reverse gear), front and rear motor driver outputs, and diagnostic (DTC) interface.

### 05-safety-analysis
- Perform a HARA (hazardous events such as unintended wiping, loss of wiping in rain, blocked wiper, wiper stuck in the field of view) with severity, exposure, controllability, and resulting ASIL.
- Derive the ASIL from the HARA only; do not pre-assign a target ASIL.
- Derive safety goals, safe states, fault tolerant time interval, and safety requirements.
- Provide an FMEA covering sensor fault, signal loss/timeout, motor stall, driver fault, stuck-on, and stuck-off, with detection and reaction for each.

### 06-test-plan
- Define the verification strategy per level (MIL, SIL, HIL, vehicle) and entry/exit criteria.
- Each test case: ID, linked requirement(s), preconditions, steps, expected result, and level.
- Include fault-injection cases from the FMEA.

## 5. Workflow

1. Author in order 01 to 06. Do not start a document before its inputs exist.
2. Keep a traceability table (requirement, architecture element, interface, safety item, test case) in `docs/06-test-plan.md`.
3. Update earlier documents when later work reveals gaps, and keep IDs consistent.

Definition of done:
- No orphan IDs: every requirement traces to design and test; every safety requirement traces to a test.
- All Mermaid diagrams render.
- Open items (`TBD` and `Assumption`) are listed in each document.

## 6. Rules

- Keep documents concise. Prefer tables and diagrams over prose.
- Ask before changing the conventions in this file.
- Do not modify `README.md` unless asked.
