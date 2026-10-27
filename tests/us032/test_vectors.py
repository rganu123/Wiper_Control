"""Literal US-032 CSV stimuli/oracles, not an implementation model."""

I = ("INHIBITED", 0, 0, 0, 0, 0, 0, 0)
Z = ("STOPPED", 0, 0, 0, 0, 0, 0, 0)
R = ("RUNNING", 40, 1, 0, 0, 0, 0, 0)
H = ("RUNNING", 60, 1, 0, 0, 0, 0, 0)
C = ("CYCLE", 40, 1, 0, 0, 0, 0, 0)
P = ("PARKING", 40, 1, 0, 0, 0, 0, 0)
O = ("OVERRUN", 0, 0, 0, 0, 0, 1, 0)
DONE = ("STOPPED", 0, 0, 0, 0, 0, 0, 1)
BADREQ = ("PARKING", 40, 1, 0, 1, 0, 0, 0)
RD = ("RUNNING", 40, 1, 0, 0, 1, 0, 0)
CD = ("CYCLE", 40, 1, 0, 0, 1, 0, 0)
PD = ("PARKING", 40, 1, 0, 0, 1, 0, 0)
ZD = ("STOPPED", 0, 0, 0, 0, 1, 0, 0)
DDONE = ("STOPPED", 0, 0, 0, 0, 1, 0, 1)
OD = ("OVERRUN", 0, 0, 0, 0, 1, 1, 0)
R50 = ("RUNNING", 50, 1, 0, 0, 0, 0, 0)


def tick(now, mode, expected, *, park=None, speed=None, peer=0,
         inhibit=False, request_present=True, refreshed=None,
         park_valid=True, park_time=None, speed_valid=True, speed_time=None):
    return dict(action="step", now=now, mode=mode, expected=expected,
                park=park, speed=speed, peer=peer, inhibit=inhibit,
                request_present=request_present, refreshed=refreshed,
                park_valid=park_valid, park_time=park_time,
                speed_valid=speed_valid, speed_time=speed_time)


def reset(config=None, peer=0, release=True):
    return dict(action="reset", config=config or {}, peer=peer, release=release)


CASES = {}


def case(number, steps, config=None, peer_config=None, init_only=False):
    assert number not in CASES
    CASES[number] = dict(steps=steps, config=config or {},
                         peer_config=peer_config, init_only=init_only)


case(1, [], init_only=True)
case(2, [tick(2, "SINGLE_WIPE", C, park=True),
         tick(4, "SINGLE_WIPE", O, park=True), reset(release=False)],
     dict(park_available=True, park_debounce_ms=0, departure_timeout_ms=2))
case(3, [tick(2, "RUN_LOW", R), tick(2, "RUN_HIGH", H), tick(4, "STOP", Z)])
case(4, [tick(2, "RUN_LOW", R), tick(4, "RUN_HIGH", H),
         tick(6, "STOP", Z), tick(8, "STOP", Z)])
case(5, [tick(2, "RUN_LOW", R), tick(4, "STOP", Z), tick(6, "PARK", P)],
     dict(channel="REAR"))
case(6, [tick(2, "RUN_LOW", R), tick(2, "RUN_LOW", R, peer=1),
         tick(4, "STOP", Z), tick(4, "RUN_LOW", R, peer=1)],
     peer_config=dict(channel="REAR"))
case(7, [tick(2, "RUN_LOW", R), tick(2, "RUN_LOW", R, peer=1),
         tick(4, "RUN_LOW", I, peer=1, inhibit=True), tick(4, "RUN_LOW", R)],
     peer_config=dict(channel="REAR"))
case(8, [tick(2, "RUN_LOW", R), tick(2, "RUN_LOW", R, peer=1),
         tick(4, -1, BADREQ), tick(4, "RUN_LOW", R, peer=1)],
     peer_config=dict(channel="REAR"))
