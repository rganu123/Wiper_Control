# Product Requirements Document (PRD): Rain-Adaptive Wiper Control System

**Document status:** Draft for engineering review  
**Version:** 1.0  
**Date:** 2026-10-27

## 1. Purpose

Design an automotive wiper control system that combines driver input and rain-sensor feedback to control wiper motor speed, while respecting motor torque, thermal, timing, and microcontroller constraints.

This document defines product-level requirements. Exact motor ratings, sensor characteristics, vehicle interfaces, environmental limits, and safety targets must be confirmed during system design.

## 2. Product Goals

- Provide driver-selectable wiper operation, including OFF and time-based intermittent operation.
- Automatically adapt wiping speed to measured rain intensity when automatic mode is selected.
- Execute sensing, control decisions, and motor commands on a Renesas or Texas Instruments (TI) microcontroller.
- Support small, medium, and large motor/wiper configurations with configuration-specific torque limits.
- Prevent operation beyond the approved thermal duty limits, including the stated eight-hour continuous-operation constraint unless a validated thermal-management solution is approved.

## 3. Scope

### In scope
- Driver input acquisition and mode selection.
- Rain sensing and intensity estimation.
- Wiper speed/interval control.
- Motor drive command generation and feedback monitoring where supported by the selected hardware.
- Motor configuration selection (S/M/L) and torque-limit enforcement.
- Thermal and fault monitoring.
- Embedded application memory and resource budgeting.
- Verification of timing, control, and safety requirements.

### Out of scope until specified
- Mechanical linkage design and vehicle packaging.
- Detailed motor-driver power electronics design.
- Vehicle-network protocol definition (CAN/LIN/Ethernet).
- Regulatory certification and vehicle-level homologation.
- Exact cybersecurity, functional-safety, and diagnostic standards allocation.

## 4. Operating Concept

The system has two control inputs:

1. **Driver input:** OFF/ON and a selectable intermittent timing or sensitivity setting.
2. **Rain sensor:** rain presence and estimated rain intensity.

The selected operating mode determines how these inputs are combined. Driver OFF always requests wiper stop, subject to any vehicle-specific park-position behavior. In manual intermittent mode, the driver-selected interval governs wiping. In automatic mode, rain intensity governs the interval/speed within calibrated limits.

The controller must not exceed the selected motor configuration's approved speed, current, torque, or thermal limits. The 500 Hz requirement is treated as a control-loop execution target (2 ms period), not as a requirement to mechanically cycle the wipers 500 times per second.

## 5. User and System Requirements

Requirement IDs are intended to remain stable for traceability.

### 5.1 Driver Input and Modes

| ID | Requirement | Verification |
|---|---|---|
| PR-001 | The system shall provide a driver-selectable OFF mode. | Test |
| PR-002 | The system shall provide an ON/continuous-wipe mode, subject to the approved vehicle interface. | Test |
| PR-003 | The system shall provide an intermittent mode with a configurable time interval. | Test |
| PR-004 | The system shall provide an automatic mode that uses rain-sensor intensity to adjust wiping behavior. | Test |
| PR-005 | The system shall define and implement deterministic priority between driver commands and automatic control. Driver OFF shall inhibit new wipe commands, except for a defined safe park sequence if required by the vehicle design. | Test / Review |
| PR-006 | The system shall reject or safely handle invalid, contradictory, noisy, or unavailable driver-input signals. | Fault injection |
| PR-007 | The system shall apply input filtering/debounce appropriate to the selected input hardware without violating response-time requirements. | Test |

### 5.2 Rain Sensing and Adaptive Control

| ID | Requirement | Verification |
|---|---|---|
| PR-010 | The system shall acquire rain-sensor data and determine a calibrated rain-intensity level. | Test |
| PR-011 | In automatic mode, the system shall map rain intensity to a calibrated wipe interval and/or motor-speed command. | Test |
| PR-012 | The mapping shall define thresholds, hysteresis, filtering, and transition behavior to avoid rapid mode or speed oscillation. | Test |
| PR-013 | The system shall detect rain-sensor data that is stale, out of range, implausible, or unavailable. | Fault injection |
| PR-014 | When rain-sensor data is invalid, the system shall enter a documented fallback behavior and inform the driver through the available vehicle interface, if supported. | Test / Review |
| PR-015 | The system shall not interpret sensor intensity as a direct motor-speed command unless the control calibration explicitly defines that relationship. | Review / Test |

