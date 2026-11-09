"""Parse scout reports and battle reports out of a Dominions 6 .trn file.

The .trn is the turn file a player receives after a host.  It is *not* the
world state (that lives only on the host as ``ftherlnd``), but it does carry
every message the player is allowed to see: province names, scout reports,
battle reports, events, etc.

All text strings are stored XOR-encoded with key 0x4F and terminated by a
raw 0x4F byte (which decodes to NUL).  Message headers sit between the
previous terminator and the string.
"""

from __future__ import annotations

import re
import struct
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from . import gamedata

XOR = 0x4F
VALID_UNITS: set[int] = set(gamedata.units().keys())


# --------------------------------------------------------------------------
# low level: split the file into (header, text) messages
# --------------------------------------------------------------------------
def _terminators(raw: bytes) -> list[int]:
    out: list[int] = []
    pos = 0
    while True:
        t = raw.find(b"\x4f", pos)
        if t < 0:
            break
        out.append(t)
        pos = t + 1
    return out


def _dec(buf: bytes, start: int, end: int) -> str:
    return bytes(b ^ XOR for b in buf[start:end]).decode("utf-8", "replace")


def _messages(raw: bytes) -> list[tuple[int, int, int, str]]:
    """Return (header_start, header_end, text_start, text) for every message.

    A header is everything between the previous 0x4F terminator and the text.
    Because 0x4F can legitimately appear inside a header, we keep the longest
    candidate whose text is printable ASCII (the real text is always a run of
    printable characters, whereas a 0x4F in the middle of a header produces
    a garbage fragment).
    """
    terms = _terminators(raw)
    msgs: list[tuple[int, int, int, str]] = []
    for i in range(1, len(terms) - 1):
        text_start = terms[i] + 1
        text_end = terms[i + 1]
        text = _dec(raw, text_start, text_end)
        if not text:
            continue
        if not all(32 <= ord(c) < 127 for c in text):
            continue
        header_start = terms[i - 1] + 1
        msgs.append((header_start, terms[i], text_start, text))
    return msgs


# --------------------------------------------------------------------------
# province id <-> name
# --------------------------------------------------------------------------
def find_province_name(raw: bytes, province_id: int) -> str | None:
    """Return the in-game name of ``province_id`` (e.g. 191 -> "Ryd")."""
    pid = struct.pack("<H", province_id)
    for h_start, h_end, t_start, text in _messages(raw):
        if len(text) < 2:
            continue
        region = raw[max(0, t_start - 80):t_start]
        if pid in region:
            return text
    return None


# --------------------------------------------------------------------------
# scout report: a per-province "known units" record in the binary section
#
#     [u32 index][u32 province][u32 F0][u32 F1]
#     [u32 type_a][u32 zero][u32 count_a][u32 count_b][u32 type_b]
#     [u16 total][ff ff]
#     [5 byte header][report text][00]     (running-XOR cipher)
#
# Verified against host-side ftherlnd ground truth (games dg/fm): the record
# carries ONLY the province garrison's top two non-mount unit types with
# their exact counts (type_a x count_a, type_b x count_b; type_b may be 0).
# F0 is usually 50, F1 is the "about N units" number, ``total`` is constant
# per file (a player-level value, NOT the garrison size).
# Everything beyond the top two types (third+ types, commanders, small
# squads) appears only in the report text.
#
# The record is located structurally, not by a magic constant.  What looked
# like one (INTEL_MAGIC) is really the ciphertext of the first 29 bytes of a
# standard report's text: after the 5 byte header every ordinary scout report
# says "province contains about ", so those 29 bytes coincide and only the
# number behind them differs.  A report from another source opens with a
# different sentence -- a Seithberender scrying says "Seithberenders have
# scryed upon our enemies." and diverges at byte 5 -- so a magic search is
# blind to it (measured on StarCrossedLover, province 61: 84 Comitatenses and
# 10 Flagellants were stored, but the province came back as "no scout
# report").  Such a report also carries F0 = -1 instead of 50/30.
# --------------------------------------------------------------------------
INTEL_MAGIC = bytes.fromhex(
    "052ca451b9c95bf47ce98734df3f5ccd7f0b923dd358bedf7dee8511f9")
INTEL_META = 40           # meta block size: the report text starts here
INTEL_TEXT_HEADER = 5     # u16 id + marker + one byte before the text


def _intel_meta(raw: bytes, province_id: int) -> int | None:
    """Offset of ``province_id``'s intel meta block, or None."""
    return _intel_index(raw).get(province_id)


