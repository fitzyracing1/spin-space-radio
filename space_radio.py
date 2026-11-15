"""spin-space-radio: pass time, Doppler, hydrogen line, and band lookup."""
from __future__ import annotations

import argparse
import math
import sys
from decimal import Decimal, localcontext
from typing import Iterable

INTRO = (
    "spin-space-radio by Joshua Almeida.\n"
    "Rules and code, no API, offline. Sponsor: https://github.com/sponsors/fitzyracing1"
)

# Speed of light, exact SI value, metres per second.
C = Decimal("299792458")

# 1420.405751 MHz, the hydrogen-line rest frequency used by this tool.
HYDROGEN_LINE_HZ = Decimal("1420405751")

# Mean Earth radius, 6371 km. This is a spherical mean, not a geoid model.
EARTH_RADIUS_M = Decimal("6371000")

# Standard gravitational parameter of Earth, GM, in m^3/s^2 (WGS-84 / conventional).
MU_EARTH = Decimal("3.986004418E14")

# Commonly used band-name ranges for lookup, not a license or allocation authority.
# ITU radio bands, and IEEE Std 521 radar-letter bands.
ITU_BANDS = (
    ("ITU VLF", Decimal("3000"), Decimal("30000")),
    ("ITU LF", Decimal("30000"), Decimal("300000")),
    ("ITU MF", Decimal("300000"), Decimal("3000000")),
    ("ITU HF", Decimal("3000000"), Decimal("30000000")),
    ("ITU VHF", Decimal("30000000"), Decimal("300000000")),
    ("ITU UHF", Decimal("300000000"), Decimal("3000000000")),
    ("ITU SHF", Decimal("3000000000"), Decimal("30000000000")),
    ("ITU EHF", Decimal("30000000000"), Decimal("300000000000")),
)

IEEE_BANDS = (
    ("IEEE HF", Decimal("3000000"), Decimal("30000000")),
    ("IEEE VHF", Decimal("30000000"), Decimal("300000000")),
    ("IEEE UHF", Decimal("300000000"), Decimal("1000000000")),
    ("IEEE L", Decimal("1000000000"), Decimal("2000000000")),
    ("IEEE S", Decimal("2000000000"), Decimal("4000000000")),
    ("IEEE C", Decimal("4000000000"), Decimal("8000000000")),
    ("IEEE X", Decimal("8000000000"), Decimal("12000000000")),
    ("IEEE Ku", Decimal("12000000000"), Decimal("18000000000")),
    ("IEEE K", Decimal("18000000000"), Decimal("27000000000")),
    ("IEEE Ka", Decimal("27000000000"), Decimal("40000000000")),
    ("IEEE V", Decimal("40000000000"), Decimal("75000000000")),
    ("IEEE W", Decimal("75000000000"), Decimal("110000000000")),
)

UNITS = {
    "hz": Decimal("1"),
    "khz": Decimal("1000"),
    "mhz": Decimal("1000000"),
    "ghz": Decimal("1000000000"),
}


def D(value) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def parse_freq(text: str) -> Decimal:
    raw = str(text).strip().replace(" ", "")
    lower = raw.lower()
    for unit, scale in (("ghz", UNITS["ghz"]), ("mhz", UNITS["mhz"]), ("khz", UNITS["khz"]), ("hz", UNITS["hz"])):
        if lower.endswith(unit):
            return D(raw[: -len(unit)]) * scale
    return D(raw)


def format_hz(hz: Decimal) -> str:
    hz = D(hz)
    if hz >= UNITS["ghz"] and hz % UNITS["mhz"] == 0:
        return f"{hz / UNITS['ghz']} GHz"
    if hz >= UNITS["mhz"]:
        mhz = hz / UNITS["mhz"]
        return f"{mhz} MHz ({hz} Hz)"
    if hz >= UNITS["khz"]:
        return f"{hz / UNITS['khz']} kHz ({hz} Hz)"
    return f"{hz} Hz"