case(9, [tick(2, "RUN_LOW", R50, speed=1),
         tick(2, "RUN_LOW", R50, speed=1, peer=1),
         tick(4, "RUN_LOW", RD, speed=1, speed_valid=False, peer=1),
         tick(4, "RUN_LOW", R50, speed=1)], dict(speed_available=True),
     dict(channel="REAR", speed_available=True))
case(10, [tick(2, "SINGLE_WIPE", C), tick(2, "RUN_LOW", R, peer=1),
          tick(42, "SINGLE_WIPE", O), tick(42, "RUN_LOW", R, peer=1)],
     dict(timed_park_ms=60), dict(channel="REAR"))
case(11, [tick(2, "STOP", ("INHIBITED", 0, 0, 0, 1, 1, 0, 0),
               inhibit=True, request_present=False),
          tick(4, "STOP", I, inhibit=True, park=True, speed=1)],
     dict(park_available=True, speed_available=True, park_debounce_ms=0))
case(12, [tick(2, "SINGLE_WIPE", ("CYCLE", 50, 1, 0, 0, 0, 0, 0), park=True, speed=1),
          tick(4, "SINGLE_WIPE", O, park=True, speed=1),
          tick(6, "STOP", ("OVERRUN", 0, 0, 0, 1, 1, 1, 0), request_present=False),
          tick(8, "RUN_LOW", O, park=False, speed=1)],
     dict(park_available=True, speed_available=True, park_debounce_ms=0,
          departure_timeout_ms=2))
case(13, [tick(2, "RUN_LOW", R), tick(4, "RUN_HIGH", H)])
case(14, [tick(2, "RUN_LOW", ("RUNNING", 45, 1, 0, 0, 0, 0, 0)),
          tick(4, "RUN_HIGH", ("RUNNING", 65, 1, 0, 0, 0, 0, 0))],
     dict(variant="M", low=(45, 75, 2, 10), high=(65, 95, 3, 10)))
case(15, [tick(2, "RUN_LOW", R50),
          tick(4, "RUN_HIGH", ("RUNNING", 75, 1, 0, 0, 0, 0, 0))],
     dict(variant="L", low=(50, 80, 2, 10), high=(75, 100, 3, 10)))
case(16, [tick(2, "RUN_LOW", R)], dict(channel="REAR"))
case(17, [tick(2, "RUN_LOW", ("RUNNING", 45, 1, 0, 0, 0, 0, 0))],
     dict(channel="REAR", variant="M", low=(45, 75, 2, 10)))
case(18, [tick(2, "RUN_LOW", R50)],
     dict(channel="REAR", variant="L", low=(50, 80, 2, 10)))
case(19, [tick(2, "RUN_LOW", R50, speed=1)], dict(speed_available=True))
case(20, [tick(2, "RUN_LOW", R, speed=2)], dict(speed_available=True))
case(21, [tick(2, "RUN_LOW", ("RUNNING", 30, 1, 0, 0, 0, 0, 0), speed=3)],
     dict(speed_available=True))
case(22, [tick(2, "RUN_HIGH", H, speed=3)], dict(speed_available=True))
case(23, [tick(2, "PARK", ("PARKING", 50, 1, 0, 0, 0, 0, 0), speed=1)],
     dict(speed_available=True))
case(24, [tick(2, "SINGLE_WIPE", ("CYCLE", 50, 1, 0, 0, 0, 0, 0), speed=1)],
     dict(speed_available=True))
case(25, [tick(2, "RUN_LOW", R50, speed=1), tick(4, "RUN_LOW", R50, speed=1),
          tick(6, "RUN_LOW", ("RUNNING", 30, 1, 0, 0, 0, 0, 0), speed=3),
          tick(8, "RUN_LOW", R50, speed=1)], dict(speed_available=True))