_INTEL_CACHE: dict[int, tuple[bytes, dict[int, int]]] = {}


def _intel_index(raw: bytes) -> dict[int, int]:
    """``{province: meta offset}`` for the reports ``raw`` holds.

    Scanning 780 KB of .trn once per province is too slow, so the index is
    cached per buffer (the cache holds the buffer, so its id cannot be
    reused).
    """
    cached = _INTEL_CACHE.get(id(raw))
    if cached is not None and cached[0] is raw:
        return cached[1]
    index = _scan_intel(raw)
    if len(_INTEL_CACHE) > 4:
        _INTEL_CACHE.clear()
    _INTEL_CACHE[id(raw)] = (raw, index)
    return index


def _scan_intel(raw: bytes) -> dict[int, int]:
    """Every intel record in ``raw``, found by layout.

    Two passes: the fast one follows INTEL_MAGIC (standard scout reports),
    the structural one follows the ``ff ff`` that closes every record header.
    The magic hit wins when both find the same province, and it is taken
    without further checks -- that is exactly what this lookup always did, so
    the structural pass can only ADD reports, never lose one.
    """
    index: dict[int, int] = {}
    pos = 0
    while True:
        i = raw.find(INTEL_MAGIC, pos)
        if i < 0:
            break
        meta = i - INTEL_META
        if meta >= 0:
            _add_intel(index, raw, meta, strict=False)
        pos = i + 1
    pos = 0
    while True:
        i = raw.find(b"\xff\xff", pos)
        if i < 0:
            break
        _add_intel(index, raw, i - 38, strict=True)
        pos = i + 1
    return index


def _add_intel(index: dict[int, int], raw: bytes, meta: int,
               strict: bool) -> None:
    if meta < 0 or meta + INTEL_META > len(raw):
        return
    if meta in index.values():
        return
    if strict and not _intel_at(raw, meta):
        return
    index.setdefault(struct.unpack_from("<I", raw, meta + 4)[0], meta)


def _intel_at(raw: bytes, meta: int) -> bool:
    """True when ``meta`` looks like an intel record of ``raw``."""
    if meta < 0 or meta + INTEL_META + INTEL_TEXT_HEADER + 20 > len(raw):
        return False
    if raw[meta + 38:meta + 40] != b"\xff\xff":
        return False
    if not 1 <= struct.unpack_from("<I", raw, meta + 4)[0] <= _province_max:
        return False
    type_a, zero, count_a, count_b, type_b = struct.unpack_from(
        "<IIIII", raw, meta + 16)
    if type_a not in VALID_UNITS or zero > 1:
        return False
    if count_a > 20000 or count_b > 20000:
        return False
    if type_b and type_b not in VALID_UNITS:
        return False
    return _intel_text_ok(raw, meta + INTEL_META)


def _intel_text_ok(raw: bytes, start: int) -> bool:
    """True when the bytes at ``start`` decrypt to readable report text."""
    key = RUNNING_XOR_KEY
    out = bytearray()
    p = start
    while p < min(len(raw), start + 256):
        c = raw[p] ^ key
        key = (key + c) & 0xFF
        p += 1
        if c == 0:
            break
        out.append(c)
    text = bytes(out[INTEL_TEXT_HEADER:])
    if len(text) < 20:
        return False
    printable = sum(1 for c in text if 32 <= c < 127 or c in (10, 13))
    return printable >= len(text) - 1


def scout_intel(raw: bytes, province_id: int) -> dict[int, int] | None:
    """Exact {unit_type: count} of the top scouted types, or None."""
    meta = _intel_meta(raw, province_id)
    if meta is None:
        return None
    t_a = struct.unpack_from("<I", raw, meta + 16)[0]
    c_a = struct.unpack_from("<I", raw, meta + 24)[0]
    c_b = struct.unpack_from("<I", raw, meta + 28)[0]
    t_b = struct.unpack_from("<I", raw, meta + 32)[0]
    out: dict[int, int] = {}
    if t_a in VALID_UNITS and c_a:
        out[t_a] = c_a
    if t_b in VALID_UNITS and c_b:
        out[t_b] = c_b
    return out


def scout_units(raw: bytes, province_id: int) -> list[int]:
    """Unit types certain to be in ``province_id``, one entry per enemy unit.

    Only the garrison's top two types carry exact counts in the file; the
    report's remaining types are named in the encrypted report text (see
    below) but their counts are never stored.
    """
    intel = scout_intel(raw, province_id)
    if not intel:
        return []
    out: list[int] = []
    for unit_type, count in intel.items():
        out += [unit_type] * count
    return out