def doppler(rest_hz, radial_ms, *, relativistic: bool = False) -> Decimal:
    """Observed frequency for a one-way path.

    Positive radial velocity means the source is receding (range increasing),
    so the observed frequency falls. Classical: f * (c - v) / c.
    Relativistic uses the one-way formula f * sqrt((c - v) / (c + v)).
    """
    rest = D(rest_hz)
    radial = D(radial_ms)
    if abs(radial) >= C:
        raise ValueError("Radial velocity must be slower than the speed of light.")
    if relativistic:
        with localcontext() as ctx:
            ctx.prec = 50
            ratio = (C - radial) / (C + radial)
            return rest * ratio.sqrt()
    return rest * (C - radial) / C


def circular_period_s(altitude_km) -> Decimal:
    altitude_m = D(altitude_km) * Decimal("1000")
    if altitude_m < 0:
        raise ValueError("Altitude cannot be negative.")
    a = EARTH_RADIUS_M + altitude_m
    # T = 2π √(a³ / μ)
    with localcontext() as ctx:
        ctx.prec = 50
        return Decimal("2") * Decimal(str(math.pi)) * (a**3 / MU_EARTH).sqrt()


def orbital_speed_ms(altitude_km) -> Decimal:
    a = EARTH_RADIUS_M + D(altitude_km) * Decimal("1000")
    if a <= 0:
        raise ValueError("Orbit radius must be positive.")
    with localcontext() as ctx:
        ctx.prec = 50
        return (MU_EARTH / a).sqrt()


def _central_half_angle(altitude_km, min_elev_deg) -> Decimal:
    a = EARTH_RADIUS_M + D(altitude_km) * Decimal("1000")
    if a <= EARTH_RADIUS_M:
        raise ValueError("Altitude must be above the surface.")
    elev = D(min_elev_deg)
    if elev < 0 or elev >= 90:
        raise ValueError("Minimum elevation must be in [0, 90).")
    # γ = arccos((R/a) * cos ε) - ε  for a spherical Earth, circular orbit, overhead pass.
    ratio = float((EARTH_RADIUS_M / a) * Decimal(str(math.cos(math.radians(float(elev))))))
    if ratio < -1 or ratio > 1:
        raise ValueError("Geometry is not visible at that elevation.")
    gamma = math.acos(ratio) - math.radians(float(elev))
    if gamma <= 0:
        raise ValueError("Geometry is not visible at that elevation.")
    return Decimal(str(gamma))


def pass_duration_s(altitude_km, min_elev_deg=0) -> Decimal:
    """Horizon-to-horizon (or min-elevation) duration of an overhead circular-orbit pass."""
    period = circular_period_s(altitude_km)
    gamma = _central_half_angle(altitude_km, min_elev_deg)
    return period * gamma / Decimal(str(math.pi))


def max_range_rate_ms(altitude_km) -> Decimal:
    """Peak |range rate| at the geometric horizon for an overhead circular-orbit pass: v * R / a."""
    a = EARTH_RADIUS_M + D(altitude_km) * Decimal("1000")
    return orbital_speed_ms(altitude_km) * EARTH_RADIUS_M / a


def max_doppler(rest_hz, altitude_km) -> Decimal:
    return doppler(rest_hz, -max_range_rate_ms(altitude_km)) - D(rest_hz)


def lookup_bands(hz) -> list[str]:
    hz = D(hz)
    names = []
    for name, low, high in ITU_BANDS + IEEE_BANDS:
        if low <= hz < high:
            names.append(name)
    return names


