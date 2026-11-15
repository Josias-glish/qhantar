"""Analytical tests for the QHANTAR engine (synthetic inputs, by design)."""
import numpy as np
import pytest

from qhantar import engine as E

D = np.deg2rad


def los_az(az_deg, inc_deg):
    """Target-to-sensor LOS whose horizontal part points to azimuth az_deg."""
    a, t = D(az_deg), D(inc_deg)
    return E.los_vector(np.sin(t) * np.sin(a), np.sin(t) * np.cos(a))


# 1. Motion parallel to the LOS -> |S| = 1
def test_parallel_to_los():
    u_los = los_az(80, 35)
    # downhill pointing horizontally away from the sensor, dipping at 90 - incidence:
    # exactly anti-parallel to the target-to-sensor LOS
    S = E.sensitivity(E.slope_vector(D(90 - 35), D(80 + 180)), u_los)
    assert S == pytest.approx(-1.0, abs=1e-12)


# 2. Motion perpendicular to the LOS -> S = 0
def test_perpendicular_to_los():
    u_los = los_az(80, 35)
    # S = sin(theta - beta) when downhill points towards the sensor: zero when beta = theta
    assert E.sensitivity(E.slope_vector(D(35), D(80)), u_los) == pytest.approx(0.0, abs=1e-12)
    # near-horizontal motion across the LOS azimuth
    for aspect_deg in (80 + 90, 80 - 90):
        u = E.slope_vector(D(1e-9), D(aspect_deg))
        assert E.sensitivity(u, u_los) == pytest.approx(0.0, abs=1e-8)


# 3. Flat slope -> not applicable (state 0, reason "flat")
def test_flat_is_not_applicable():
    dem = np.full((5, 5), 4000.0)
    slope, aspect = E.slope_aspect(dem, 80, 80)
    assert np.all(slope == 0)
    u_los = los_az(80, 35)[:, None, None]
    S = E.sensitivity(E.slope_vector(slope, aspect), u_los)
    lay, sha = E.layover_shadow(slope, aspect, u_los)
    state, reason = E.classify(S, np.full(S.shape, 0.9), np.ones(S.shape, bool),
                               np.ones(S.shape, bool), lay, sha, slope)
    assert np.all(state == E.STATE_INVALID)
    assert np.all(reason == 6)


# 4. Orientation in five bearings: a DEM tilted down towards each bearing gives that aspect
@pytest.mark.parametrize("bearing", [0, 45, 90, 180, 270])
def test_aspect_five_bearings(bearing):
    n = 21
    cols, rows = np.meshgrid(np.arange(n), np.arange(n))
    east = cols * 80.0
    north = -rows * 80.0  # row 0 is the northern edge
    a = D(bearing)
    dem = 1000.0 - 0.3 * (east * np.sin(a) + north * np.cos(a))  # descends towards bearing
    slope, aspect = E.slope_aspect(dem, 80.0, 80.0)
    inner = (slice(2, -2), slice(2, -2))
    assert np.allclose(slope[inner], np.arctan(0.3))
    assert np.allclose(np.angle(np.exp(1j * (aspect[inner] - a))), 0, atol=1e-9)
    u = E.slope_vector(slope[inner], aspect[inner])
    assert np.allclose(u[0], np.sin(a) * np.cos(np.arctan(0.3)))
    assert np.allclose(u[1], np.cos(a) * np.cos(np.arctan(0.3)))
    assert np.all(u[2] < 0)


# 5. Layover: slope facing the radar steeper than the incidence angle
def test_layover():
    u_los = los_az(90, 35)  # sensor to the east
    facing = D(90)          # downhill towards the sensor
    lay, sha = E.layover_shadow(D(40), facing, u_los)
    assert lay and not sha
    lay, sha = E.layover_shadow(D(30), facing, u_los)
    assert not lay and not sha


# 6. Shadow: slope facing away steeper than 90 - incidence
def test_shadow():
    u_los = los_az(90, 35)
    away = D(270)
    lay, sha = E.layover_shadow(D(56), away, u_los)
    assert sha and not lay
    lay, sha = E.layover_shadow(D(54), away, u_los)
    assert not sha and not lay