# --------------------------------------------------------------------------
# scout report text: the report body IS stored in the .trn, in the intel
# record itself as
#     [5 byte header][text][00]
# encrypted with the god-file password cipher: a running XOR whose key starts
# at 0xED and is updated by adding each plaintext byte, so it must be
# decrypted from the record's first byte (meta + 40), not from the text.
# The GUI composes the first line itself ("The province contains about N
# enemy units.", N from the meta) and then shows the stored text, which the
# engine builds from these format strings (read out of Dominions6.exe):
#     "The army consists of mainly " + "A, B, C and D."
#     "A huge %s was seen towering over the army. "          (one unit)
#     "%d huge %s were seen towering over the army. "        (N units)
#     "Sometimes a %s could be seen flying over the army camp. "   (one unit)
#     "Several %s could also be seen flying over the army camp. "  (unknown N)
# %s is filled with the singular or the plural of the Inspector unit name.
# Counts beyond the top two types are NOT stored anywhere (that fuzziness is
# the point of a scout report); only the "huge" sentence carries one.
# --------------------------------------------------------------------------
RUNNING_XOR_KEY = 0xED


def scout_report_text(raw: bytes, province_id: int) -> str | None:
    """The decrypted scout report text of ``province_id``, or None."""
    meta = _intel_meta(raw, province_id)
    if meta is None:
        return None
    key = RUNNING_XOR_KEY
    out = bytearray()
    p = meta + INTEL_META
    while p < len(raw):
        c = raw[p] ^ key
        key = (key + c) & 0xFF
        p += 1
        if c == 0:
            break
        out.append(c)
    # The first bytes are the record header (u16 id + marker + one byte),
    # which the GUI never shows.
    return bytes(out[INTEL_TEXT_HEADER:]).decode("latin1").strip()


def scout_total(raw: bytes, province_id: int) -> int | None:
    """The N in "The province contains about N enemy units.".

    The GUI reads it from the intel meta (third dword); it is the garrison
    size the report is based on, exact when the report says so and an
    approximation when it says "about".
    """
    meta = _intel_meta(raw, province_id)
    if meta is None:
        return None
    return struct.unpack_from("<I", raw, meta + 12)[0] or None


# --------------------------------------------------------------------------
# unit names: the report prints the Inspector's spelling, singular after
# "A huge" / "Sometimes a" and plural after "%d huge" / "Several" / the
# "mainly" list.  data/units.csv holds that spelling, so the match is exact:
# every plural form is generated from the name itself instead of guessing
# prefixes.  Generating all forms is safe because no two different unit names
# share a plural (checked against data/units.csv).
# --------------------------------------------------------------------------
def _plural_forms(name: str) -> set[str]:
    """Plural spellings the game can print for ``name``.

    Covers the regular "+s"/"+es", consonant+"y" -> "ies" (Harpy/Harpies),
    "man" -> "men" (Crossbowman/Crossbowmen), "f"/"fe" -> "ves"
    (Wolf/Wolves) and the Latin plurals of "is"/"us" names.
    """
    forms = {name + "s", name + "es"}
    if len(name) > 1:
        if name.endswith("y") and name[-2].lower() not in "aeiou":
            forms.add(name[:-1] + "ies")
        if name.endswith("man"):
            forms.add(name[:-3] + "men")
        if name.endswith("f"):
            forms.add(name[:-1] + "ves")
        if name.endswith("fe"):
            forms.add(name[:-2] + "ves")
        if name.endswith("is"):
            forms.add(name[:-2] + "es")
        if name.endswith("us"):
            forms.add(name[:-2] + "i")
    return forms


@lru_cache(maxsize=1)
def _names() -> dict[str, tuple[int, ...]]:
    """Every singular and plural unit name -> the unit ids carrying it."""
    index: dict[str, list[int]] = {}
    for uid, unit in gamedata.units().items():
        for token in {unit.name} | _plural_forms(unit.name):
            index.setdefault(token, []).append(uid)
    return {token: tuple(sorted(ids)) for token, ids in index.items()}


def unit_id_by_name(name: str) -> int | None:
    """Unit id for a scout report type name, or None.

    The Inspector export repeats some names ("Crossbowman" exists for nine
    nations) and the report never says which army -- let alone which nation --
    it saw, so duplicates resolve by id alone: the lowest id that is not a god
    chassis (a chassis can never be a garrison type).  The arena enemy nation
    is random, so disambiguating by nation would pick a variant at random.
    """
    ids = _names().get(name.strip())
    if not ids:
        return None
    chassis = gamedata.pretender_chassis()
    return next((uid for uid in ids if uid not in chassis), ids[0])