### 5.3 Real-Time Control and Microcontroller

| ID | Requirement | Verification |
|---|---|---|
| PR-020 | The controller shall execute the designated high-priority sensing/control task at a target frequency of 500 Hz (2 ms period). | Timing measurement |
| PR-021 | The 500 Hz task shall complete within its 2 ms execution period under the defined worst-case workload, with engineering-approved timing margin. | WCET analysis / Stress test |
| PR-022 | The controller shall generate motor commands through a compatible motor driver and shall use feedback signals where required by the selected control strategy. | Integration test |
| PR-023 | The selected Renesas or TI MCU shall have sufficient CPU, RAM, flash, timer/PWM, ADC, communication, watchdog, and safety features for the application. | Design review |
| PR-024 | MCU selection shall be based on documented peripheral, timing, memory, environmental, lifecycle, and safety requirements; no specific MCU is mandated by this draft. | Design review |
| PR-025 | Lower-priority application functions shall not block or cause deadline misses in the 500 Hz control task. | Stress test |
| PR-026 | The software shall include watchdog supervision and defined behavior for task overrun, lockup, or reset. | Fault injection |
| PR-027 | The software shall measure or estimate task execution time and expose timing-fault diagnostics during development and, where feasible, in production. | Test / Review |

### 5.4 Embedded Application and Memory

| ID | Requirement | Verification |
|---|---|---|
| PR-030 | The MCU shall host the wiper-control software and any approved supporting application functions required by the product. | Integration test |
| PR-031 | The project shall define a RAM and flash budget for code, stack, heap (if used), calibration data, diagnostics, and persistent settings. | Static analysis / Review |
| PR-032 | The control application shall operate within the approved memory budget and shall handle memory exhaustion or corrupted configuration safely. | Stress / Fault test |
| PR-033 | Persistent settings shall use a defined integrity mechanism, versioning strategy, and safe defaults. | Test / Review |
| PR-034 | Optional application workloads shall be isolated by scheduling and resource controls so they cannot compromise real-time control. | Stress test |

### 5.5 Motor Variants, Torque, and Drive Limits

| ID | Requirement | Verification |
|---|---|---|
| PR-040 | The product shall support configured Small (S), Medium (M), and Large (L) motor/wiper variants. | Configuration test |
| PR-041 | Each variant shall have an approved parameter set covering motor rating, allowable torque, current, speed, linkage/wiper length, and thermal limits. | Review / Test |
| PR-042 | The controller shall enforce the maximum permitted torque/current/speed limits for the selected motor and driver, using available feedback and validated limits. | Test |
| PR-043 | The commanded operating point shall remain within the motor manufacturer's specified operating envelope. | Test / Analysis |
| PR-044 | The system shall detect motor stall, overload, or abnormal current when the required sensing hardware is available. | Fault injection |
| PR-045 | On detected overload or stall, the system shall apply the defined protective response, such as limiting drive, stopping the motor, and recording a diagnostic. | Test |
| PR-046 | Motor variant configuration shall be validated at startup; invalid or unsupported configuration shall not enable unrestricted motor operation. | Fault injection |
| PR-047 | Motor and linkage sizing shall be verified against the maximum expected friction, aerodynamic/water load, ice or obstruction assumptions, supply voltage, and environmental conditions. | Engineering analysis / Test |

### 5.6 Thermal Management and Duty Cycle