def test_range_slope_oblique_component():
    """An oblique slope only counts its component along range."""
    u_los = los_az(90, 35)
    br = E.range_slope(D(40), D(90 + 60), u_los)  # downhill 60 deg off the sensor direction
    assert np.tan(br) == pytest.approx(np.tan(D(40)) * np.cos(D(60)), rel=1e-12)


# 7. Four-state classification including precedence of state 0
def test_four_states_and_precedence():
    S = np.array([0.8, 0.8, 0.1, 0.1, 0.8, 0.8, 0.8, 0.8, np.nan, 0.8])
    coh = np.array([0.9, 0.2, 0.9, 0.2, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9])
    valid = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 0], bool)
    ccv = np.array([1, 1, 1, 1, 0, 1, 1, 1, 1, 1], bool)
    lay = np.array([0, 0, 0, 0, 0, 1, 0, 0, 0, 1], bool)
    sha = np.array([0, 0, 0, 0, 0, 0, 1, 0, 0, 0], bool)
    slope = np.full(10, D(20))
    slope[7] = D(1)
    state, reason = E.classify(S, coh, valid, ccv, lay, sha, slope)
    assert state.tolist() == [1, 2, 3, 0, 0, 0, 0, 0, 0, 0]
    assert reason.tolist() == [0, 1, 2, 8, 7, 4, 5, 6, 3, 3]


def test_thresholds_are_parameters():
    S, coh, one, zero = np.array([0.25]), np.array([0.45]), np.ones(1, bool), np.zeros(1, bool)
    st, _ = E.classify(S, coh, one, one, zero, zero, np.array([D(20)]), s_min=0.2, coh_min=0.4)
    assert st[0] == 1
    st, _ = E.classify(S, coh, one, one, zero, zero, np.array([D(20)]))
    assert st[0] == 0


def test_sign_positive_towards_sensor():
    u_los = los_az(90, 35)
    assert E.sensitivity(E.slope_vector(D(10), D(90)), u_los) > 0
    assert E.sensitivity(E.slope_vector(D(10), D(270)), u_los) < 0


# 8. Native LOS vs incidence + heading formulation
@pytest.mark.parametrize("heading,look,expected_az", [
    (-12.0, "left", -12.0 - 90 + 180),    # ascending, left-looking: sensor to the east
    (-168.0, "left", -168.0 - 90 + 180),  # descending, left-looking: sensor to the west
    (-12.0, "right", -12.0 + 90 + 180),
])
def test_native_los_equals_angle_formulation(heading, look, expected_az):
    inc = 37.0
    native = los_az(expected_az, inc)
    angles = E.los_from_angles(D(inc), D(heading), look)
    assert np.allclose(native, angles, atol=1e-12)
    assert np.degrees(E.incidence_from_los(angles)) == pytest.approx(inc)
    u = E.slope_vector(D(25), D(130))
    assert E.sensitivity(u, native) == pytest.approx(E.sensitivity(u, angles))


def test_ascending_left_looking_sees_from_east():
    assert E.los_from_angles(D(37), D(-12), "left")[0] > 0.5


def test_interp_cube_reproduces_linear_field():
    z = np.arange(-500.0, 9001, 500)
    y = np.arange(8278250.0, 8270000, -500)
    x = np.arange(381750.0, 390000, 500)
    Z, Y, X = np.meshgrid(z, y, x, indexing="ij")
    cube = 0.001 * Z - 2e-5 * Y + 3e-5 * X
    rng = np.random.default_rng(1)
    pz, py, px = rng.uniform(0, 6000, 50), rng.uniform(8271000, 8278000, 50), rng.uniform(382000, 389000, 50)
    got = E.interp_cube(cube, z, y, x, pz, py, px)
    assert np.allclose(got, 0.001 * pz - 2e-5 * py + 3e-5 * px)


def test_los_unit_norm():
    rng = np.random.default_rng(0)
    t, a = rng.uniform(0.3, 0.8, 100), rng.uniform(0, 2 * np.pi, 100)
    u = E.los_vector(np.sin(t) * np.sin(a), np.sin(t) * np.cos(a))
    assert np.allclose(np.linalg.norm(u, axis=0), 1.0)