def hydrogen(radial_ms=0, *, relativistic: bool = False) -> dict:
    rest = HYDROGEN_LINE_HZ
    observed = doppler(rest, radial_ms, relativistic=relativistic)
    return {"rest_hz": rest, "observed_hz": observed, "shift_hz": observed - rest}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="space_radio.py",
        description="Satellite pass time, Doppler shift, hydrogen-line frequency, and band lookup.",
    )
    sub = parser.add_subparsers(dest="cmd")

    hyd = sub.add_parser("hydrogen", help="Hydrogen-line rest frequency, optionally Doppler shifted.")
    hyd.add_argument("--radial-ms", dest="radial", default="0", help="Range rate, m/s. Positive = receding.")
    hyd.add_argument("--relativistic", action="store_true")

    dop = sub.add_parser("doppler", help="One-way Doppler shift. Positive radial velocity is receding.")
    dop.add_argument("freq", help="Rest frequency, such as 145MHz or 145000000.")
    dop.add_argument("--radial-ms", dest="radial", required=True, help="Range rate, m/s. Positive = receding.")
    dop.add_argument("--relativistic", action="store_true")

    pas = sub.add_parser("pass", help="Overhead circular-orbit pass duration and max Doppler.")
    pas.add_argument("altitude_km", help="Orbital altitude above a 6371 km mean Earth radius.")
    pas.add_argument("--min-elev", dest="min_elev", default="0", help="Minimum elevation in degrees.")
    pas.add_argument("--freq", help="Optional rest frequency for max horizon Doppler.")

    band = sub.add_parser("band", help="Look up commonly used ITU and IEEE band names.")
    band.add_argument("freq", help="Frequency, such as 1420.405751MHz.")

    per = sub.add_parser("period", help="Circular-orbit period from altitude.")
    per.add_argument("altitude_km")

    try:
        args = parser.parse_args([] if argv is None and len(sys.argv) == 1 else (sys.argv[1:] if argv is None else argv))
    except SystemExit as exc:
        code = exc.code
        return 0 if code in (0, None) else int(code)

    if not args.cmd:
        print(INTRO)
        print()
        print("Usage: python space_radio.py hydrogen [--radial-ms V]")
        print("       python space_radio.py doppler 145MHz --radial-ms 7215")
        print("       python space_radio.py pass 400 --freq 145MHz")
        print("       python space_radio.py period 400")
        print("       python space_radio.py band 1420.405751MHz")
        return 0
    try:
        print(INTRO)
        print()
        if args.cmd == "hydrogen":
            result = hydrogen(args.radial, relativistic=args.relativistic)
            print("Hydrogen line  (rest frequency 1420.405751 MHz)")
            print(f"  rest        {format_hz(result['rest_hz'])}")
            print(f"  radial      {D(args.radial)} m/s  (positive = receding)")
            print(f"  observed    {format_hz(result['observed_hz'])}")
            print(f"  shift       {result['shift_hz']} Hz")
            return 0
        if args.cmd == "doppler":
            rest = parse_freq(args.freq)
            observed = doppler(rest, args.radial, relativistic=args.relativistic)
            print("Doppler  (one-way; positive radial velocity = receding)")
            print(f"  rest        {format_hz(rest)}")
            print(f"  radial      {D(args.radial)} m/s")
            print(f"  observed    {format_hz(observed)}")
            print(f"  shift       {observed - rest} Hz")
            return 0
        if args.cmd == "band":
            hz = parse_freq(args.freq)
            names = lookup_bands(hz)
            print("Band lookup  (commonly used ITU and IEEE names, not a license or allocation)")
            print(f"  frequency   {format_hz(hz)}")
            if names:
                for name in names:
                    print(f"  {name}")
            else:
                print("  no named ITU/IEEE range in the bundled table contains this frequency")
            return 0
        if args.cmd == "period":
            period = circular_period_s(args.altitude_km)
            print("Circular orbit period  (spherical mean Earth radius 6371 km)")
            print(f"  altitude    {D(args.altitude_km)} km")
            print(f"  period      {period} s  ({period / Decimal('60')} min)")
            return 0
        period = circular_period_s(args.altitude_km)
        duration = pass_duration_s(args.altitude_km, args.min_elev)
        vr = max_range_rate_ms(args.altitude_km)
        print("Overhead pass  (circular orbit, spherical Earth, geometric horizon)")
        print(f"  altitude    {D(args.altitude_km)} km")
        print(f"  min elev    {D(args.min_elev)} deg")
        print(f"  period      {period} s  ({period / Decimal('60')} min)")
        print(f"  pass time   {duration} s  ({duration / Decimal('60')} min)")
        print(f"  max |range rate| at horizon  {vr} m/s")
        if args.freq:
            rest = parse_freq(args.freq)
            shift = max_doppler(rest, args.altitude_km)
            print(f"  max |Doppler| at {format_hz(rest)}  {abs(shift)} Hz")
        return 0
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