for number, speed, expected in [
    (26, 1.55, ("RUNNING", 89, 1, 0, 0, 0, 0, 0)),
    (27, 1.5, ("RUNNING", 90, 1, 0, 0, 0, 0, 0)),
    (28, 1.45, ("RUNNING", 90, 1, 0, 0, 0, 0, 0)),
    (29, 5.95, ("RUNNING", 1, 1, 0, 0, 0, 0, 0)),
    (30, 6, ("RUNNING", 0, 0, 0, 0, 0, 0, 0)),
    (31, 6.05, ("RUNNING", 0, 0, 0, 0, 0, 0, 0)),
]:
    case(number, [tick(2, "RUN_HIGH", expected, speed=speed)],
         dict(speed_available=True, high=(60, 90, 3, 20)))
case(32, [tick(2, "RUN_LOW", RD, speed=0)],
     dict(speed_available=True, low=(40, 70, 2, "DBL_MAX")))
case(33, [tick(2, "RUN_LOW", RD, speed=2)],
     dict(speed_available=True, low=(40, 70, 0, "DBL_MAX")))
case(34, [tick(2, "RUN_LOW", R, speed=10)],
     dict(speed_available=True, low=(40, 70, 2, 0)))
case(35, [tick(2, "RUN_LOW", ("RUNNING", 40.25, 1, 0, 0, 0, 0, 0), speed=1.5)],
     dict(speed_available=True, low=(40.125, 70, 2, 0.25)))
case(36, [tick(2, "RUN_LOW", ("RUNNING", 40, 1, 1, 0, 0, 0, 0)),
          tick(4, "RUN_HIGH", ("RUNNING", 60, 1, 1, 0, 0, 0, 0)), tick(6, "STOP", Z)],
     dict(output="DIGITAL"))
case(37, [tick(2, "RUN_HIGH", ("RUNNING", 90, 1, 1, 0, 0, 0, 0), speed=0),
          tick(4, "RUN_HIGH", ("RUNNING", 0, 0, 0, 0, 0, 0, 0), speed=10)],
     dict(output="DIGITAL", speed_available=True, high=(60, 90, 3, 20)))
case(38, [tick(2, "RUN_LOW", ("RUNNING", 0, 0, 0, 0, 0, 0, 0))],
     dict(output="DIGITAL", low=(0, 0, 2, 10)))
case(39, [tick(2, "RUN_LOW", ("RUNNING", 100, 1, 0, 0, 0, 0, 0))],
     dict(low=(100, 100, 2, 0)))
case(40, [tick(2, "RUN_LOW", R), reset(dict(low=(55, 70, 2, 10))),
          tick(2, "RUN_LOW", ("RUNNING", 55, 1, 0, 0, 0, 0, 0))])
case(41, [tick(2, "RUN_LOW", R, park=True, park_valid=False,
               speed="NAN", speed_valid=False), tick(4, "RUN_HIGH", H), tick(6, "STOP", Z)])
case(42, [tick(2, "RUN_LOW", RD)], dict(speed_available=True))
case(43, [tick(2, "RUN_LOW", RD, speed=1, speed_valid=False)], dict(speed_available=True))
case(44, [tick(9, "RUN_LOW", R50, speed=1, speed_time=0)], dict(speed_available=True))
case(45, [tick(10, "RUN_LOW", RD, speed=1, speed_time=0)], dict(speed_available=True))
case(46, [tick(11, "RUN_LOW", RD, speed=1, speed_time=0)], dict(speed_available=True))
case(47, [tick(2, "RUN_LOW", RD, speed=1, speed_time=3)], dict(speed_available=True))
for number, speed, expected in [
    (48, "NAN", RD), (49, "INFINITY", RD), (50, "-INFINITY", RD),
    (51, -0.5, RD), (52, 0, H),
    (53, 0.5, ("RUNNING", 55, 1, 0, 0, 0, 0, 0)),
    (54, 9.5, ("RUNNING", 0, 0, 0, 0, 0, 0, 0)),
    (55, 10, ("RUNNING", 0, 0, 0, 0, 0, 0, 0)), (56, 10.5, RD),
]:
    case(number, [tick(2, "RUN_LOW", expected, speed=speed)], dict(speed_available=True))
