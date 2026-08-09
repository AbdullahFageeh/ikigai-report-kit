#!/usr/bin/env python3
"""
Chart calculator for the Ikigai Report Kit.

Computes, from a birth date/time/place:
  - natal tropical positions, Ascendant and Midheaven
  - the exact minute the Ascendant changes sign (birth-time sensitivity)
  - the lunar nodes, with houses
  - sidereal (Lahiri) positions with nakshatra and pada
  - the Vedic D10 (Dashamsha) career chart
  - a solar return for a chosen year
  - astrocartography MC/IC lines

Requires: pip install pyswisseph

Example:
  python chart.py --date 1990-01-15 --time 14:30 --tz +0 \
                  --lat 51.4779 --lon -0.0015 --solar-year 2026
"""
from __future__ import annotations

import argparse
import sys

try:
    import swisseph as swe
except ImportError:  # pragma: no cover
    sys.exit("error: pyswisseph not installed. Run: pip install pyswisseph")

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "P.Phalguni", "U.Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula",
    "P.Ashadha", "U.Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "P.Bhadrapada", "U.Bhadrapada", "Revati",
]

PLANETS = [
    ("Sun", swe.SUN), ("Moon", swe.MOON), ("Mercury", swe.MERCURY),
    ("Venus", swe.VENUS), ("Mars", swe.MARS), ("Jupiter", swe.JUPITER),
    ("Saturn", swe.SATURN), ("Uranus", swe.URANUS), ("Neptune", swe.NEPTUNE),
    ("Pluto", swe.PLUTO),
]


def fmt(longitude: float) -> str:
    """Format an ecliptic longitude as 'Sign DD°MM''."""
    deg = longitude % 30
    minutes = int(round((deg % 1) * 60))
    whole = int(deg)
    if minutes == 60:          # guard against rounding to 60'
        minutes, whole = 0, whole + 1
    return f"{SIGNS[int(longitude // 30)]} {whole}\u00b0{minutes:02d}'"


def house_of(longitude: float, cusps) -> int:
    for i in range(12):
        start, end = cusps[i], cusps[(i + 1) % 12]
        if start <= longitude < end or (start > end and (longitude >= start or longitude < end)):
            return i + 1
    return 0