def _split_and(segment: str) -> list[str]:
    """Split "... and ..." only where both halves are real unit names.

    A unit name can itself contain " and " ("Queen of Land and Water"), so a
    blind split would break it.
    """
    if unit_id_by_name(segment) is not None:
        return [segment]
    for m in re.finditer(r" and ", segment):
        left = segment[:m.start()].strip()
        right = segment[m.end():].strip()
        if (unit_id_by_name(left) is not None
                and unit_id_by_name(right) is not None):
            return [left, right]
    return [segment]


def scout_type_names(text: str) -> list[str]:
    """Garrison type names from the "consists of mainly" sentence.

    The engine joins the types with ", " except the last pair, which it joins
    with " and " (most numerous first).  The splits are checked against the
    unit table so a name containing " and " survives.
    """
    m = re.search(r"consists of mainly (.+?)(?:\.(?:\s|$)|\Z)", text)
    if not m:
        # A province holding nothing but its god gets
        # "The enemy force appears to consist of only Tathai the Monolith."
        # -- a personal name plus the type, not a type list.
        m = re.search(r"force appears to consist of only ([^.]+)\.", text)
        if not m:
            return []
        cuts = [c.start() for c in re.finditer(r" the ", m.group(1))]
        for cut in reversed(cuts):
            type_name = m.group(1)[cut + 5:].strip()
            if unit_id_by_name(type_name) is not None:
                return [type_name]
        return []
    body = m.group(1).strip()
    if unit_id_by_name(body) is not None:
        return [body]
    parts = [part.strip() for part in body.split(",") if part.strip()]
    if not parts:
        return []
    return parts[:-1] + _split_and(parts[-1])


def scout_huge_units(text: str) -> list[tuple[str, int]]:
    """Type names and exact counts from the "huge" sentence.

    The engine has exactly two spellings and fills one name only:
        "A huge Kraken was seen towering over the army."        (1)
        "3 huge Hydras were seen towering over the army."       (3)
    """
    out: list[tuple[str, int]] = []
    for m in re.finditer(
            r"(?:(\d+)\s+huge|an?\s+huge)\s+(.+?)\s+"
            r"(?:was|were)\s+seen\s+towering", text, re.IGNORECASE):
        count = int(m.group(1)) if m.group(1) else 1
        out.append((m.group(2).strip(), count))
    return out


def scout_flying_units(text: str) -> list[tuple[str, int | None]]:
    """Units named by the flying sentence; count only when the engine says it.

        "Sometimes a Harab Seraphine could be seen flying over the army camp."
        "Several Harab Seraphs could also be seen flying over the army camp."

    "Sometimes a" is exactly one unit; "Several" stores no count at all
    (``None``), like the types of the "consists of mainly" list.
    """
    out: list[tuple[str, int | None]] = []
    for m in re.finditer(
            r"(?:sometimes\s+an?\s+(.+?)|several\s+(.+?))\s+"
            r"could\s+(?:also\s+)?be\s+seen\s+flying", text, re.IGNORECASE):
        name = (m.group(1) or m.group(2) or "").strip()
        if name:
            out.append((name, 1 if m.group(1) else None))
    return out


def scout_commander_names(text: str) -> list[tuple[int, str]]:
    """``(unit_type, personal name)`` for every "commanded by" sentence.

    The engine prints
        "The army appears to be commanded by Tathai the Monolith who radiates
         power."
    (the " who radiates power" half only for a god) and the same sentence
    without that half for an ordinary commander.  The personal name is
    everything left of the type name and can itself contain " the ", so the
    split that leaves a real unit name on the right wins.  Only the type is
    used for the copy; the name is reported to the log, because the arena's
    pretender keeps its own design name.
    """
    out: list[tuple[int, str]] = []
    for m in re.finditer(r"commanded by ([^.]+)\.", text):
        body = re.sub(r"\s+who\s+radiates\s+power$", "", m.group(1).strip(),
                      flags=re.IGNORECASE)
        cuts = [c.start() for c in re.finditer(r" the ", body)]
        for cut in reversed(cuts):
            uid = unit_id_by_name(body[cut + 5:])
            if uid is not None:
                if all(uid != other for other, _ in out):
                    out.append((uid, body[:cut].strip()))
                break
    return out


