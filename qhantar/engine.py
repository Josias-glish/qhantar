"""QHANTAR engine: pure NumPy functions, no file I/O.

Conventions (see docs/conventions.md):
- Vectors are East-North-Up (ENU) unit vectors.
- Aspect alpha = azimuth of the DOWNHILL direction, radians, clockwise from north.
- Slope beta = terrain inclination, radians, 0 = flat.
- u_LOS points from the ground target to the sensor (NISAR losUnitVectorX/Y convention).
- S = u_slope . u_LOS ; S > 0 means downhill motion projects towards the sensor.
"""
import numpy as np

# Four-state map codes
STATE_INVALID, STATE_INTERPRETABLE, STATE_INCOHERENT, STATE_LOW_SENS = 0, 1, 2, 3

# Reason codes: why each pixel got its state. First matching rule wins (top to bottom).
REASONS = {
    0: "interpretable",
    1: "visible_incoherent",
    2: "coherent_low_sensitivity",
    3: "nodata",
    4: "layover",
    5: "shadow",
    6: "flat",
    7: "invalid_component",
    8: "low_sensitivity_and_low_coherence",
}

DEFAULTS = {"s_min": 0.3, "coh_min": 0.5, "slope_min_deg": 2.0}


def slope_aspect(dem, dx, dy):
    """Slope and downhill aspect (radians) from a DEM on a metric grid.

    dem rows run north->south (row 0 is the northern edge, as in north-up rasters);
    dx, dy are the positive pixel sizes in metres (east and north).
    """
    dz_drow, dz_dcol = np.gradient(dem.astype("float64"))
    dz_de = dz_dcol / dx
    dz_dn = -dz_drow / dy  # row index grows southwards
    slope = np.arctan(np.hypot(dz_de, dz_dn))
    aspect = np.mod(np.arctan2(-dz_de, -dz_dn), 2 * np.pi)  # downhill = minus gradient
    return slope, aspect


def slope_vector(slope, aspect):
    """Unit vector of hypothetical downhill motion, ENU."""
    cb = np.cos(slope)
    return np.stack([np.sin(aspect) * cb, np.cos(aspect) * cb, -np.sin(slope)])


def los_vector(lx, ly):
    """Target-to-sensor unit LOS vector from the native East/North components."""
    lz = np.sqrt(np.clip(1.0 - lx**2 - ly**2, 0.0, None))
    return np.stack([lx, ly, lz])


def los_from_angles(incidence, heading, look_side):
    """Target-to-sensor LOS from incidence angle and platform heading (radians).

    heading: azimuth of flight direction, clockwise from north.
    look_side: 'right' or 'left'. The sensor-to-target look azimuth is heading +/- 90 deg,
    so the target-to-sensor horizontal azimuth is the opposite.
    """
    look_az = heading + (np.pi / 2 if look_side == "right" else -np.pi / 2)
    to_sensor_az = look_az + np.pi
    s = np.sin(incidence)
    return np.stack([s * np.sin(to_sensor_az), s * np.cos(to_sensor_az), np.cos(incidence)])


def sensitivity(u_slope, u_los):
    """Signed projection S of the downhill unit vector on the LOS."""
    return np.sum(u_slope * u_los, axis=0)


def incidence_from_los(u_los):
    return np.arccos(np.clip(u_los[2], -1.0, 1.0))


def range_slope(slope, aspect, u_los):
    """Terrain slope angle measured in the range plane; positive = facing the radar.

    The horizontal unit vector towards the sensor is h = (lx, ly)/|(lx, ly)|.
    A slope faces the radar when its downhill direction points towards the sensor,
    i.e. terrain rises when moving away from the sensor. tan(beta_r) = tan(beta) * (d . h),
    with d = (sin alpha, cos alpha) the horizontal downhill direction.
    """
    hn = np.hypot(u_los[0], u_los[1])
    hn = np.where(hn == 0, np.nan, hn)
    d_dot_h = (np.sin(aspect) * u_los[0] + np.cos(aspect) * u_los[1]) / hn
    return np.arctan(np.tan(slope) * d_dot_h)


def layover_shadow(slope, aspect, u_los):
    """Layover: slope faces the radar more steeply than the incidence angle.
    Shadow: slope faces away more steeply than the complement of the incidence angle."""
    theta = incidence_from_los(u_los)
    br = range_slope(slope, aspect, u_los)
    layover = br > theta
    shadow = -br > (np.pi / 2 - theta)
    return layover, shadow


def classify(S, coh, valid, cc_valid, layover, shadow, slope,
             s_min=DEFAULTS["s_min"], coh_min=DEFAULTS["coh_min"],
             slope_min_deg=DEFAULTS["slope_min_deg"]):
    """Return (state, reason) uint8 arrays. Coherence and sensitivity are never combined."""
    sens_ok = np.abs(S) >= s_min
    coh_ok = coh >= coh_min
    flat = slope < np.deg2rad(slope_min_deg)
    rules = [  # (condition, reason) in precedence order
        (~valid | ~np.isfinite(S) | ~np.isfinite(coh), 3),
        (layover, 4),
        (shadow, 5),
        (flat, 6),
        (~cc_valid, 7),
        (~sens_ok & ~coh_ok, 8),
        (sens_ok & coh_ok, 0),
        (sens_ok & ~coh_ok, 1),
        (~sens_ok & coh_ok, 2),
    ]
    reason = np.select([c for c, _ in rules], [r for _, r in rules], default=3).astype("uint8")
    to_state = np.array([1, 2, 3, 0, 0, 0, 0, 0, 0], dtype="uint8")
    return to_state[reason], reason