| ID | Requirement | Verification |
|---|---|---|
| PR-050 | The system shall prevent continuous operation beyond eight hours unless the motor, driver, and thermal design have been validated for the required duty cycle. | Test / Analysis |
| PR-051 | The eight-hour constraint shall be implemented as a defined duty-cycle/thermal policy, not as an arbitrary shutdown that creates an unsafe visibility condition. | Safety review |
| PR-052 | The design shall monitor motor/driver temperature directly or use a validated thermal model where temperature sensing is not available. | Test / Analysis |
| PR-053 | If the required operating duty cycle exceeds component thermal ratings, the design shall add an approved heat-dissipation solution or select suitably rated components. | Thermal analysis |
| PR-054 | Thermal protection shall use calibrated warning, derating, and shutdown thresholds based on component specifications and vehicle safety analysis. | Test |
| PR-055 | Thermal protection shall define a safe response that considers driver visibility and avoids abrupt loss of wiping without a documented hazard assessment. | Safety review / Test |
| PR-056 | The system shall recover from thermal protection only when the approved recovery conditions are met. | Test |

### 5.7 Diagnostics and Fault Handling

| ID | Requirement | Verification |
|---|---|---|
| PR-060 | The system shall detect and record defined faults, including sensor failure, motor overload/stall, overtemperature, invalid configuration, watchdog reset, and control-task overrun where applicable. | Fault injection |
| PR-061 | Each fault shall have a defined detection condition, severity, response, recovery condition, and diagnostic indication. | Review / Test |
| PR-062 | The system shall transition to a documented fallback state when critical inputs or control functions are unavailable. | Fault injection |
| PR-063 | The system shall avoid unintended motor activation during startup, reset, brownout, or configuration failure. | Test |
| PR-064 | Diagnostic reporting shall use the vehicle interface selected during system architecture. | Integration test |

## 6. Proposed Control Behavior

| Driver mode | Sensor status | Expected behavior |
|---|---|---|
| OFF | Any | Inhibit new wipe requests; complete safe park behavior if required |
| Manual continuous | Any | Run at the driver-selected/approved continuous setting, within motor limits |
| Manual intermittent | Any | Wipe using the configured time interval |
| Automatic | Valid | Adapt wipe interval/speed using calibrated rain-intensity mapping |
| Automatic | Invalid/stale | Use the approved fallback, indicate fault if supported, and avoid uncontrolled operation |
| Any active mode | Overload/stall | Apply protective response defined by safety analysis |
| Any active mode | Overtemperature | Apply validated derating/protection policy while considering visibility safety |

## 7. Timing and Performance Targets

- **Control-loop target:** 500 Hz, equivalent to a 2 ms period.
- **Deadline:** Complete the designated task within 2 ms under the defined worst-case workload, with margin established by engineering.
- **Sensor-to-command latency:** To be specified after sensor update rate, filtering, and motor-driver interface are selected.
- **Rain-intensity response thresholds and wipe intervals:** To be calibrated and validated with representative rain conditions.
- **Motor speed, torque, current, temperature, and duty-cycle limits:** Must come from the selected motor/driver datasheets and validated system analysis.

**Important clarification:** A 500 Hz control loop does not imply a 500 Hz wiper-motor rotation or wiping frequency. The mechanical wiper cycle is much slower and must follow the motor and linkage ratings.

## 8. Motor Variant Configuration Template

Populate this table with approved supplier and vehicle data before implementation.

| Parameter | Small (S) | Medium (M) | Large (L) |
|---|---|---|---|
| Supported wiper/linkage length | TBD | TBD | TBD |
| Rated voltage range | TBD | TBD | TBD |
| Rated torque | TBD | TBD | TBD |
| Maximum permitted torque | TBD | TBD | TBD |
| Rated / maximum speed | TBD | TBD | TBD |
| Continuous / peak current | TBD | TBD | TBD |
| Stall-current limit and response | TBD | TBD | TBD |
| Operating temperature range | TBD | TBD | TBD |
| Maximum approved duty cycle | TBD | TBD | TBD |
| Thermal warning / derating / shutdown thresholds | TBD | TBD | TBD |
| Motor-driver part number | TBD | TBD | TBD |

The controller must not invent missing ratings or use the S/M/L label alone to infer safe limits.

## 9. MCU Selection Criteria

Evaluate candidate Renesas and TI MCUs against:

- Worst-case execution time for the 500 Hz control task.
- CPU headroom for diagnostics and supporting application functions.
- RAM/flash capacity and memory-protection capabilities, where applicable.
- PWM/timer resources and required motor-driver interface.
- ADC and digital input resources for sensor and current/temperature feedback.
- Watchdog, brownout detection, clock monitoring, and fault-handling support.
- Required automotive temperature range, qualification, lifecycle, and supply availability.
- Required functional-safety capability and development evidence, if allocated by the vehicle safety concept.
- Debug, trace, calibration, and production-programming support.

Select the MCU only after the requirements and peripheral needs are confirmed. No Renesas or TI part number is assumed in this PRD.

## 10. Safety, Reliability, and Engineering Considerations

- Perform a vehicle-level hazard analysis to determine safe behavior for loss of wiping, unintended wiping, sensor failure, and thermal shutdown.
- Determine whether ISO 26262 functional-safety activities or other automotive standards apply; do not assume an ASIL without analysis.
- Define electrical protection for reverse polarity, transients, load dump, ESD, and brownout as applicable to the vehicle electrical architecture.
- Define environmental validation for temperature, vibration, humidity, water ingress, and electromagnetic compatibility.
- Validate the wiper's ability to clear the required field of view under the specified rain and environmental conditions.
- Treat ice, obstruction, dry-glass friction, worn blades, and linkage binding as operating cases for mechanical and current/torque validation.

## 11. Verification and Validation Plan

| Test ID | Test | Acceptance basis |
|---|---|---|
| VV-001 | Verify OFF, continuous, and intermittent driver modes. | Behavior matches mode requirements |
| VV-002 | Sweep rain-sensor intensity across calibrated levels. | Wipe behavior follows approved mapping |
| VV-003 | Inject stale, disconnected, noisy, and out-of-range sensor data. | Defined fallback occurs |
| VV-004 | Measure 500 Hz task period and worst-case execution time under load. | No deadline misses; approved timing margin met |
| VV-005 | Run supporting application workload concurrently with control task. | Control deadlines and memory budgets remain satisfied |
| VV-006 | Test S/M/L configurations and invalid configuration values. | Correct limits selected; invalid setup is safe |
| VV-007 | Test motor overload, stall, and current-limit behavior. | Protective response matches specification |
| VV-008 | Perform thermal/duty-cycle tests through the approved operating profile. | Component ratings and thermal policy are respected |
| VV-009 | Inject watchdog reset, brownout, and startup faults. | No unintended motor activation |
| VV-010 | Validate thermal recovery and driver notification behavior. | Recovery follows approved thresholds and safety policy |

## 12. Open Questions / Decisions Required

1. What vehicle supply voltage and electrical architecture are required (for example, 12 V or 24 V)?
2. Which rain sensor and interface will be used, and what are its update rate and diagnostics?
3. Does “500 Hz” apply to the control task, sensor sampling, PWM, or another function? This PRD assumes the high-priority control task.
4. What are the exact S/M/L wiper lengths, motor part numbers, torque/current/speed ratings, and linkage loads?
5. Is motor position/park feedback available? Is motor current and/or temperature feedback available?
6. Which driver controls and modes are required (switch positions, intermittent dial, sensitivity setting, automatic mode)?
7. What is the required fallback when the rain sensor fails?
8. Does eight hours mean continuous motor energization, cumulative operation, or a defined duty-cycle profile? What visibility/safety analysis governs protective shutdown?
9. What application is hosted on the MCU, and what are its CPU, RAM, flash, and scheduling needs?
10. Which vehicle interface and diagnostic protocol are required?
11. What environmental, functional-safety, cybersecurity, and regulatory requirements apply?

## 13. Acceptance Criteria

The product requirement baseline is ready for detailed design when:

- Driver modes and input priority are approved.
- Rain-intensity calibration and sensor-failure behavior are defined.
- The 500 Hz task scope and timing budget are confirmed.
- S/M/L motor ratings and configuration parameters are supplied by engineering.
- Torque/current/speed limits and overload responses are defined.
- The eight-hour duty-cycle policy is reconciled with visibility safety and thermal validation.
- MCU, motor driver, sensor, diagnostics interface, and memory budgets are selected.
- Verification cases are traceable to all approved requirements.

---
**End of document**