@dataclass(frozen=True)
class ScoutReport:
    """What a province's scout report says about its garrison."""

    units: list[tuple[int, int | None]]
    total: int | None = None
    unmatched: tuple[str, ...] = ()
    commanders: tuple[tuple[int, str], ...] = ()


def scout_report(raw: bytes, province_id: int) -> ScoutReport:
    """The scouted garrison of ``province_id``, most numerous type first.

    ``[(unit_type, count), ...]``: the counts of the top two types are exact
    (from the intel meta, matched to the report text by position), as are the
    counts of the "huge" / "flying" / "commanded by" sentences; every further
    type the "consists of mainly" list names comes with ``None`` -- the game
    stores its presence but never its count.  ``total`` is the garrison size
    the report's first line shows; ``unmatched`` holds names that no unit in
    data/units.csv carries.  Names resolve to ids by id alone
    (``unit_id_by_name``): the report does not name the army's nation.
    """
    intel = scout_intel(raw, province_id) or {}
    exact = list(intel.items())
    text = scout_report_text(raw, province_id) or ""
    names = scout_type_names(text) if text else []
    out: list[tuple[int, int | None]] = []
    unmatched: list[str] = []
    for i, name in enumerate(names):
        if i < len(exact):
            out.append(exact[i])
            continue
        uid = unit_id_by_name(name)
        if uid is None:
            unmatched.append(name)
        else:
            out.append((uid, None))
    if not out:
        out = exact
    elif len(exact) > len(names):
        out += exact[len(names):]
    # The "huge" sentence carries exact counts, so it is appended with them
    # (no estimation) unless the type is already listed above.  The flying
    # sentence names one more type, usually a commander or a flyer that is
    # not part of the "consists of mainly" list.
    seen = {uid for uid, _ in out}
    for name, count in scout_huge_units(text) + scout_flying_units(text):
        uid = unit_id_by_name(name)
        if uid is None:
            if name not in unmatched:
                unmatched.append(name)
        elif uid not in seen:
            out.append((uid, count))
            seen.add(uid)
    # The "commanded by" sentence names the army's leader, which the "mainly"
    # list never counts; it is one unit when it is not already sighted.
    commanders = scout_commander_names(text)
    for uid, _ in commanders:
        if uid not in seen:
            out.append((uid, 1))
            seen.add(uid)
    return ScoutReport(out, scout_total(raw, province_id), tuple(unmatched),
                       tuple(commanders))


def scout_army(raw: bytes, province_id: int) -> list[tuple[int, int | None]]:
    """Shorthand for ``scout_report(...).units``."""
    return scout_report(raw, province_id).units


# --------------------------------------------------------------------------
# battle reports: "vcr_VCR" records in the binary section.  A province can
# have several battle reports in a turn (e.g. several armies attacking it one
# after another); they appear in file order, which is the order the battles
# were resolved in and the order the GUI lists them in.  The .trn stores no
# ritual/movement phase field -- the position in this list is the only clue.
#
#     "vcr_VCR" [u32 ver=4][u32 province][u32 defender][u32 attacker]
#     [u32 cstlmode][u32 seed] ... [u32 province again at vcr+39] ...
#     then a "BCD\x17\x19\x64" block of 8- or
#     10-byte entries, terminated by ff 2c:
#         [u8 side][81][u16 unit_type][u8 count_lo][u8 count_hi][00 00][u16 ?]
#         [u8 side][u8 unit_type][u8 count_lo][u8 count_hi][00 00 00 00]
#
# The field names come from the writer's own debug string in the exe:
#   "  createvcr to%d lnr%d (own %d/%d) def%d att%d cstlmode%d seed%d\n"
# so +8 is the *defender* nation, +12 the *attacker*, +16 the castle mode and
# +20 the battle's RNG seed.
#
# side 0/1 = attacker's army, side 2/3 = defender's army (0/2 = at battle
# start, 1/3 = what is left at the end).  Counts: lo byte, except commander
# entries which store a 1 in the hi byte instead (lo=0).  Battle casualties
# are absent from the unit record table (dead units are removed), so these
# BCD blocks are the only place a wiped-out army (e.g. a relieving nation that
# left no survivors) can be read from.
# --------------------------------------------------------------------------
VCR_MAGIC = b'vcr_VCR'
BCD_HEAD = b'BCD\x17\x19\x64'