case(57, [tick(2, "RUN_LOW", RD, speed=1, speed_valid=False),
          tick(4, "RUN_LOW", R50, speed=1)], dict(speed_available=True))
case(58, [tick(2, "RUN_LOW", R50, speed=1, speed_time=2),
          tick(10, "RUN_LOW", R50, speed=1, speed_time=2),
          tick(12, "RUN_LOW", RD, speed=1, speed_time=2)], dict(speed_available=True))
case(59, [tick(2, "RUN_LOW", RD),
          tick(4, "RUN_LOW", ("RUNNING", 50, 1, 0, 0, 1, 0, 0), speed=1),
          tick(6, "RUN_LOW", R50, park=True, speed=1)],
     dict(park_available=True, speed_available=True, park_debounce_ms=0))
case(60, [tick(2, "PARK", PD, park=True), tick(4, "PARK", PD, park=True),
          tick(6, "PARK", Z, park=True), tick(8, "PARK", Z, park=True)],
     dict(park_available=True))
case(61, [tick(2, "PARK", Z, park=True)], dict(park_available=True, park_debounce_ms=0))
case(62, [tick(2, "PARK", PD, park=True), tick(4, "PARK", PD, park=True, park_valid=False),
          tick(6, "PARK", PD, park=True), tick(8, "PARK", PD, park=True),
          tick(10, "PARK", Z, park=True)], dict(park_available=True))
case(63, [tick(2, "PARK", PD)], dict(park_available=True))
case(64, [tick(2, "PARK", PD, park=True, park_time=3)],
     dict(park_available=True, park_debounce_ms=0))
case(65, [tick(9, "PARK", Z, park=True, park_time=0)],
     dict(park_available=True, park_debounce_ms=0))
case(66, [tick(10, "PARK", PD, park=True, park_time=0)],
     dict(park_available=True, park_debounce_ms=0))
case(67, [tick(11, "PARK", PD, park=True, park_time=0)],
     dict(park_available=True, park_debounce_ms=0))
case(68, [tick(2, "PARK", PD, park=True, park_time=2),
          tick(4, "PARK", PD, park=True, park_time=2),
          tick(6, "PARK", Z, park=True, park_time=2)], dict(park_available=True))
case(69, [tick(2, "PARK", PD, park=True, park_time=2),
          tick(10, "PARK", PD, park=True, park_time=2),
          tick(12, "PARK", PD, park=True, park_time=2),
          tick(14, "PARK", PD, park=True), tick(24, "PARK", Z, park=True)],
     dict(park_available=True, park_debounce_ms=10))
case(70, [tick(8, "PARK", PD, park=True, park_time=0),
          tick(10, "PARK", PD, park=True), tick(12, "PARK", Z, park=True)],
     dict(park_available=True))
case(71, [tick(2, "STOP", ZD, park=True), tick(6, "STOP", Z, park=True),
          tick(8, "PARK", Z, park=False), tick(12, "PARK", Z, park=False)],
     dict(park_available=True))
case(72, [tick(2, "STOP", ZD, park=True), tick(6, "STOP", Z, park=True),
          tick(8, "PARK", PD, park=True, park_valid=False),
          tick(10, "PARK", PD, park=True), tick(12, "PARK", PD, park=True),
          tick(14, "PARK", Z, park=True)], dict(park_available=True))
case(73, [tick(2, "STOP", ZD, park=True), tick(6, "STOP", Z, park=True),
          tick(8, "RUN_LOW", R, park=False), tick(10, "RUN_LOW", R, park=True),
          tick(12, "RUN_LOW", R, park=False), tick(14, "RUN_LOW", R, park=True),
          tick(24, "RUN_LOW", RD, park=True)], dict(park_available=True))