def d10_sign(longitude: float) -> int:
    """Dashamsha: 3° divisions. Odd signs count from themselves, even from the 9th."""
    sign_index = int(longitude // 30)
    division = int((longitude % 30) // 3)
    start = sign_index if sign_index % 2 == 0 else (sign_index + 8) % 12
    return (start + division) % 12


def julian_day(date: str, time: str, tz: float) -> float:
    year, month, day = (int(x) for x in date.split("-"))
    hour, minute = (int(x) for x in time.split(":"))
    return swe.julday(year, month, day, hour + minute / 60.0 - tz)


def section(title: str) -> None:
    print(f"\n=== {title} ===")


def natal(jd: float, lat: float, lon: float) -> None:
    section("NATAL (tropical)")
    for name, code in PLANETS:
        pos, _ = swe.calc_ut(jd, code)
        flag = " R" if pos[3] < 0 else ""
        print(f"  {name:<9} {fmt(pos[0]):<22}{flag}")

    try:
        pos, _ = swe.calc_ut(jd, swe.CHIRON)
        print(f"  {'Chiron':<9} {fmt(pos[0])}")
    except swe.Error:
        print("  Chiron    (needs the seas_18.se1 asteroid ephemeris file)")

    cusps, ascmc = swe.houses(jd, lat, lon, b"P")
    print(f"  {'ASC':<9} {fmt(ascmc[0])}")
    print(f"  {'MC':<9} {fmt(ascmc[1])}")

    north = swe.calc_ut(jd, swe.TRUE_NODE)[0][0]
    south = (north + 180) % 360
    print(f"  {'N Node':<9} {fmt(north):<22} house {house_of(north, cusps)}")
    print(f"  {'S Node':<9} {fmt(south):<22} house {house_of(south, cusps)}")


def ascendant_sensitivity(jd: float, lat: float, lon: float, tz: float) -> None:
    """Find when the Ascendant next changes sign, so birth-time error is visible."""
    section("BIRTH-TIME SENSITIVITY")
    start_sign = int(swe.houses(jd, lat, lon, b"P")[1][0] // 30)
    lo, hi = jd, jd + (4.0 / 24.0)      # search the next four hours
    if int(swe.houses(hi, lat, lon, b"P")[1][0] // 30) == start_sign:
        print("  Ascendant sign stable for at least the next 4 hours")
        return
    for _ in range(60):
        mid = (lo + hi) / 2
        if int(swe.houses(mid, lat, lon, b"P")[1][0] // 30) == start_sign:
            lo = mid
        else:
            hi = mid
    y, m, d, ut_hours = swe.revjul((lo + hi) / 2)
    local = (ut_hours + tz) % 24
    new_sign = SIGNS[int(swe.houses(hi, lat, lon, b"P")[1][0] // 30)]
    print(f"  Ascendant leaves {SIGNS[start_sign]} and enters {new_sign}")
    print(f"  at {int(local):02d}:{(local % 1) * 60:05.2f} local time")


def sidereal(jd: float, lat: float, lon: float) -> None:
    section("SIDEREAL (Vedic, Lahiri)")
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    bodies = PLANETS[:7] + [("Rahu", swe.TRUE_NODE)]
    for name, code in bodies:
        pos, _ = swe.calc_ut(jd, code, flags)
        nak = NAKSHATRAS[int(pos[0] // (360 / 27))]
        pada = int((pos[0] % (360 / 27)) / (360 / 108)) + 1
        print(f"  {name:<9} {fmt(pos[0]):<22} {nak} pada {pada}")
    _, ascmc = swe.houses_ex(jd, lat, lon, b"P", swe.FLG_SIDEREAL)
    print(f"  {'ASC':<9} {fmt(ascmc[0])}")
    print(f"  {'MC':<9} {fmt(ascmc[1])}")


def dashamsha(jd: float, lat: float, lon: float) -> None:
    section("D10 (DASHAMSHA) — career chart")
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    _, ascmc = swe.houses_ex(jd, lat, lon, b"P", swe.FLG_SIDEREAL)
    lagna = d10_sign(ascmc[0])
    print(f"  D10 lagna: {SIGNS[lagna]}")
    print(f"  D10 10th house sign: {SIGNS[(lagna + 9) % 12]}")
    bodies = PLANETS[:7] + [("Rahu", swe.TRUE_NODE)]
    for name, code in bodies:
        pos, _ = swe.calc_ut(jd, code, flags)
        sign = d10_sign(pos[0])
        house = ((sign - lagna) % 12) + 1
        print(f"  {name:<9} -> {SIGNS[sign]:<12} house {house}")


def solar_return(jd: float, lat: float, lon: float, tz: float, year: int) -> None:
    section(f"SOLAR RETURN {year}")
    natal_sun = swe.calc_ut(jd, swe.SUN)[0][0]
    _, month, day, _ = swe.revjul(jd)
    lo = swe.julday(year, int(month), int(day), 0) - 2
    hi = lo + 4
    for _ in range(60):
        mid = (lo + hi) / 2
        if (swe.calc_ut(mid, swe.SUN)[0][0] - natal_sun) % 360 < 180:
            hi = mid
        else:
            lo = mid
    sr = (lo + hi) / 2
    y, m, d, ut_hours = swe.revjul(sr)
    local = (ut_hours + tz) % 24
    print(f"  Exact return: {int(y)}-{int(m):02d}-{int(d):02d} "
          f"{int(local):02d}:{int((local % 1) * 60):02d} local")
    cusps, ascmc = swe.houses(sr, lat, lon, b"P")
    print(f"  {'ASC':<9} {fmt(ascmc[0])}")
    print(f"  {'MC':<9} {fmt(ascmc[1])}")
    print(f"  Natal Sun falls in SR house {house_of(natal_sun, cusps)}")
    for name, code in PLANETS[:7]:
        pos, _ = swe.calc_ut(sr, code)
        print(f"  {name:<9} {fmt(pos[0]):<22} house {house_of(pos[0], cusps)}")


def astrocartography(jd: float) -> None:
    section("ASTROCARTOGRAPHY — MC / IC lines")
    gmst_deg = swe.sidtime(jd) * 15.0
    for name, code in PLANETS[:7]:
        ra = swe.calc_ut(jd, code, swe.FLG_SWIEPH | swe.FLG_EQUATORIAL)[0][0]
        mc = ((ra - gmst_deg + 180) % 360) - 180
        ic = ((mc + 360) % 360) - 180
        print(f"  {name:<9} MC line {mc:+8.2f}\u00b0    IC line {ic:+8.2f}\u00b0")
    print("  (positive = east longitude)")
    print("  Note: MC/IC lines are longitude-only and valid at all latitudes.")
    print("  Ascendant/Descendant lines are latitude-dependent curves and need a mapping tool.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Compute chart data for an Ikigai report.")
    ap.add_argument("--date", required=True, help="birth date, YYYY-MM-DD")
    ap.add_argument("--time", required=True, help="local birth time, HH:MM (24h)")
    ap.add_argument("--tz", required=True, type=float,
                    help="UTC offset in hours at birth, e.g. +3 or -5.5")
    ap.add_argument("--lat", required=True, type=float, help="latitude, north positive")
    ap.add_argument("--lon", required=True, type=float, help="longitude, east positive")
    ap.add_argument("--solar-year", type=int, help="also compute the solar return for this year")
    args = ap.parse_args()

    jd = julian_day(args.date, args.time, args.tz)
    print(f"Birth: {args.date} {args.time} (UTC{args.tz:+g})  "
          f"lat {args.lat}  lon {args.lon}")

    natal(jd, args.lat, args.lon)
    ascendant_sensitivity(jd, args.lat, args.lon, args.tz)
    sidereal(jd, args.lat, args.lon)
    dashamsha(jd, args.lat, args.lon)
    if args.solar_year:
        solar_return(jd, args.lat, args.lon, args.tz, args.solar_year)
    astrocartography(jd)
    print()


if __name__ == "__main__":
    main()