def battle_reports(raw: bytes, province: int) -> list[dict]:
    """Every battle report at ``province``, in file order (= resolution order).

    Each entry: ``{'defender': nation, 'attacker': nation,
    'cstlmode': int, 'seed': int,
    'start': {nation: {unit_type: count}}}`` with the armies as they were
    when the battle began.
    """
    out: list[dict] = []
    pos = 0
    while True:
        v = raw.find(VCR_MAGIC, pos)
        if v < 0:
            break
        pos = v + 1
        ver, prov_field, nat_a, nat_b = struct.unpack_from('<IIII', raw, v + 7)
        # Follow-up VCR records belonging to the same battle sequence store 0
        # in the primary province field; +39 still carries the real province.
        prov = prov_field or struct.unpack_from('<I', raw, v + 39)[0]
        if prov != province:
            continue
        cstl, seed = struct.unpack_from('<II', raw, v + 23)
        nxt = raw.find(VCR_MAGIC, v + 7)
        b = raw.find(BCD_HEAD, v + 7)
        if b < 0 or (0 <= nxt < b):
            continue
        start: dict[int, dict[int, int]] = {nat_a: {}, nat_b: {}}
        start_cmdrs: dict[int, dict[int, int]] = {nat_a: {}, nat_b: {}}
        i = b + len(BCD_HEAD)
        while i + 8 <= len(raw) and raw[i:i + 2] != b'\xff\x2c':
            side = raw[i]
            if raw[i + 1] == 0x81:
                if i + 10 > len(raw):
                    break
                typ = struct.unpack_from('<H', raw, i + 2)[0]
                lo, hi = raw[i + 4], raw[i + 5]
                step = 10
            else:
                typ = raw[i + 1]
                lo, hi = raw[i + 2], raw[i + 3]
                step = 8
            count = lo if lo else hi
            nation = nat_b if side in (0, 1) else nat_a
            if side in (0, 2) and typ in VALID_UNITS and count:
                start[nation][typ] = start[nation].get(typ, 0) + count
                if lo == 0 and hi:
                    start_cmdrs[nation][typ] = (
                        start_cmdrs[nation].get(typ, 0) + count)
            i += step
        out.append({'defender': nat_a, 'attacker': nat_b,
                    'cstlmode': cstl, 'seed': seed, 'start': start,
                    'start_commanders': start_cmdrs,
                    'vcr': v, 'bcd': b})
    return out


# --------------------------------------------------------------------------
# unit records: the armies a battle report is about are stored here, not in
# the message block.  A .trn keeps one record per unit instance, stride 173:
#     +4  u32 unit id (unique, the same unit is stored twice)
#     +32 u32 per-type constant, 0xffffffff for commanders
#     +36 u16 unit type
#     +38 u16 current hit points
#     +40 u16 province the unit is in now
#     +42 u16 province the unit started the turn in (!= +40: it moved)
#     +44 u16 squad id inside the province (not a count)
#     +68 u16 nation that owns the unit (0 = independents)
# --------------------------------------------------------------------------
TRN_STRIDE = 173

# Province bound of the record scan below.  A .trn carries no map, so the ids
# come from the save's own .map: on an 841 province map (sanguosha.map) the
# army stands at province 556, which a fixed 1..300 guess rejected outright,
# while dropping the bound lets the byte-step scan accept garbage (measured on
# that save: 747 records at provinces the map does not have, 511 with absurd
# hp).  build() calls set_map_provinces() with the save's map before reading
# any .trn; the default covers every official map for other callers.
DEFAULT_PROVINCE_MAX = 2048
_province_max = DEFAULT_PROVINCE_MAX

MAP_TERRAIN = re.compile(r"^\s*#terrain\s+(\d+)", re.M)


def _is_plane2(path: Path) -> bool:
    """A second-plane map file.

    A two-plane game stores each plane in its own .map: the surface one under
    the game's map name and the underworld as ``__under_srvgame_<game>.map``
    (saved random map) or ``<map>_plane2.map`` (hand made map).
    """
    name = path.name.lower()
    return name.startswith("__under_") or "_plane2." in name


def map_provinces(save_dir) -> set[int]:
    """The province ids of the map a save is played on, both planes.

    The surface file holds ids 1..N; the second plane's ids are plane-local
    (1..M) and the game shifts them by N.  Measured on Wherecrowfeast:
    surface 1..166, the underworld's 61st province is game province 227
    ("The Nether") and holds the save's largest army.  Reading only the
    surface file bounded the scan at 166, so every underworld unit looked
    like a mis-aligned record and ``player.provinces`` = [227] failed with
    "no units found".
    """
    files = sorted(Path(save_dir).glob("*.map"))
    ids: set[int] = set()
    for path in files:
        if not _is_plane2(path):
            ids.update(int(m) for m in MAP_TERRAIN.findall(
                path.read_text(errors="replace")))
    base = max(ids) if ids else 0
    for path in files:
        if base and _is_plane2(path):
            ids.update(base + int(m) for m in MAP_TERRAIN.findall(
                path.read_text(errors="replace")))
    return ids