for number, parked in [(74, True), (75, False)]:
    case(number, [tick(2, "RUN_LOW", R, park=parked), tick(16, "RUN_LOW", R, park=parked),
                  tick(18, "RUN_LOW", RD, park=parked), tick(20, "RUN_LOW", RD, park=parked)],
         dict(park_available=True, park_debounce_ms=0))
case(76, [tick(2, "RUN_LOW", R, park=True), tick(10, "RUN_HIGH", H, park=True),
          tick(18, "RUN_HIGH", ("RUNNING", 60, 1, 0, 0, 1, 0, 0), park=True)],
     dict(park_available=True, park_debounce_ms=0))
case(77, [tick(2, "STOP", ZD, park=True), tick(6, "STOP", Z, park=True),
          tick(8, "RUN_LOW", R, park=True), tick(20, "RUN_LOW", R, park=False),
          tick(24, "RUN_LOW", R, park=False), tick(38, "RUN_LOW", R, park=False),
          tick(40, "RUN_LOW", RD, park=False)], dict(park_available=True))
case(78, [tick(2, "RUN_LOW", R, park=True), tick(18, "RUN_LOW", RD, park=True),
          tick(20, "STOP", ZD, park=True, park_valid=False), tick(22, "STOP", ZD, park=True),
          tick(24, "RUN_LOW", RD, park=True)], dict(park_available=True, park_debounce_ms=0))
case(79, [tick(2, "STOP", ZD, park=True), tick(6, "STOP", Z, park=True),
          tick(8, "RUN_LOW", R, park=True), tick(24, "RUN_LOW", RD, park=True),
          tick(26, "STOP", ZD, park=False), tick(28, "STOP", ZD, park=False),
          tick(30, "STOP", Z, park=False)], dict(park_available=True))
case(80, [tick(2, "RUN_LOW", R, park=True), tick(18, "RUN_LOW", RD, park=True),
          tick(20, "RUN_LOW", ("INHIBITED", 0, 0, 0, 0, 1, 0, 0), park=True, inhibit=True),
          tick(22, "RUN_LOW", I, park=False, inhibit=True),
          tick(24, "RUN_LOW", Z, park=False), tick(26, "RUN_LOW", R, park=False)],
     dict(park_available=True, park_debounce_ms=0))
case(81, [tick(2, "RUN_LOW", R, park=True), tick(10, "STOP", Z, park=True),
          tick(100, "STOP", Z, park=True), tick(102, "RUN_LOW", R, park=True),
          tick(116, "RUN_LOW", R, park=True), tick(118, "RUN_LOW", RD, park=True)],
     dict(park_available=True, park_debounce_ms=0))
case(82, [tick(2, "STOP", ZD, park=True), tick(6, "STOP", Z, park=True),
          tick(8, "RUN_LOW", R, park=True), tick(24, "RUN_LOW", RD, park=True),
          tick(26, "STOP", ZD, park=False),
          tick(28, "STOP", ZD, park=False, park_valid=False), tick(30, "STOP", ZD, park=False),
          tick(32, "STOP", ZD, park=False), tick(34, "STOP", Z, park=False)],
     dict(park_available=True))
case(83, [tick(2, "SINGLE_WIPE", C, park=True), tick(4, "SINGLE_WIPE", C, park=True),
          tick(6, "SINGLE_WIPE", C, park=False), tick(8, "SINGLE_WIPE", DONE, park=True),
          tick(10, "SINGLE_WIPE", DONE, park=True)], dict(park_available=True, park_debounce_ms=0))
case(84, [tick(2, "SINGLE_WIPE", C, park=False), tick(4, "SINGLE_WIPE", DONE, park=True)],
     dict(park_available=True, park_debounce_ms=0))
case(85, [tick(2, "PARK", P, park=False), tick(4, "PARK", Z, park=True),
          tick(6, "PARK", Z, park=False)], dict(park_available=True, park_debounce_ms=0))
case(86, [tick(2, "PARK", Z, park=True), tick(4, "PARK", Z, park=True)],
     dict(park_available=True, park_debounce_ms=0))