def set_map_provinces(provinces) -> None:
    """Bound unit record scans by the provinces the save's map really has.

    Call this once per save, before reading its .trn/.2h.  An empty set keeps
    the fallback bound (a save with no .map staged next to it).
    """
    global _province_max
    _province_max = max(provinces) if provinces else DEFAULT_PROVINCE_MAX


def province_max() -> int:
    """Highest province id the current scan accepts."""
    return _province_max


def _looks_like_record(raw: bytes, pos: int) -> bool:
    if pos < 0 or pos + TRN_STRIDE > len(raw):
        return False
    typ, hp = struct.unpack_from("<HH", raw, pos + 36)
    here, origin = struct.unpack_from("<HH", raw, pos + 40)
    # No hp bound: damaged or high-hp units (222, 260) are real records, and
    # the type/province/origin checks already filter out false matches.
    return (typ in VALID_UNITS and hp > 0
            and 1 <= here <= _province_max
            and 1 <= origin <= _province_max)


def unit_records(raw: bytes) -> list[dict]:
    """Every unit instance of a .trn, de-duplicated by unit id AND by pos.

    Records sit back to back at ``TRN_STRIDE``, but "shadow" records
    (type 5/9-12/16/20/53, hp=0, garbage nation 2435/65535) can slot between
    real ones.  We scan byte-by-byte collecting every slot that passes
    ``_looks_like_record`` AND has a valid nation AND a plausible uid,
    dedupe by uid, and return.  A stride-mode scan after a valid record
    misses real records that sit behind a shadow record; byte-step is
    slower but correct.
    """
    found: dict[int, dict] = {}
    pos = 0
    while pos < len(raw) - TRN_STRIDE:
        if not _looks_like_record(raw, pos):
            pos += 1
            continue
        nation = struct.unpack_from("<H", raw, pos + 68)[0]
        uid = struct.unpack_from("<I", raw, pos + 4)[0]
        if nation >= 65535 or nation == 2435 or not (1 <= uid < 10_000_000):
            # Shadow or garbage record — skip.
            pos += 1
            continue
        found.setdefault(uid, {
            "pos": pos,
            "uid": uid,
            "type": struct.unpack_from("<H", raw, pos + 36)[0],
            "hp": struct.unpack_from("<H", raw, pos + 38)[0],
            "province": struct.unpack_from("<H", raw, pos + 40)[0],
            "origin": struct.unpack_from("<H", raw, pos + 42)[0],
            "nation": nation,
        })
        pos += 1  # byte-step — don't jump stride, real records may be sparse
    return list(found.values())


def province_units(raw: bytes, province: int, nation: int | None = None,
                   exclude_nation: int | None = None) -> list[int]:
    """Unit types standing in ``province``, one entry per unit.

    This is what a battle report at ``province`` shows: both armies are in the
    same province record, and their owners are told apart by the record's
    nation field.  ``nation`` keeps only that nation's units, and
    ``exclude_nation`` drops them (the enemy of the reading player is simply
    "everything that is not mine").
    """
    out: list[int] = []
    for rec in unit_records(raw):
        if rec["province"] != province:
            continue
        if nation is not None and rec["nation"] != nation:
            continue
        if exclude_nation is not None and rec["nation"] == exclude_nation:
            continue
        out.append(rec["type"])
    return out


# --------------------------------------------------------------------------
# helpers for the build step
# --------------------------------------------------------------------------
def split_evenly(units: list[int]) -> list[tuple[int, int]]:
    """Total count split evenly across unique unit types.

    Returns ``[(unit_type, count), ...]``.  Leftover units go to the first
    types in order of appearance.
    """
    from collections import Counter, OrderedDict

    seen: OrderedDict[int, int] = OrderedDict()
    for t in units:
        seen[t] = seen.get(t, 0) + 1
    total = len(units)
    n_types = len(seen)
    if n_types == 0:
        return []
    base = total // n_types
    leftover = total - base * n_types
    result: list[tuple[int, int]] = []
    for i, (t, _) in enumerate(seen.items()):
        result.append((t, base + (1 if i < leftover else 0)))
    return result


# --------------------------------------------------------------------------
# commander records inside a player .trn
# --------------------------------------------------------------------------
def _unit_type_map(raw: bytes, provinces: set[int] | None = None) -> dict[int, int]:
    """unit id -> unit type for every unit record sitting in ``provinces``.

    ``provinces=None`` maps every record in the file; used to locate the
    pretender, which may stand outside the provinces being copied.
    """
    return {rec["uid"]: rec["type"] for rec in unit_records(raw)
            if provinces is None or rec["province"] in provinces}


def pretender_type(raw: bytes, god_name: str,
                   provinces: set[int] | None = None,
                   chassis: set[int] | None = None) -> int | None:
    """Unit type of the pretender inside a .trn / .2h, or None.

    The pretender's com record carries the same name as the nation design's
    god, followed by its unit id: ``[..][name][0x4f][u32 unitid]``.  That is
    the only reliable way to tell which unit *record* is the pretender — the
    .trn stores units in arbitrary order, so record 0 is not the commander.

    The name also appears in the design array and in the god's name record,
    where the u32 behind it is NOT a unit id (it can be a small counter, and
    some of those numbers happen to be unit ids too — "Cux47" was read as
    uid 4, whose garbage record typed as 200 Charioteer).  A real hit is a
    unit record that carries the god flag (636 at +46), so the god flag
    picks the candidate; a plain unit-id hit is only the fallback for saves
    where the flag is not set.

    ``chassis`` is the nation's pretender list (``data/pretenders.csv``, the
    Dom6 Inspector's ``pretender_types_by_nation``): it is the unit-type
    test of what may stand in the god slot.  A save that stores no god flag
    otherwise matches any record whose id happens to follow the name — the
    source of a "pretender" typed 113 Lord Guardian (a C'tis commander) and
    of the host's ``king is no god``.  Candidates are therefore ranked
    flag+chassis, flag, chassis, and a non-chassis type is not returned.
    """
    if not god_name:
        return None
    records = {rec["uid"]: rec for rec in unit_records(raw)}
    enc = bytes(ord(c) ^ XOR for c in god_name) + b'\x4f'
    candidates: list[dict] = []
    pos = 0
    while True:
        idx = raw.find(enc, pos)
        if idx < 0:
            break
        pos = idx + 1
        end = idx + len(enc)
        if end + 4 > len(raw):
            continue
        rec = records.get(struct.unpack_from('<I', raw, end)[0])
        if rec is not None:
            candidates.append(rec)

    def _flagged(rec: dict) -> bool:
        return struct.unpack_from('<H', raw, rec['pos'] + 46)[0] == 636

    def _is_chassis(rec: dict) -> bool:
        return chassis is None or rec['type'] in chassis

    for rec in candidates:
        if _flagged(rec) and _is_chassis(rec):
            return rec['type']
    for rec in candidates:
        if _flagged(rec):
            return rec['type']
    if chassis is not None:
        for rec in candidates:
            if _is_chassis(rec):
                return rec['type']
        return None
    for rec in candidates:
        if provinces is None or rec['province'] in provinces:
            return rec['type']
    return None


def commander_type_counts(raw: bytes, provinces: set[int]) -> dict[int, int]:
    """Commander unit types found in ``provinces`` of a .trn, with counts.

    A .trn stores mid-game unit records as: u32 id at +4, u16 type at +36,
    province pair at +40/+42.  Commander records look like
    ``[u32 comid][encoded name][0x4f][u32 unitid]``; a unit claimed by one is
    a commander, everything else is a plain unit.  A unit *type* is therefore
    not intrinsically a commander type — this answers "which types actually
    led units in the source provinces" so an arena rebuild can re-arm them.
    """
    unit_type = _unit_type_map(raw, provinces)

    counts: dict[int, int] = {}
    seen_uids: set[int] = set()
    for pos in range(len(raw) - 16):
        q = pos + 4
        name = []
        while q < len(raw) and len(name) < 30:
            c = raw[q] ^ XOR
            q += 1
            if c == 0:
                break
            if not 32 <= c < 127:
                break
            name.append(chr(c))
        else:
            continue
        if len(name) < 3 or len(set(name)) < 2 or raw[q - 1] != XOR:
            continue
        uid = struct.unpack_from('<I', raw, q)[0] if q + 4 <= len(raw) else 0
        typ = unit_type.get(uid)
        if typ and uid not in seen_uids:
            seen_uids.add(uid)
            counts[typ] = counts.get(typ, 0) + 1
    return counts
