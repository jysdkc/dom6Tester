"""Build an arena save from a JSON config.

The arena game already contains both nations as players.  ``player`` (己方)
and ``enemy`` (敌方) each describe where their army and pretender come from:
the player's from provinces and/or battle reports of the source save, the
enemy's from a scout report and/or battle reports.  The player's pretender is
transplanted whole (chassis, name and bless); the enemy keeps its own arena
pretender and only receives the bless read from the source save's design
entry for that nation -- the same row the Pretenders of the World screen
shows.  An empty entry means the bless is not known and no bless is set at
all, unless the scout report sighted a god chassis in the enemy army -- a
chassis cannot be an ordinary soldier, so it becomes the enemy pretender with
the chassis' own default magic paths.  The map is not
generated: ``arena.map``
names a fixed, hand made map folder that is staged under the game name as
authored.

Usage:  python -m dom6arena.arena_build arena_config.json
"""

from __future__ import annotations

import json
import random
import shutil
import struct
import sys
from collections import Counter, deque
from pathlib import Path

if __package__ in (None, ''):
    # Started as a plain script (``python dom6arena/arena_build.py ...`` or an
    # IDE's Run button): the relative imports below need the package parent on
    # sys.path.  Without this the tool dies with "attempted relative import
    # with no known parent package".
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    __package__ = 'dom6arena'

from . import blesses, config, gamedata, newgame, savecrc, saveedit, trn_parse

XOR = 0x4F
STRIDE = saveedit.UNIT_TABLE_STRIDE
CHUNK_TAIL = 175          # name length + 175 == offset of the f4 01 00 00 marker
# Unit types the debug mod grants every capital at game creation.  The
# arena's own grant stays (see _keep_offsets); a copied army never brings
# one along (see _without_debug).
DEBUG_TYPES = {46, 9001, 9002}


class ArenaCapacityError(Exception):
    """The created arena's unit table cannot hold both armies plus the
    kept debug grant.  Independent garrison sizes vary per creation, so
    recreating the arena rolls a new table size."""

    def __init__(self, message: str, count: int = 0, required: int = 0):
        super().__init__(message)
        self.count = count
        self.required = required


# The creation-time --indepstr is only a unit table size lever: every
# independent garrison is deleted afterwards (_clear_independents), so the
# arena's independent strength is always 0.  Records keep growing past the
# game's normal 0..9 range — measured on ww21duel (10 provinces):
#   0 -> 153 records, 9 -> 979, 12 -> 1940, 25 -> 2570.
# 2570 is the practical ceiling of a fixed small map, so an army that needs
# more than that cannot be placed at all and gets a clear error.
MAX_INDEPSTR = 25


def _next_indepstr(current: int, count: int, required: int) -> int:
    """A creation-time --indepstr that should allocate enough records.

    Every recreation costs a full arena build (tens of seconds), so a large
    shortfall is jumped over instead of walking up one step at a time: the
    table grows by roughly 60+ records per indepstr step on the arena map.
    Clamped to MAX_INDEPSTR; returning ``current`` means it is already maxed
    out and the army cannot fit.
    """
    if count <= 0 or required <= count:
        return min(MAX_INDEPSTR, current + 1)
    step = -(-(required - count) // 60)           # ceil division
    return min(MAX_INDEPSTR, current + step)


def _enc(text: str) -> bytes:
    return bytes(ord(c) ^ XOR for c in text)


def _dec(buf: bytes, pos: int) -> tuple[str, int]:
    out = []
    while pos < len(buf):
        c = buf[pos] ^ XOR
        pos += 1
        if c == 0:
            break
        out.append(chr(c))
    return ''.join(out), pos


# --------------------------------------------------------------------------
# nation design records: ac 0b <u32 nation> 02 31 <6 scales> <title> ...
# --------------------------------------------------------------------------
def _bless_before_name(raw: bytes, lo: int, end: int,
                       n_hint: int) -> tuple[str, int, int] | None:
    """Pretender name, bless count and bless offset.

    The bless ids always sit immediately before the pretender name, which is
    what the record closes with: the name's terminator plus up to two empty
    hero/prophet names.  Reading from the end therefore finds both, and the
    count is the dword of the ``<count> 0`` pair in front of the array.  A
    design with extra bless entries (ids 1000+, see ``_parse_design``) has more
    dwords before the array, but none of those is a valid bless id, so only the
    real array matches.

    ``n_hint`` is the count read from the fixed layout; it is the fallback for
    a record whose count is not repeated in front of the array.
    """
    tail = end
    while tail > lo and raw[tail - 1] == XOR:
        tail -= 1
    for start in range(tail - 1, lo, -1):
        name = raw[start:tail]
        if not name or any(b == XOR or not 32 <= (b ^ XOR) < 127 for b in name):
            continue
        decoded = bytes(b ^ XOR for b in name).decode('latin1')
        if not any(c.isalnum() for c in decoded):
            continue
        for n in range(1, 17):
            vals_pos = start - 4 * n
            if vals_pos < lo + 8:
                continue
            if not all(v < BLESS_COUNT
                       for v in struct.unpack_from(f'<{n}I', raw, vals_pos)):
                continue
            if struct.unpack_from('<I', raw, vals_pos - 8)[0] == n and \
                    struct.unpack_from('<I', raw, vals_pos - 4)[0] == 0:
                return decoded, n, vals_pos
        if n_hint:
            vals_pos = start - 4 * n_hint
            if vals_pos >= lo and all(
                    v < BLESS_COUNT
                    for v in struct.unpack_from(f'<{n_hint}I', raw, vals_pos)):
                return decoded, n_hint, vals_pos
    return None


def _parse_design(raw: bytes, pos: int, end: int | None = None) -> dict:
    assert raw[pos:pos + 2] == b'\xac\x0b', pos
    nation = struct.unpack_from('<I', raw, pos + 2)[0]
    assert raw[pos + 6:pos + 8] == b'\x02\x31', (pos, raw[pos:pos + 12].hex())
    title, p = _dec(raw, pos + 14)
    # After the title: two flag dwords, then a list of ``<id> <value> <0>``
    # entries for bless effects that carry a magnitude (ids 1000+ -- nation 98
    # in ``mortal`` has ``Poison resistance 10`` and ``Animal Awe 1`` there), a
    # 0 terminator, then the bless count, a u32 and that many bless ids.
    q = p + 8
    extras: list[tuple[int, int]] = []
    while q + 12 <= len(raw) and struct.unpack_from('<I', raw, q)[0] >= 1000:
        extras.append((struct.unpack_from('<I', raw, q)[0],
                       struct.unpack_from('<I', raw, q + 4)[0]))
        q += 12
    q += 4                                     # 0 terminator
    n = struct.unpack_from('<I', raw, q)[0]
    vals_pos, count_pos = q + 8, q
    god, _ = _dec(raw, vals_pos + 4 * n)
    if end is not None:
        found = _bless_before_name(raw, q, end, n)
        if found is not None:
            god, n, vals_pos = found
            count_pos = vals_pos - 8
    vals = list(struct.unpack_from(f'<{n}I', raw, vals_pos))
    # Two more XOR names follow the pretender name (hero / prophet names;
    # empty strings for a nation that is not in the game).  They must be
    # consumed to find where this record ends, otherwise the array walk stops
    # right after the first nation that actually has a pretender.
    _, tail = _dec(raw, vals_pos + 4 * n)
    for _ in range(2):
        _, tail = _dec(raw, tail)
    return {'pos': pos, 'end': tail if end is None else end, 'nation': nation,
            'scales': struct.unpack_from('<6b', raw, pos + 8),
            'title': title, 'extras': extras, 'vals': vals, 'god': god,
            'title_end': p, 'count_pos': count_pos, 'vals_pos': vals_pos,
            'god_pos': vals_pos + 4 * n}


def _with_design(record: bytes, source: bytes) -> bytes:
    """Copy a source design's bless onto an arena record.

    Everything from after the title up to the pretender name is replaced: the
    extra ``<id> <value> <0>`` bless entries, the count and the bless ids.  The
    arena record keeps its header, scales, title and pretender name, so the
    enemy still has its own chassis while its bless is exactly the source
    nation's -- copying only the id array would drop the magnitude entries
    (Morale +2, Poison resistance +10, Animal Awe +1, ...).
    """
    here = _parse_design(record, 0, len(record))
    there = _parse_design(source, 0, len(source))
    return (record[:here['title_end']]
            + source[there['title_end']:there['god_pos']]
            + record[here['god_pos']:])


def _design_header_at(raw: bytes, pos: int) -> bool:
    if pos + 8 > len(raw) or raw[pos:pos + 2] != b'\xac\x0b':
        return False
    if raw[pos + 6:pos + 8] != b'\x02\x31':
        return False
    nation = struct.unpack_from('<I', raw, pos + 2)[0]
    return 1 <= nation <= 2000


def _next_design_header(raw: bytes, pos: int, limit: int) -> int | None:
    """Offset of the next design record header at or after ``pos``."""
    while True:
        i = raw.find(b'\xac\x0b', pos, limit)
        if i < 0:
            return None
        if _design_header_at(raw, i):
            return i
        pos = i + 1


def _design_array(raw: bytes) -> tuple[int, int, list[dict]]:
    start = raw.find(b'\xac\x0b\x01\x00\x00\x00\x02\x31')
    if start < 0:
        raise ValueError('design record array not found')
    pos, records = start, []
    while _design_header_at(raw, pos):
        # A record can carry extra bless entries between its flags and the
        # bless array (see _parse_design); the next real header is the
        # authoritative end either way.
        nxt = _next_design_header(raw, pos + 8, min(len(raw), pos + 1024))
        rec = _parse_design(raw, pos, nxt)
        if nxt is not None and nxt != rec['end']:
            rec['end'] = nxt
        records.append(rec)
        pos = rec['end']
    return start, pos, records


def _design_for(raw: bytes, nation: int) -> dict:
    for rec in _design_array(raw)[2]:
        if rec['nation'] == nation:
            return rec
    raise ValueError(f'no design record for nation {nation}')


def _design_for_or_none(raw: bytes, nation: int) -> dict | None:
    try:
        return _design_for(raw, nation)
    except ValueError:
        return None


# Size of the bless table (Dominions6.exe).  Bless vals are 0-based indices
# into it, so anything at or above this is not a bless id at all.
BLESS_COUNT = 99


def _random_pretender(nation: gamedata.Nation, rng: random.Random) -> int:
    """A random legal pretender chassis for ``nation``.

    Immobile statue-class chassis (Oracle, Monolith, ...) are excluded: the
    forged arena design is awake, and the host exiles an immobile god to an
    off-map province instead of placing it in the capital.
    """
    choices = sorted(
        uid for uid in gamedata.pretenders().get(nation.id, set())
        if gamedata.units().get(uid) and not gamedata.units()[uid].immobile)
    if not choices:
        raise ValueError(
            f'no mobile pretender chassis for {nation.name} ({nation.id})')
    return rng.choice(choices)


# --------------------------------------------------------------------------
# pretender name: the same string lives in three places
#   blurb        [20 x ff][name][0x4f][params..][f4 01 00 00]
#   name record  [u32][name][0x4f][u32 instance id][20 x ff]
#   design rec   ...<u32 n><vals>[name][0x4f][4f 4f]
# --------------------------------------------------------------------------
def _blurb_owner_distance(buf: bytes, pos: int, nation: int,
                          window: int) -> int | None:
    """Distance of the nearest u32 equal to ``nation`` around a blurb.

    A god blurb sits inside a repeated per-player block whose nearest nation
    tag (verified on a two-human hotseat save: a u32 nation id 618 bytes in
    front of the blurb) names the block's owner.  The other player's tag is a
    whole block away, so within half a block the nearest tag is unambiguous.
    """
    needle = struct.pack('<I', nation)
    best: int | None = None
    lo, hi = max(0, pos - window), min(len(buf) - 4, pos + window)
    p = lo
    while p <= hi:
        j = buf.find(needle, p, hi + 4)
        if j < 0:
            break
        d = abs(j - pos)
        if best is None or d < best:
            best = d
        p = j + 1
    return best


def _god_slots(buf: bytes, name: str, nation: int | None = None,
               uid_nation: dict[int, int] | None = None) -> dict[str, int]:
    """Offsets of the three encodings of the pretender name.

    blurb        preceded by 20 x ff   (name, design block, ... menu blurb)
    name_record  followed by u32 id then 20 x ff   (the commander record)
    design       inside the nation design array; a design record ends with two
                 more XOR names (hero / prophet, usually empty), so the
                 ``4f 4f`` tail only marks a record whose extra names are
                 both blank and is kept as a fallback

    A freshly forged hotseat arena gives BOTH gods the same placeholder name,
    so plain "first occurrence" matching attaches the player's transplanted
    god to the enemy's slot (and vice versa).  When ``nation`` is given the
    name record is chosen by the nation of the unit id behind it
    (``uid_nation``: unit id -> nation) and the blurb by the nearest nation
    tag inside its per-player block.  Without the hints the old first-match
    behaviour applies (source saves carry a single copy of each god name).
    """
    try:
        arr_start, arr_end, _ = _design_array(buf)
    except ValueError:
        arr_start = arr_end = -1
    pat = _enc(name) + b'\x4f'
    blurbs: list[int] = []
    name_records: list[tuple[int, int]] = []      # (offset, unit id)
    found_design: int | None = None
    pos = buf.find(pat)
    while pos >= 0:
        after = buf[pos + len(pat):pos + len(pat) + 24]
        if arr_start <= pos < arr_end:
            if found_design is None:
                found_design = pos
        elif after[:2] == b'\x4f\x4f':
            if found_design is None:
                found_design = pos
        elif buf[pos - 20:pos] == b'\xff' * 20:
            blurbs.append(pos)
        elif after[4:24] == b'\xff' * 20:
            uid = struct.unpack_from('<I', after)[0]
            name_records.append((pos, uid))
        pos = buf.find(pat, pos + 1)

    found: dict[str, int] = {}
    if found_design is not None:
        found['design'] = found_design
    if blurbs:
        choice = blurbs[0]
        if nation is not None and len(blurbs) > 1:
            gaps = [b - a for a, b in zip(blurbs, blurbs[1:]) if b > a]
            window = min(gaps) // 2 if gaps else 1900
            ranked = [(d, b) for b in blurbs
                      if (d := _blurb_owner_distance(buf, b, nation,
                                                     window)) is not None]
            if ranked:
                choice = min(ranked)[1]
        found['blurb'] = choice
    if name_records:
        choice = name_records[0][0]
        if nation is not None and uid_nation:
            owned = [o for o, uid in name_records
                     if uid_nation.get(uid) == nation]
            if owned:
                choice = owned[0]
        found['name_record'] = choice
    return found


def _ftherlnd_unit_table(buf: bytes) -> tuple[int, int, int] | None:
    """The packed unit table, but only when the buffer really is ftherlnd.

    The header cannot tell the kinds apart: the u32 at offset 14 is the
    TURN NUMBER (14 in a mid-game save, 1 in a turn-0 arena), present in
    ftherlnd and .trn alike.  ``find_unit_table`` alone false-matches a
    short sequential run inside a .trn, so the candidate table is
    validated record by record: the packed id sequence plus sane type,
    province and nation fields.  A real table passes ~93% of records
    (deleted type-0 records and modded types make the rest), a .trn
    candidate fails nearly all of them.
    """
    table = saveedit.find_unit_table(buf)
    if table is None:
        return None
    base, stride, count = table
    nations = set(gamedata.nations())
    max_type = max(gamedata.units())
    good = 0
    for k in range(count):
        o = base + k * stride
        uid = struct.unpack_from('<I', buf, o)[0]
        typ = struct.unpack_from('<H', buf, o + 32)[0]
        p1, p2 = struct.unpack_from('<HH', buf, o + 36)
        nat = struct.unpack_from('<H', buf, o + 64)[0]
        if (uid == k + 1 and 0 < typ <= max_type
                and 1 <= p1 <= 5000 and 1 <= p2 <= 5000
                and (nat == 0 or nat in nations)):
            good += 1
    if good / count < 0.85:
        return None
    return table


def _uid_nation_map(buf: bytes) -> dict[int, int]:
    """Unit id -> owning nation.

    ftherlnd holds the packed 1..n unit table (nation at record +64); the
    turn/orders files store their 173 byte records with a 4 byte prefix
    (nation at +68) and their ids are NOT packed, so they go through the
    .trn record scan.  NOTE: a turn-0 (pretender submission) .trn stamps
    those records unreliably or omits the gods entirely; callers handling
    such files should pass the ftherlnd-derived map of the same game
    instead (world unit ids are stable across every file of a game).
    """
    table = _ftherlnd_unit_table(buf)
    if table is not None:
        base, stride, count = table
        return {k + 1: struct.unpack_from('<H', buf, base + k * stride + 64)[0]
                for k in range(count)}
    return {r['uid']: r['nation'] for r in trn_parse.unit_records(buf)}


def _pretender_uid(raw: bytes, name: str, uids: set[int]) -> int | None:
    """Unit id of the pretender's live commander record.

    A .trn holds the pretender name several times: the menu blurb, the nation
    design record and the commander record ``[u32 comid][name][0x4f][u32 uid]``.
    Only the last one names the unit standing on the map, and the name record
    near the top of the file can carry a different (world state) id, so every
    candidate is filtered against the unit ids actually present in the copied
    provinces.
    """
    pat = _enc(name) + b'\x4f'
    pos = 0
    while True:
        idx = raw.find(pat, pos)
        if idx < 0:
            return None
        pos = idx + 1
        end = idx + len(pat)
        if end + 4 <= len(raw):
            uid = struct.unpack_from('<I', raw, end)[0]
            if uid in uids:
                return uid


def _path_vector(buf: bytes, name: str) -> bytes:
    """The 9 byte magic-path vector stored right after a pretender's blurb.

    A save can hold several occurrences of the name behind a run of ff, e.g. a
    placeholder whose bytes are all zero; only the real blurb carries the
    path vector, so prefer the first candidate that is not all zero.
    """
    if not name:
        return b''
    pat = _enc(name) + b'\x4f'
    fallback = b''
    pos = buf.find(pat)
    while pos >= 0:
        if buf[pos - 20:pos] == b'\xff' * 20:
            vec = buf[pos + len(pat):pos + len(pat) + 9]
            if len(vec) == 9 and any(vec):
                return vec
            if not fallback:
                fallback = vec
        pos = buf.find(pat, pos + 1)
    return fallback


def _copy_pretender(raw: bytearray, src: bytes, old: str, new: str,
                    nation: int | None = None,
                    uid_nation: dict[int, int] | None = None) -> bytearray:
    """Replace ONE nation's arena pretender (``old``) with the source one.

    Both hotseat gods start life under the same placeholder name, so every
    slot is attributed to ``nation`` first: the blurb via its per-player
    block's nation tag, the commander name record via the nation of the unit
    id behind it.  Without that attribution the source name would be pasted
    onto the enemy god (observed: host "has god Bebel" on nation 12).
    """
    old_bytes = bytes(raw)
    old_slots = _god_slots(old_bytes, old, nation=nation,
                           uid_nation=uid_nation)
    new_slots = _god_slots(src, new)
    for slot in ('blurb', 'name_record'):
        if slot not in old_slots or slot not in new_slots:
            raise ValueError(f'pretender {slot} not found (old={old}, new={new})')
    if ('design' in old_slots) != ('design' in new_slots):
        raise ValueError('design slot mismatch between saves')
    old_design = old_bytes[old_slots['blurb'] + len(old) + 1:][:8]
    new_design = src[new_slots['blurb'] + len(new) + 1:][:8]
    if len(old_design) != 8 or len(new_design) != 8:
        raise ValueError('pretender blurb too short')

    # 1. blurb: variable name length -> whole chunk replacement
    o, n = old_slots['blurb'], new_slots['blurb']
    oend = o + len(old) + CHUNK_TAIL
    nend = n + len(new) + CHUNK_TAIL
    if old_bytes[oend:oend + 4] != b'\xf4\x01\x00\x00' or src[nend:nend + 4] != b'\xf4\x01\x00\x00':
        raise ValueError('pretender blurb layout unexpected')
    raw = bytearray(old_bytes[:o] + src[n:nend] + old_bytes[oend:])

    # 2. name record (the host prints this name in "has god ..."): the
    #    enemy placeholder of the same name must stay untouched, so the
    #    record is re-located by its unit id's nation, not by first match.
    o = _god_slots(bytes(raw), old, nation=nation,
                   uid_nation=uid_nation)['name_record']
    raw = bytearray(bytes(raw)[:o] + _enc(new) + b'\x4f'
                    + bytes(raw)[o + len(old) + 1:])

    # 3. the live design block inside that same record: the game reads this
    #    one, and it sits behind a run of 10 x ff + 7 x 00 + one marker byte.
    #    Some saves (.trn-only hotseat) don't carry this pattern — step 1+2
    #    (blurb + name record) still give the client its visible name, and
    #    the design-array swap (in _transplant) provides paths/bless/scales.
    rec = _god_slots(bytes(raw), new, nation=nation,
                     uid_nation=uid_nation)['name_record']
    try:
        s_start, s_end = _live_block(src, new_slots['name_record'], new_design)
        d_start, d_end = _live_block(bytes(raw), rec, old_design)
    except ValueError:
        print('    (no live design block in source — design array swap '
              'handles paths/bless/scales)')
        return raw
    span = s_end - s_start
    raw[d_start:d_start + span] = src[s_start:s_end]
    if d_end > d_start + span:
        raw[d_start + span:d_end] = b'\x00' * (d_end - d_start - span)
    return raw


def _live_block(buf: bytes, rec_pos: int, design: bytes) -> tuple[int, int]:
    """(start, end) of a design block copy stored in the pretender record.

    Layout: 10 x ff, 7 x 00, marker byte, 8 design bytes, up to 4 trailing
    nonzero bytes.  The 20 x ff field right after the name must not be
    mistaken for the anchor, hence the "not inside a longer ff run" test.
    """
    anchor = buf.find(b'\xff' * 10, rec_pos)
    while anchor >= 0:
        if (buf[anchor - 1:anchor] != b'\xff'
                and buf[anchor + 10:anchor + 17] == b'\x00' * 7
                and buf[anchor + 18:anchor + 26] == design):
            break
        anchor = buf.find(b'\xff' * 10, anchor + 1)
    if anchor < 0:
        raise ValueError(f'design block {design.hex(" ")} anchor not found')

    start, end = anchor + 10, anchor + 26
    while end < len(buf) and buf[end] and end < anchor + 30:
        end += 1
    return start, end


def _retag_trn_god(buf: bytearray, god_name: str, god_type: int,
                   nation: int) -> int:
    """Set the pretender's unit type inside a .trn.

    The client draws the pretender from its unit record in the turn file, and
    a turn written when the arena was created still holds the chassis of the
    forged god file (a placeholder), even though ftherlnd was given the
    source chassis.  The god's unit id sits behind its name record; every
    copy of that record is retagged.

    The unit id alone does not identify the record: a province intel block in
    the file header can alias a unit record (its dword happens to equal the
    god's unit id and the following bytes look like valid type/hp/province
    fields), and retagging it to the god chassis makes the client abort with
    ``getland: bad owner``.  Only the real unit record also carries the god's
    own nation, so hits are filtered on the nation field as well.

    Returns the number of records changed.
    """
    if not god_name or not god_type:
        return 0
    slot = _god_slots(bytes(buf), god_name).get('name_record')
    if slot is None:
        return 0
    uid_pos = slot + len(_enc(god_name)) + 1
    if uid_pos + 4 > len(buf):
        return 0
    uid = struct.unpack_from('<I', buf, uid_pos)[0]
    if not 1 <= uid < 10_000_000:
        return 0
    data = bytes(buf)
    hits = [pos for pos in range(len(data))
            if trn_parse._looks_like_record(data, pos)
            and struct.unpack_from('<I', data, pos + 4)[0] == uid
            and struct.unpack_from('<H', data, pos + 68)[0] == nation]
    for pos in hits:
        struct.pack_into('<H', buf, pos + 36, god_type)
    return len(hits)


# --------------------------------------------------------------------------
# commander records: name, squad slots and battle orders ("scripts")
#
# A com record follows the unit table and has the same layout in ftherlnd
# and in a .trn:
#     [u32 comid][xor-encoded name][0x4f][u32 unit id]
#     [5 x u32 squad id (ff ff ff ff = empty slot)]
#     [181 byte tail: items, magic paths, battle orders]
# Tail fields that reference the world and therefore need remapping:
#     +92  u32 province the commander is in (0 when none)
#     +126 u32 unit id of one of the commander's own units
#     +140 u8  the commander's order/status code, dropped on transplant
#     +141 8 x u8 carried gems (F,A,W,E,S,D,N,B) -- copied verbatim
# --------------------------------------------------------------------------
COM_BODY = 205          # unit id (4) + squad slots (20) + tail (181)
COM_TAIL = 181
T_PROV = 92
T_UIDREF = 126
T_PATHS = 130           # ten bytes: F,A,W,E,S,D,N,G,B,H
T_ORDER = 140           # one byte; +141 starts the eight gem counts
T_SQUAD_LAYOUT = 152    # 29 bytes: copied squad layout (ftherlnd) / scripts (.2h)
PATH_LETTERS = 'FAWESDNGBH'


def _paths_from_config(value, label: str) -> tuple[int, ...]:
    """A magic-path vector from a config object keyed by path letter.

    ``{"F": 1, "W": 2}`` is Fire 1 and Water 2; every letter left out is 0.
    The save stores the ten paths as consecutive bytes in F,A,W,E,S,D,N,G,B,H
    order, so the object is expanded to that tuple.
    """
    if not isinstance(value, dict):
        raise ValueError(
            f'{label} magic_paths must be an object keyed by path letter '
            f'({" ".join(PATH_LETTERS)})')
    bad = [k for k in value if k not in PATH_LETTERS]
    if bad:
        raise ValueError(
            f'{label} magic_paths has unknown path(s) {bad}; use '
            f'{" ".join(PATH_LETTERS)}')
    paths = [0] * len(PATH_LETTERS)
    for key, level in value.items():
        level = int(level)
        if level < 0 or level > 9:
            raise ValueError(
                f'{label} magic_paths {key} must be 0..9, got {level}')
        paths[PATH_LETTERS.index(key)] = level
    return tuple(paths)


def _com_name_start(raw: bytes, pos: int) -> int | None:
    """Start of the XOR name that ends at the ``0x4f`` at ``pos``.

    The four bytes in front of the name are the comid, which can decode to
    printable garbage ("UNOO", "jl"), and a .2h header is mostly zero bytes
    that decode to 'O'.  A plain printable walk-back therefore runs far past
    the real name.  Commander names are stored as UTF-8 (accented Nidavangr
    names included), so a candidate must decode as UTF-8 — the stray bytes
    in front of a record (0xb0, 0xff, ...) are not valid UTF-8 and reject
    themselves — and must start like a word (uppercase then lowercase), with
    a plausible comid in front of it.
    """
    low = max(4, pos - 64)
    for p in range(pos - 1, low - 1, -1):
        try:
            decoded = bytes(b ^ XOR for b in raw[p:pos]).decode('utf-8')
        except UnicodeDecodeError:
            continue
        if (len(decoded) >= 2 and decoded[0].isupper()
                and decoded[1].islower() and decoded.isprintable()
                and struct.unpack_from('<I', raw, p - 4)[0] < 100_000):
            return p
    return None


def _trn_commander(raw: bytes, uid: int) -> dict | None:
    """The com record of unit ``uid`` in a .trn, or None if it has none.

    Only commanders (and pretenders) carry such a record; an accidental
    ``0x4f + uid`` elsewhere in the file is rejected by the name check
    (printable, second letter lowercase) and the squad-slot check.
    """
    pat = b'\x4f' + struct.pack('<I', uid)
    pos = raw.find(pat)
    while pos >= 0:
        name_start = _com_name_start(raw, pos)
        if name_start is not None:
            # latin-1 keeps one char per byte, so _enc() writes the name back
            # unchanged.  Commander names are not plain ASCII: saves with
            # accented names (Nidavangr, ...) store them as UTF-8 bytes.
            name = bytes(b ^ XOR for b in raw[name_start:pos]).decode('latin1')
            body = raw[pos + 5:pos + 5 + COM_BODY - 4]
            if len(body) == COM_BODY - 4:
                squads = struct.unpack_from('<5I', body, 0)
                tail = body[20:20 + COM_TAIL]
                # Squads may be any mix of ids and ff (including five ff for
                # a hero / commander with no squads and default orders, e.g.
                # Hanif); the name check above is the garbage guard.
                return {'comid': struct.unpack_from('<I', raw,
                                                    name_start - 4)[0],
                        'name': name, 'uid': uid,
                        'squads': [v for v in squads if v != 0xFFFFFFFF],
                        'tail': bytes(tail),
                        'start': name_start - 4,
                        'end': pos + 5 + COM_BODY - 4}
        pos = raw.find(pat, pos + 1)
    return None


def _source_com(h2_raw: bytes | None, trn_raw: bytes, uid: int
                ) -> dict | None:
    """A source commander's com record, orders file first.

    ``.2h`` holds the player's current state (items, carried gems, magic
    paths, squads, battle script); the ``.trn`` is the turn-start snapshot and
    one turn older -- the source pretender carries five 1321 items in the .2h
    and none at all in the .trn.  Every copied com record therefore comes from
    the orders file whenever it has one.  A commander the .2h does not list
    falls back to its own .trn record by uid; that is the same unit (the
    lookup is uid-keyed), not one of the stale-name false positives above.
    """
    com = _trn_commander(h2_raw, uid) if h2_raw else None
    if com is not None:
        return com
    # The orders file can be stale or omit a commander (e.g. a garrison
    # locked in a besieged castle).  _trn_commander is uid-keyed, so a
    # .trn hit for this very uid is the same unit, not a false positive:
    # without it the commander is copied with no name/equipment at all
    # (that is how "Meliath the Fortune Teller" went missing).
    com = _trn_commander(trn_raw, uid)
    if com is None:
        return None
    # A stale text/index block can still pass _trn_commander's loose
    # "0x4f + uid" test (engine log: "Dagan, the Renegade Sage" at .trn
    # offset 658507, whose 181-byte body is text, not a com).  A real com
    # tail holds magic paths as 0..15 at 130..139; a bigger byte means the
    # hit is garbage -- transplanting it put 26812 in an item slot and the
    # host aborted the whole ftherlnd with "bad equip".
    tail = com.get('tail') or b''
    bad_paths = len(tail) >= 140 and any(tail[130 + i] > 15 for i in range(10))
    if len(tail) != 181 or bad_paths:
        print(f'  NOTE: .trn com candidate for uid {uid} is malformed '
              f'(paths {list(tail[130:140])}); name and equipment not copied')
        return None
    return com


VANILLA_ITEM_MAX = 529   # data/item.trs in a stock Dominions 6 install
ITEM_MAX_ID = 699        # raised from the loaded mods (#selectitem/#newitem)

# The item slots are u16 LE at the very start of the com tail: 23 slots,
# slot k at tail + 2k (0..44).  Verified against the engine: injecting id 12
# at +24 reproduces "bad equip", while tail +46/152/162 are not item slots.
# tail + 141..148 holds the eight carried gem counts (and +149 the ninth).
T_ITEMS = 0
T_ITEMS_END = 46


def _item_max_from_mods(mods) -> int:
    """Largest item id defined by the loaded mods (vanilla floor 529)."""
    root = Path(__file__).resolve().parent.parent / 'resources' / 'mods'
    best = VANILLA_ITEM_MAX
    for mod in mods:
        p = root / str(mod)
        if not p.exists():
            p = root / (str(mod) + '.dm')
        if not p.exists():
            continue
        try:
            with open(p, encoding='utf-8', errors='ignore') as fh:
                for line in fh:
                    s = line.strip()
                    if s.startswith('#newitem ') or s.startswith('#selectitem '):
                        try:
                            best = max(best, int(s.split()[1]))
                        except (IndexError, ValueError):
                            pass
        except OSError:
            pass
    return best


def _items_of(tail: bytes) -> list[int]:
    """Item ids held in the com tail's 23 equipment slots (u16 LE)."""
    if len(tail) < T_ITEMS_END:
        return []
    return [struct.unpack_from('<H', tail, o)[0]
            for o in range(T_ITEMS, T_ITEMS_END, 2)]


def _sanitize_items(tail: bytearray, who: str) -> bytearray:
    """Zero equipment ids the arena's item table does not define.

    A stale .trn/.2h slot can hold an id past the last real item (the host
    aborts the whole ftherlnd with "bad equip" if one survives).  Ids above
    ITEM_MAX_ID -- or the 0xFFFF placeholder -- are cleared; legal items,
    paths, gems and scripts are untouched.
    """
    if len(tail) < T_ITEMS_END:
        return tail
    cleared = []
    for off in range(T_ITEMS, T_ITEMS_END, 2):
        iid = struct.unpack_from('<H', tail, off)[0]
        if iid and (iid > ITEM_MAX_ID or iid == 0xFFFF):
            struct.pack_into('<H', tail, off, 0)
            cleared.append(iid)
    if cleared:
        print(f'  dropped invalid item id(s) {cleared} on {who} '
              f'(arena item table ends at {ITEM_MAX_ID})')
    return tail


def _squad_slots(squads: list[tuple[int, int]]) -> list[int]:
    """Squad ids laid out in a com record's five slot fields.

    The host treats slot 0 as the commander's bodyguard squad and caps it to
    the commander's bodyguard limit (5 units for a mounted commander such as
    the Bird Knight Commander).  A copied 79-unit squad placed there comes
    out of the first host as one 5-unit squad plus 74 leaderless units.
    Slot 0 is optional, so it stays empty and the squads go to slots 1..4;
    only a fifth squad has to use it, and then the smallest one does.
    """
    ids = [s for s, _ in sorted(squads, key=lambda kv: kv[1])[:5]]
    return ids if len(ids) == 5 else [0xFFFFFFFF] + ids


def _com_record(comid: int, name: str, uid: int, squads: list[int],
                tail: bytes, keep_layout: bool = False) -> bytes:
    """A whole com record: comid, name, unit id, 5 squad slots, tail.

    The order byte at ``tail + 140`` is written as 0.  It is a leftover of
    the copied commander's move/patrol/sneak order (0 = no order, 1 = move,
    20 = a sneaking scout such as Shinuyama's Bakemono Scout).  The arena is
    a fresh map, so the order points at a province that means nothing there
    and the host rejects the whole ftherlnd with "kdv: bad f" (hostack 2) as
    soon as one commander carries it.  Dropping it only reverts that
    commander to the default (defend) order.

    Only that ONE byte is cleared: ``tail + 141`` is the start of the
    commander's carried gem counts (eight bytes, F,A,W,E,S,D,N,B), and an
    earlier u32 clear at +140 silently wiped the fire/air/water gems.
    Items, magic paths, gems and battle scripts are kept as copied.

    ``keep_layout=False`` clears the image's copy of the 29 byte per-squad
    block at ``tail + 152``.  In ftherlnd that block still describes the
    *source* province's squads -- including which slot held its bodyguard
    squad -- and the host re-applies it on init: a copied squad that now
    sits in a slot the source used for bodyguards is cut down to the
    bodyguard limit (5 units for a mounted commander), so 18 of Aitareya's
    23 Bird Knights came out leaderless even though the squad occupied
    slot 1 with its full size.  The arena is a new map, so the copied
    layout is meaningless and blanking it lets the host lay the squads out
    from scratch with their full size.  The orders file copy must keep it
    (``keep_layout=True``): there the same bytes carry the battle scripts
    the client and the host read.
    """
    slots = (list(squads) + [0xFFFFFFFF] * 5)[:5]
    body = bytearray(tail)
    if len(body) > T_ORDER:
        body[T_ORDER] = 0
    if not keep_layout and squads and len(body) >= COM_TAIL:
        body[T_SQUAD_LAYOUT:COM_TAIL] = bytes(COM_TAIL - T_SQUAD_LAYOUT)
    _sanitize_items(body, f'com {comid} ({name})')
    return (struct.pack('<I', comid) + _enc(name) + b'\x4f'
            + struct.pack('<I', uid) + struct.pack('<5I', *slots) + bytes(body))


def _write_arena_h2(path: Path, god_name: str, god_uid: int, god_tail: bytes,
                    commanders: list[tuple[int, str, int, list[int], bytes]]
                    ) -> None:
    """Populate the arena's orders file with the transplanted com records.

    The client draws squad attachment and battle scripts from the .2h, not
    from ftherlnd; the freshly created arena .2h holds only the forged
    god's (empty) com record, so the GUI shows default orders.  Replace it
    with the source god's record plus one record per transplanted
    commander, reusing the comids and squad ids assigned in ftherlnd.
    """
    if not path.exists():
        return
    raw = path.read_bytes()
    god_com = _trn_commander(raw, god_uid) if god_uid else None
    if god_com is None:
        for uid in range(1, 64):
            god_com = _trn_commander(raw, uid)
            if god_com:
                break
    if god_com is None:
        print(f'  WARNING: no god com record in {path.name}, orders not written')
        return
    recs = [_com_record(god_com['comid'], god_name, god_uid, [], god_tail,
                        keep_layout=True)]
    recs += [_com_record(comid, name, auid, squads, tail, keep_layout=True)
             for comid, name, auid, squads, tail in commanders]
    raw = raw[:god_com['start']] + b''.join(recs) + raw[god_com['end']:]
    path.write_bytes(savecrc.fix(raw))
    print(f'  orders file {path.name}: god + {len(commanders)} '
          f'commander record(s)')


def _h2_add_commanders(
        path: Path,
        commanders: list[tuple[int, str, int, list[int], bytes]],
        god_unit: int | None = None,
        god_tail: bytes | None = None) -> None:
    """Append extra commander records behind a side's own god record.

    ``_write_arena_h2`` rewrites the whole record of a *transplanted* god.
    A side that keeps its forged arena god does not need that, but the host
    still only lists commanders that have a record in the orders file, so
    the extra com records must be spliced in after the existing god record.
    ``god_unit`` is the god's unit id in this arena; the forged god is not
    always one of the first 63 records (the unit table layout varies with the
    creation's indepstr), so look it up by id first.

    ``god_tail`` replaces the forged god's own tail (equipment, carried gems,
    magic paths and battle script) when the god came from a battle report.
    The record is then rewritten in place, with the scripts kept
    (``keep_layout=True``); the commanders follow it.
    """
    if not commanders and god_tail is None:
        return
    if not path.exists():
        print(f'  WARNING: {path.name} missing, extra commander orders '
              f'not written')
        return
    raw = path.read_bytes()
    god_com = _trn_commander(raw, god_unit) if god_unit else None
    if god_com is None:
        for uid in range(1, 64):
            god_com = _trn_commander(raw, uid)
            if god_com:
                break
    if god_com is None:
        print(f'  WARNING: no god com record in {path.name}, extra '
              f'commander orders not written')
        return
    recs = [_com_record(comid, name, auid, squads, tail, keep_layout=True)
            for comid, name, auid, squads, tail in commanders]
    if god_tail is not None or (god_unit and god_com['uid'] != god_unit):
        # The god record keeps the arena's own uid: the client looks the god
        # up by the unit id ftherlnd uses.  A freshly created arena's orders
        # file can name the god by its creation-time id (6, ...), which no
        # longer matches once the copied armies have filled the table, so the
        # record is rewritten with the current id even when the tail is
        # unchanged.
        god_rec = _com_record(
            god_com['comid'], god_com['name'], god_unit or god_com['uid'], [],
            god_com['tail'] if god_tail is None else god_tail,
            keep_layout=True)
        raw = (raw[:god_com['start']] + god_rec
               + b''.join(recs) + raw[god_com['end']:])
    else:
        raw = raw[:god_com['end']] + b''.join(recs) + raw[god_com['end']:]
    path.write_bytes(savecrc.fix(raw))
    print(f'  orders file {path.name}: god'
          f'{" tail" if god_tail is not None else ""} +{len(recs)} '
          f'commander record(s)')


def _h2_set_god_paths(path: Path, paths: tuple[int, ...],
                      god_unit: int | None = None) -> None:
    """Rewrite the forged god's magic paths in a side's orders file."""
    if not path.exists():
        return
    raw = path.read_bytes()
    god_com = _trn_commander(raw, god_unit) if god_unit else None
    if god_com is None:
        for uid in range(1, 64):
            god_com = _trn_commander(raw, uid)
            if god_com:
                break
    if god_com is None:
        print(f'  WARNING: no god com record in {path.name}, pretender '
              f'paths not written')
        return
    tail = bytearray(god_com['tail'])
    tail[T_PATHS:T_PATHS + 10] = bytes(paths)
    rec = _com_record(god_com['comid'], god_com['name'],
                      god_unit or god_com['uid'], [], bytes(tail),
                      keep_layout=True)
    raw = raw[:god_com['start']] + rec + raw[god_com['end']:]
    path.write_bytes(savecrc.fix(raw))


# --------------------------------------------------------------------------
# source save: ftherlnd if present, else the .trn that holds the armies
# --------------------------------------------------------------------------
def _source_dir(arena: dict) -> Path:
    """The save the armies and pretenders are copied from.

    ``arena.path`` overrides the directory lookup; otherwise ``arena.save``
    names a folder in ``savedgames``.
    """
    path = (arena.get('path') or '').strip()
    if path:
        return Path(path)
    name = arena['save']
    return config.saved_games_dir() / name


def _source_army(save_dir: Path, nation: int, provinces: list[int]
                 ) -> tuple[bytes, list[int]]:
    """Army composition of the copied provinces.

    Only the player's OWN .trn is read (matched by nation id ->
    file_name_base, same as the bananas PBEM save).  A hotseat save's
    ``ftherlnd`` is a *world* state whose province lists hold every
    nation's units, and another player's .trn shows our pretender scrubbed
    (zeroed bless, no live design block); neither is ever used.

    Units are selected by the province they are **in** now (+40), not by
    their origin (+42, where they started the turn).  The user's
    ``player.provinces`` means "the army standing in these provinces"; an
    origin filter would also drag along everything that marched out of them
    (a save where 61 units left province 199 for 176 copied 100 units for a
    province holding 15).
    """
    trn_path, raw = _player_trn(save_dir, nation)
    wanted = set(provinces)
    comp = [r['type'] for r in trn_parse.current_unit_records(raw)
            if r['nation'] == nation and r['province'] in wanted]
    if not comp:
        raise ValueError(_no_army_message(trn_path, save_dir, nation,
                                          provinces))
    return raw, comp


def _no_army_message(trn_path: Path, save_dir: Path, nation: int,
                     provinces: list[int]) -> str:
    """A "nothing in these provinces" error that says what the save holds.

    The bare message cannot tell the three usual causes apart: a province id
    that is not on this map, a wrong ``arena.own_nation``, and an army that
    simply stands somewhere else.
    """
    raw = trn_path.read_bytes()
    on_map = trn_parse.map_provinces(save_dir)
    mine = Counter(r['province'] for r in trn_parse.current_unit_records(raw)
                   if r['nation'] == nation)
    lines = [f'no units found in {trn_path.name} for provinces {provinces}']
    if on_map:
        lines.append(f'  map: {len(on_map)} province(s), ids up to '
                     f'{max(on_map)}')
        missing = [p for p in provinces if p not in on_map]
        if missing:
            lines.append(f'  not on this map: {missing} -- fix '
                         f'player.provinces')
    if mine:
        where = ', '.join(
            f'{p} ({n} unit(s))' for p, n in
            sorted(mine.items(), key=lambda kv: (-kv[1], kv[0]))[:8])
        lines.append(f'  nation {nation} stands in: {where}')
    else:
        lines.append(f'  nation {nation} has no unit in this .trn at all -- '
                     f'check arena.own_nation')
    lines.append('  player.provinces = where the army stands now, not where '
                 'it started the turn')
    return '\n'.join(lines)


def _province_records(raw: bytes, provinces: list[int],
                      nation: int) -> list[dict]:
    """Our nation's unit records currently standing in ``provinces``.

    Works on a .trn and on a .2h alike: both store 173 byte records whose
    province, origin and nation fields sit at the same offsets.  Filtered by
    **current province** (+40), not origin (+42): a unit that marched out of
    the province is no longer part of the army the user sees there.
    """
    wanted = set(provinces)
    return [r for r in trn_parse.current_unit_records(raw)
            if r['nation'] == nation and r['province'] in wanted]


def _army_unitspecs(raw: bytes, records: list[dict]) -> list[dict]:
    """Turn source .trn records into write-specs for :func:`_write_nation_army`.

    Each spec carries the keys:
    - ``type`` — unit chassis (written at +32).
    - ``src_uid`` — source .trn uid; used by :func:`_apply_master_chain` to
      remap mount chains (a mount's master points at its rider's source uid,
      which must become the rider's *new* target uid).
    - ``master`` — ``-2`` = this unit IS a commander/rider, ``-1`` = plain
      unit, positive int = mount whose master has that source uid (written
      at +81 by :func:`_apply_master_chain`).
    - ``rider`` — 1 when the rider bit (+25:7) must be set in ftherlnd.
    """
    specs: list[dict] = []
    for r in records:
        pos = r['pos']
        master = struct.unpack_from('<i', raw, pos + 85)[0]
        # Same 4 byte prefix as the master chain: the rider bit (ftherlnd +25)
        # sits at pos + 29 in a .trn.  Reading pos + 25 reads the com type byte
        # instead and reports "not a rider" for every unit.
        flags = raw[pos + 29]
        rider = 1 if (flags & 0x80) else 0
        specs.append({
            'type': r['type'],
            'src_uid': r['uid'],
            'master': master,
            'rider': rider,
            'hp': r['hp'],
        })
    return specs


def _without_debug(raw: bytes, records: list[dict]) -> list[dict]:
    """Source records minus the debug mod's pregame grant.

    A copied capital would otherwise bring the debug mod's free commanders
    (46 Mounted Commander, 9001 Debug Sensei, 9002 mounted tester) into the
    arena.  A dropped rider (+81 = -2) drags its mount (+81 = rider uid)
    with it, so mounted commanders are never split apart.
    """
    # A .trn record carries a 4 byte prefix versus the ftherlnd unit table
    # (uid at +4 instead of +0), so the master chain sits at +85, not +81.
    drop = {r['uid'] for r in records if r['type'] in DEBUG_TYPES}
    changed = True
    while changed:
        changed = False
        for r in records:
            master = struct.unpack_from('<i', raw, r['pos'] + 85)[0]
            if r['uid'] not in drop and master in drop:
                drop.add(r['uid'])
                changed = True
    return [r for r in records if r['uid'] not in drop]


def _detect_nation(save_dir: Path, source: dict) -> int:
    """Nation id of the source save's human player.

    ``lastnation`` is the u32 the game writes when a player saves a turn, so it
    answers the question directly.  Failing that, the human nations are the
    ``.trn`` stems (``mid_bakemono``), and nations.csv maps them to ids.
    """
    explicit = int(source.get('nation') or 0)
    if explicit:
        return explicit
    stamp = save_dir / 'lastnation'
    if stamp.exists() and stamp.stat().st_size >= 4:
        nation = struct.unpack_from('<I', stamp.read_bytes())[0]
        if nation in gamedata.nations():
            return nation
    bases = {p.stem for p in save_dir.glob('*.trn')}
    ids = {n.id for n in gamedata.nations().values() if n.file_name_base in bases}
    if len(ids) == 1:
        return ids.pop()
    raise ValueError(
        f'cannot tell which nation of {save_dir.name} to copy '
        f'(lastnation missing, .trn files {sorted(bases)} -> nations {sorted(ids)}); '
        'set player.nation'
    )


def _detect_own_nation(game: str, explicit: int, fallback: int) -> int:
    """Nation id of the "own side" inside the arena save.

    ``arena.own_nation`` wins; otherwise the arena save's ``lastnation`` (the
    u32 the game writes when that save's player is the human one); otherwise
    the nation the source save belongs to, which is what the arena is built
    around.
    """
    if explicit:
        return explicit
    stamp = config.save_dir(game) / 'lastnation'
    if stamp.exists() and stamp.stat().st_size >= 4:
        nation = struct.unpack_from('<I', stamp.read_bytes())[0]
        if nation in gamedata.nations():
            return nation
    return fallback


def _unit_id(key) -> int:
    """A unit id from a config key: a numeric id or a unit name.

    Names repeat in the data ("Heavy Infantry" has several ids), so a name
    resolves to the first (lowest) id that carries it.
    """
    text = str(key).strip()
    try:
        return int(text)
    except ValueError:
        pass
    wanted = text.lower()
    found = [uid for uid, unit in gamedata.units().items()
             if unit.name.lower() == wanted]
    if not found:
        raise ValueError(f'unknown unit name in config: "{text}"')
    return min(found)


def _custom_unit_specs(entry) -> list[dict]:
    """Expanded ``extra_units`` entries, one dict per requested unit.

    The old ``{id-or-name: count}`` form stays valid.  The advanced form is a
    list of dicts:
        {id, count, magic_paths, as_commander}
    ``magic_paths`` is an object keyed by path letter (``{"F": 1, "W": 2}``,
    letters F A W E S D N G B H, missing letters are 0) and is valid only on
    commanders.  ``as_commander`` (true/"cmdr" or
    false/"troop"/"unit") explicitly overrides auto-detection; otherwise the
    Inspector's categories decide (nation leader/troop lists, hero list, then
    magic paths for summons -- see ``_unit_role``), with ``magic_paths`` as an
    implicit commander marker.
    """
    if not entry:
        return []
    items = []
    if isinstance(entry, dict):
        for key, count in entry.items():
            items.append((str(key), {'id': key, 'count': count}))
    else:
        for i, item in enumerate(entry):
            if not isinstance(item, dict):
                raise ValueError(f'extra_units entry {i} must be an object')
            items.append((f'entry {i}', item))

    specs: list[dict] = []
    for label, item in items:
        uid = _unit_id(item.get('id'))
        unit = gamedata.units().get(uid)
        if unit is None:
            raise ValueError(f'unknown unit id in extra_units {label}: {uid}')
        count = int(item.get('count', 1))
        if count < 1:
            raise ValueError(f'extra_units {label} count must be at least 1')
        if unit.unique and count > 1:
            raise ValueError(
                f'extra_units {label}: unit {uid} ({unit.name}) is unique'
                f'{" (fixed name " + unit.fixedname + ")" if unit.fixedname else ""}'
                f'; the engine keeps only one copy, so count must be 1')
        if uid in gamedata.pretender_chassis():
            raise ValueError(
                f'extra_units {label}: unit {uid} ({unit.name}) is a '
                'pretender chassis; the engine silently removes god-class '
                'units that are not a nation\'s god, so it cannot be added '
                'as an extra unit (set it as the side\'s pretender instead)')
        paths = item.get('magic_paths')
        if paths is not None:
            paths = _paths_from_config(paths, f'extra_units {label}')
        cmdr = item.get('as_commander')
        if cmdr is not None:
            if isinstance(cmdr, str):
                cmdr = cmdr.lower() in ('true', 'cmdr', 'commander', 'yes', '1')
            else:
                cmdr = bool(cmdr)
            if cmdr is False and paths is not None:
                raise ValueError(
                    f'extra_units {label}: magic_paths requires '
                    'as_commander=true')
        for _ in range(count):
            specs.append({'id': uid, 'paths': paths, 'label': label,
                          'cmdr_override': cmdr})
    return specs


def _custom_units(entry) -> list[int]:
    return [spec['id'] for spec in _custom_unit_specs(entry)]


def _has_commander_stats(unit) -> bool:
    """True when units.csv gives the unit commander-only attributes.

    This is the Inspector's own fallback for the types it cannot classify by
    nation list (MUnit.prepareData_PostSiteData): a unit that is in none of
    its nation's lists becomes a ``Commander`` only when it has magic paths,
    and a plain ``Unit`` otherwise.  That is what separates summons -- a
    summoned mage is a commander, a summoned troop is not.  The leadership
    columns are useless here: ``leader`` repeats the same default 50 for every
    troop, and magic/undead leadership is carried by summoned troops too
    (Kithaironic Lion and Watcher read magic leadership 10 and are ordinary
    army units).  A fixed name or the unique flag marks heroes, which the
    nation's hero list already covers (``gamedata.unit_type_role``), so those
    do not need to decide anything here.
    """
    return bool(any(unit.paths) or unit.startdom or unit.pathcost)


def _unit_role(unit_id: int) -> str:
    """Classify a unit id as ``'pretender'``, ``'cmdr'`` or ``'unit'``.

    The type comes from the Dom6 Inspector's categories, resolved by id alone
    (``gamedata.unit_type_role``): a pretender chassis is a god, an id that
    some nation recruits as a commander (or as a hero, attributes 139..149) is
    a commander, an id that some nation recruits as a troop is a troop.  A
    nation lookup cannot be used here: a scout report never names the army's
    nation and the arena enemy nation is picked at random, so the copied units
    are typed by what their id is.  The union of all commander lists and the
    union of all troop lists are disjoint, so the id alone decides.  The
    export leaves summons, mercenaries and mod units out of every list, so
    those fall back to the commander-only columns of units.csv (magic paths --
    ``_has_commander_stats``), exactly like the Inspector's "Summoned"
    category, which is split into commanders and units the same way.  A god
    chassis gets its own role: the callers decide what to do with it (the
    scout report turns it into the enemy pretender).
    """
    role = gamedata.unit_type_role(unit_id)
    if role is not None:
        return role
    unit = gamedata.units()[unit_id]
    return 'cmdr' if _has_commander_stats(unit) else 'unit'


def _custom_commanders(specs: list[dict]) -> list[dict]:
    """Commanders among expanded extra-unit specs, with final paths.

    The commander test is the Inspector's, by unit id (``_unit_role``);
    supplying ``magic_paths`` is still an explicit marker for a unit whose
    columns are empty.
    """
    commanders: list[dict] = []
    for i, spec in enumerate(specs):
        unit = gamedata.units()[spec['id']]
        paths = spec['paths']
        cmdr_override = spec.get('cmdr_override')
        if cmdr_override is not None:
            if not cmdr_override:
                continue
        elif not (paths is not None or _unit_role(unit.id) == 'cmdr'):
            continue
        commanders.append({**spec, 'index': i, 'name': unit.name,
                           'paths': unit.paths if paths is None else paths})
    return commanders


def _path_text(paths: tuple[int, ...]) -> str:
    used = [f'{letter}{level}' for letter, level in zip(PATH_LETTERS, paths)
            if level]
    return ' '.join(used) if used else 'none'


# --------------------------------------------------------------------------
# arena side
# --------------------------------------------------------------------------
def _nation_provinces(game: str, nation: int) -> list[int]:
    map_path = config.maps_dir() / game / f'{game}.map'
    if not map_path.exists():
        return []
    found = []
    for line in map_path.read_text(encoding='utf-8', errors='ignore').splitlines():
        parts = line.split()
        if len(parts) < 3:
            continue
        # #specstart <nation> <province>
        if parts[0] == '#specstart' and int(parts[1]) == nation:
            found.append(int(parts[2]))
        # #owner <province> <nation>
        elif parts[0] == '#owner' and int(parts[2]) == nation:
            found.append(int(parts[1]))
    # de-duplicate while preserving order
    seen = set()
    unique = []
    for p in found:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique


def _first_record(raw: bytes, base: int, count: int, nation: int) -> int | None:
    for k in range(count):
        off = base + k * STRIDE
        if struct.unpack_from('<H', raw, off + 64)[0] == nation:
            return off
    return None


def _god_file_for(nation: gamedata.Nation) -> Path:
    """Return a placeholder god file the engine accepts for ``nation``.

    The arena is created before the source save's design is transplanted, so
    ``--newgame`` needs a pretender submission for both human nations.  A
    fixed placeholder shipped with the project is relabeled to ``nation`` and
    written under ``output/``; the user's ``savedgames/newlords`` is never
    read or written.  ``newgame.create`` repairs the checksum on its first
    run, after which the existing file is reused as-is.
    """
    out = config.ensure_output_dir() / f'{nation.file_name_base}_placeholder.2h'
    if out.exists():
        data = out.read_bytes()
        if struct.unpack_from('<H', data, 26)[0] == nation.id:
            return out
    source = config.PROJECT_ROOT / 'resources' / 'pretender_placeholder.2h'
    if not source.is_file():
        raise FileNotFoundError(
            f'placeholder god file {source} is missing; it ships with the '
            f'project and is required to create the arena'
        )
    newgame.forge_god_file(source, nation.id, out)
    print(f'  placeholder god file for {nation.name} written to output/{out.name}')
    return out


def _select_enemy_nation(own: gamedata.Nation, seed: int,
                         explicit: int = 0) -> gamedata.Nation:
    """Pick the enemy nation: ``explicit`` from the config, else random.

    No era setting is needed: a nation id already implies its era, and a
    random enemy is drawn from ``own``'s era.  Every nation is eligible: the
    arena's placeholder god file supplies the pretender the engine needs at
    creation, so no ``savedgames/newlords`` entry is required.
    """
    if explicit:
        nation = gamedata.nations().get(explicit)
        if nation is None:
            raise ValueError(f'unknown enemy nation id {explicit}')
        return nation
    candidates = [
        n for n in gamedata.nations().values()
        if n.era == own.era and n.id != own.id
    ]
    if not candidates:
        raise ValueError(f'no enemy nation available in era {own.era} '
                         f'(own nation is {own.id})')
    return random.Random(seed).choice(candidates)


def _copy_fixed_map(game: str, map_name: str) -> Path:
    """Stage the user supplied map under ``game``'s map folder.

    Dominions looks maps up by file name, so the source folder
    ``maps/<map_name>/`` is copied as ``maps/<game>/``: every file whose
    name starts with the map name is renamed to the game name and the
    ``#imagefile`` reference inside each ``.map`` is retargeted.  Nothing
    is generated and no province is rewritten: the map is used as authored.
    """
    src = config.maps_dir() / map_name
    if not (src / f'{map_name}.map').is_file():
        raise ValueError(
            f'fixed map "{map_name}.map" not found in {src}; put the map folder '
            f'under {config.maps_dir()} or set arena.map to its name'
        )
    dst = config.maps_dir() / game
    dst.mkdir(parents=True, exist_ok=True)
    for path in sorted(src.iterdir()):
        if not path.is_file():
            continue
        name = path.name
        if name.startswith(map_name):
            name = game + name[len(map_name):]
        target = dst / name
        if path.suffix.lower() != '.map':
            shutil.copyfile(path, target)
            continue
        lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
        for i, line in enumerate(lines):
            parts = line.split(None, 1)
            if len(parts) == 2 and parts[0] == '#imagefile':
                lines[i] = f'{parts[0]} {parts[1].replace(map_name, game, 1)}'
        target.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return dst / f'{game}.map'


def _apply_starts(mp: Path, starts: list[tuple[int, int]],
                  cave_count: int) -> dict[int, int]:
    """Pin each nation to its start province on a staged map.

    ``starts`` is ``[(nation id, province id)]``.  A surface province only
    accepts a capital when its terrain mask has no nostart bit (512), so the
    surface start provinces get the bit cleared and every other surface
    province gets it set.  A ``#scenario`` block declares both nations as human
    players with ``#allowedplayer``, gives EVERY surface province an ``#owner``
    (nearest specstart in the neighbour graph), and declares them enemies with
    ``#startwar``.  The block is inserted before ``#neighbour``, matching the
    engine contract.

    An underground start is addressed as ``surface_max + cave_local``: the
    engine numbers plane 2 right after the surface.  ``cave_count`` is the
    number of provinces the map's ``_plane2.map`` declares, used to bound
    that id.  The engine ignores the authored cave layer and generates its
    own at creation, but the generated provinces are all startable and keep
    that numbering, so the ``#specstart`` is honoured -- as long as the spare
    surface provinces below keep the engine's player count check happy.

    Returns the computed province ownership dict for later use in fixing
    ftherlnd's binary owner table.
    """
    from collections import deque

    wanted = dict(starts)
    nations = list(wanted.keys())
    surface: set[int] = set()
    terrain_at: dict[int, int] = {}
    body: list[str] = []
    for line in mp.read_text(encoding='utf-8', errors='replace').splitlines():
        parts = line.split()
        head = parts[0] if parts else ''
        if head == '#terrain' and len(parts) >= 3:
            prov = int(parts[1])
            surface.add(prov)
            terrain_at[prov] = len(body)
        elif head in ('#specstart', '#scenario', '#allowedplayer',
                       '#startwar', '#victorycondition', '#owner'):
            continue
        body.append(line)
    highest = max(surface) if surface else 0
    surface_starts = {p for _, p in starts if p <= highest}
    missing = surface_starts - surface
    if missing:
        raise ValueError(
            f'start province(s) {sorted(missing)} are not declared by '
            f'{mp.name} (which defines 1..{highest}); fix start_province in '
            f'the config'
        )
    for _, prov in starts:
        if prov > highest and prov - highest > cave_count:
            raise ValueError(
                f'start province {prov} is underground, but the map has only '
                f'{cave_count} cave province(s) ({highest + 1}..'
                f'{highest + cave_count}); fix start_province in the config'
            )
    # The engine counts "max land players" on the surface plane only, even for
    # a nation whose capital is underground.  Marking every other surface
    # province nonstartable therefore left the count at 1 and creation aborted
    # with "Number of players (2 0) exceeding max value for map (1 0)".
    # Enough spare surface provinces stay startable to seat every player; the
    # pinned #specstart still decides where each nation actually appears.
    spare = max(0, len(starts) - len(surface_starts))
    for prov in sorted(terrain_at):
        mask = int(body[terrain_at[prov]].split()[2])
        if prov in surface_starts:
            mask &= ~512
        elif spare:
            mask &= ~512
            spare -= 1
        else:
            mask |= 512
        body[terrain_at[prov]] = f'#terrain {prov} {mask}'
    # Build neighbour graph to assign owners to every province.
    edges: dict[int, set[int]] = {}
    for line in body:
        parts = line.split()
        if len(parts) >= 3 and parts[0] == '#neighbour':
            a, b = int(parts[1]), int(parts[2])
            edges.setdefault(a, set()).add(b)
            edges.setdefault(b, set()).add(a)
    nodes = sorted(edges)
    # BFS from each specstart nation to find the nearest owner for every
    # province; provinces equidistant go to the earlier nation.
    nearest: dict[int, tuple[int, int]] = {}  # prov -> (dist, nation)
    for nat, anchor in starts:
        dist = {anchor: 0}
        queue = deque([anchor])
        while queue:
            cur = queue.popleft()
            for nxt in edges.get(cur, ()):
                if nxt not in dist:
                    dist[nxt] = dist[cur] + 1
                    queue.append(nxt)
        for node, d in dist.items():
            if node not in nearest or d < nearest[node][0]:
                nearest[node] = (d, nat)
    scenario = [
        '#scenario',
        '#victorycondition 0',
    ]
    for nat in nations:
        scenario.append(f'#allowedplayer {nat}')
    for nat, prov in starts:
        scenario.append(f'#specstart {nat} {prov}')
    for node in nodes:
        _, owner = nearest.get(node, (99, nations[0]))
        scenario.append(f'#owner {node} {owner}')
    if len(nations) >= 2:
        scenario.append(f'#startwar {nations[0]} {nations[1]}')
    # Insert before the first #neighbour line — Dominions' contract.
    insert_at = next((i for i, l in enumerate(body)
                      if l.startswith('#neighbour')), len(body))
    body[insert_at:insert_at] = scenario
    mp.write_text('\n'.join(body) + '\n', encoding='utf-8')

    return {node: nearest.get(node, (99, nations[0]))[1] for node in nodes}


def _cave_count(plane2: Path) -> int:
    """Provinces the map's ``_plane2.map`` declares.

    The engine does not use that file as authored (see ``_apply_starts``);
    it generates the cave layer at creation, but the file still defines how
    many underground provinces the map is meant to have, which is what a
    ``start_province`` is validated against.
    """
    lines = plane2.read_text(encoding='utf-8', errors='replace').splitlines()
    count = 0
    for line in lines:
        parts = line.split()
        if len(parts) >= 3 and parts[0] == '#terrain':
            count += 1
    return count


def _enabled_mods() -> list[str]:
    """The ``.dm`` files of the engine's most recent run, in load order.

    ``log.txt`` accumulates every launch, so only the last contiguous block of
    ``Enabledmod`` lines (the engine prints one per mod it loaded) counts.
    """
    path = config.log_path()
    if not path.exists():
        return []
    enabled: list[str] = []
    current: list[str] = []
    for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
        parts = line.split()
        if parts[:1] == ['Enabledmod'] and len(parts) > 1:
            current.append(parts[1])
        elif current:
            enabled, current = current, []
    if current:
        enabled = current
    return enabled


def _check_mods(mods: list[str]) -> None:
    """Fail when the created game did not load exactly the configured mods.

    ``mods`` is the config's list (``dir/file.dm`` entries); the engine reads
    the same entries through ``-M`` and echoes each one it actually enabled.
    A wrong name or a broken folder makes the engine skip that mod silently,
    which would build the arena with units and nations the config does not
    name, so the two lists are compared verbatim.
    """
    expected = [Path(mod).name for mod in mods]
    enabled = _enabled_mods()
    if enabled != expected:
        raise ValueError(
            f'the game enabled mods {enabled}, config asks for {expected}; '
            f'check the "mods" entries in the config')


# Vanilla nations that start under water (the one-age mods keep the ids).
_SEA_NATIONS = {40, 41, 42, 43, 44, 85, 86, 87, 88, 89, 127}


def _check_start_terrain(map_path: Path,
                         starts: list[tuple[gamedata.Nation, int, str]]) -> None:
    """Fail early when a start province's sea/land terrain does not fit the
    nation placed on it.

    The engine silently drops a ``#specstart`` that violates this (a land
    nation on a sea province or the reverse) and then aborts with the
    cryptic "Number of players (2 0) exceeding max value for map (1 1)".
    Plane-2 (underground) provinces are not checked: they use their own
    numbering in the separate plane2 file, and a land nation may start
    underground anyway.
    """
    terrain: dict[int, int] = {}
    for line in map_path.read_text(
            encoding='utf-8', errors='replace').splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0] == '#terrain':
            terrain[int(parts[1])] = int(parts[2])
    for nation, prov, side in starts:
        mask = terrain.get(prov)
        if mask is None:  # plane-2 province, not covered here
            continue
        if mask & 4 and nation.id not in _SEA_NATIONS:
            raise ValueError(
                f'{side} start province {prov} is a sea province, but '
                f'{nation.id} ({nation.name}) is a land nation: fix the '
                f'{side} start_province in the config')
        if not mask & 4 and nation.id in _SEA_NATIONS:
            raise ValueError(
                f'{side} start province {prov} is a land province, but '
                f'{nation.id} ({nation.name}) is a water nation: fix the '
                f'{side} start_province in the config')


def _ensure_arena(game: str, era: int, player_nation: gamedata.Nation,
                  enemy_nation: gamedata.Nation, mods: list[str],
                  map_name: str, player_start: int, enemy_start: int,
                  recreate: bool = False, indepstr: int = 0) -> None:
    """Create the arena game with both nations as human players.

    The map is a fixed, hand made one: ``arena.map`` names a folder under
    ``maps/`` and is copied under the game name as-is, except that the capitals
    from ``player_start`` / ``enemy_start`` are pinned and every other surface
    province is made nonstartable (minus the few spare ones the engine's player
    count check needs when a capital is underground).  ``recreate`` discards
    the existing save and the staged copy first, so a changed source map is
    picked up.
    """
    if not map_name:
        raise ValueError(
            'arena.map is empty: set it to the folder name of the fixed map '
            'you authored under the maps directory'
        )
    source = config.maps_dir() / map_name / f'{map_name}.map'
    if not source.is_file():
        raise ValueError(
            f'fixed map "{map_name}.map" not found in {source.parent}; put the '
            f'map folder under {config.maps_dir()} or fix arena.map'
        )
    save = config.save_dir(game)
    staged = config.maps_dir() / game
    if recreate:
        if save.exists():
            shutil.rmtree(save)
            print(f'arena {game} discarded for recreation')
        if staged.exists():
            shutil.rmtree(staged)
            print(f'map {staged.name} discarded for recreation')
    staged_map = staged / f'{game}.map'
    if not staged_map.exists():
        _copy_fixed_map(game, map_name)
        print(f'map {game}: copied from fixed map {map_name} '
              f'(starts {player_start} / {enemy_start})')
    plane2 = staged / f'{game}_plane2.map'
    cave_count = _cave_count(plane2) if plane2.exists() else 0
    _apply_starts(staged_map,
                  [(player_nation.id, player_start),
                   (enemy_nation.id, enemy_start)],
                  cave_count)
    _check_start_terrain(staged / f'{game}.map',
                         [(player_nation, player_start, 'player'),
                          (enemy_nation, enemy_start, 'enemy')])
    if (save / 'ftherlnd').exists():
        print(f'arena {game} already exists, reusing ftherlnd')
        return
    print(f'creating arena {game} ({player_nation.name} vs {enemy_nation.name})')
    # newgame.create always passes --conqall (win by eliminating all opponents
    # only).  Without it the map (which has no thrones) makes the game end in
    # a "Horrors" victory the first time a pretender dies.
    # --indepstr: the arena always ends up with independent strength 0 (every
    # independent garrison is deleted after creation, see
    # _clear_independents).  The flag is only a unit-table size lever: the
    # table is fixed at creation and the random independent garrisons are
    # most of it, so a table too small for both armies is retried with a
    # higher value (see main) purely to allocate more records.
    # --research 0: Very easy research, so Construction 1 completes quickly.
    newgame.create(game, era,
                   [(player_nation, _god_file_for(player_nation)),
                    (enemy_nation, _god_file_for(enemy_nation))],
                   mods=mods, indepstr=indepstr,
                   extra_flags=['--eventrarity', '2', '--research', '0'])
    _check_mods(mods)
    if mods:
        print(f'  mods loaded as configured: {[Path(m).name for m in mods]}')


def _player_trn(save_dir: Path, nation: int) -> tuple[Path, bytes]:
    """The player's own .trn, with graceful fallback.

    Primary rule: look up the nation's ``file_name_base`` in gamedata
    (``nations()[nation].file_name_base + '.trn'``; e.g. nation 104 ->
    ``late_abysia.trn``) and open that exact file.

    Fallback (PBEM / hotseat saves where the player's own turn is not
    stored under its canonical name, or mod nations that gamedata does not
    know about): scan every ``*.trn`` in the save folder and pick the one
    whose unit records carry the most entries for ``nation``.  A folder
    with a single .trn is unambiguous and always accepted.  A folder with
    several .trn where none contains any unit of the target nation raises
    ``FileNotFoundError`` — the caller genuinely has no data to copy.

    The orders file (``.2h``) is derived from the selected .trn stem by
    the caller, so it is covered as well.
    """
    # -- 1. Try the canonical file_name_base from gamedata ----------------
    nations = gamedata.nations()
    if nation in nations:
        base = nations[nation].file_name_base
        exact = save_dir / f'{base}.trn'
        if exact.is_file():
            return exact, exact.read_bytes()

    # -- 2. Fallback: scan all .trn, pick the one with most target-nation units
    trn_candidates = sorted(save_dir.glob('*.trn'))
    if not trn_candidates:
        raise FileNotFoundError(
            f'no .trn files found in {save_dir}; cannot read nation '
            f'{nation}\'s army')

    if len(trn_candidates) == 1:
        chosen = trn_candidates[0]
        return chosen, chosen.read_bytes()

    ranked: list[tuple[int, Path]] = []
    for trn_path in trn_candidates:
        try:
            raw = trn_path.read_bytes()
            recs = trn_parse.unit_records(raw)
            count = sum(1 for r in recs if r['nation'] == nation)
        except Exception:
            count = 0
        ranked.append((count, trn_path))

    ranked.sort(key=lambda x: -x[0])
    best_count, best_path = ranked[0]
    if best_count == 0:
        raise FileNotFoundError(
            f'no .trn in {save_dir} contains units of nation {nation} '
            f'(scanned {len(trn_candidates)} files: '
            f'{", ".join(p.name for p in trn_candidates)})')
    # Warn if the fallback picked a non-canonical file
    if nation in nations:
        canonical = save_dir / f'{nations[nation].file_name_base}.trn'
        if best_path != canonical:
            import sys as _sys
            print(f'  WARNING: canonical {canonical.name!r} missing; '
                  f'falling back to {best_path.name!r} '
                  f'({best_count} units match)', file=_sys.stderr)
    return best_path, best_path.read_bytes()


def _vcr_unit_type(raw: bytes, uid: int, lo: int, hi: int,
                   nations: tuple[int, ...] | None = None) -> int | None:
    """Unit type of a battle participant, read from its VCR snapshot record.

    A commander of the copied side usually has no record in the player's .trn
    unit table (only the player's own units and visible enemies are listed).
    The VCR carries its own 173-byte snapshot: uid at ``q``, squad at
    ``q + 28`` (``-1`` for a commander), type at ``q + 32``, province at
    ``q + 36`` and nation at ``q + 64``.  These are four bytes earlier than
    the .trn record layout -- reading ``q + 36`` as the type silently matched
    province ids and returned None for every commander, which dropped all of
    them into the "unknown type" spare pool and handed each one a random
    other commander's com record.

    This type is what aligns a VCR com record (name, magic paths, equipment)
    with the right unit slot.
    """
    pat = struct.pack('<I', uid)
    q = raw.find(pat, lo, hi)
    while q >= 0:
        if q + 68 > len(raw):
            return None
        typ = struct.unpack_from('<H', raw, q + 32)[0]
        prov = struct.unpack_from('<H', raw, q + 36)[0]
        nat = struct.unpack_from('<H', raw, q + 64)[0]
        if (typ in gamedata.units()
                and 1 <= prov <= trn_parse.province_max()
                and (nations is None or nat in nations)
                and raw[q + 28:q + 32] == b'\xff\xff\xff\xff'):
            return typ
        q = raw.find(pat, q + 1, hi)
    return None


def _battle_com_candidates(raw: bytes, rep: dict) -> list[dict]:
    """Commander records carried in a report's VCR block.

    A battle casualty has no 173-byte unit record, but the VCR still carries
    its complete com record (name, squads, orders and equipment) next to the
    surviving commanders.  The whole ``[vcr, bcd)`` segment is searched: on a
    big battle the block is far larger than the 8 KiB window that used to be
    scanned before the BCD head (province 61: 201 records spread over ~45 KiB),
    and a narrow window left most commanders without a com record -- the host
    then treated them as plain soldiers.

    A strict pass accepts only names that look like a word (upper case then
    lower case).  A few records in a real save carry a placeholder name in
    lower case ("redmage") or with a space ("sss lock"); a second, relaxed
    pass fills in the uids still missing, guarded by a valid comid and a
    well-formed tail (magic paths 0..15) so unrelated text cannot qualify.
    """
    start = rep['vcr'] + 7
    end = rep['bcd']
    nations = (rep['attacker'], rep['defender'])

    def scan(relaxed: bool) -> dict[int, dict]:
        found: dict[int, dict] = {}
        i = raw.find(b'\x4f', start, end - 4)
        while i >= 0:
            uidpos = i + 1
            uid = struct.unpack_from('<I', raw, uidpos)[0]
            slots = struct.unpack_from('<5I', raw, uidpos + 4)
            if (1 <= uid < 1_000_000
                    and all(s == 0xFFFFFFFF or s < 10_000_000
                            for s in slots)
                    and uidpos + COM_BODY <= end):
                # Find the nearest plausible start of the XOR-encoded name.
                # In particular, do not call _trn_commander(uid): that
                # returns the last record for the uid elsewhere in the .trn
                # and misses this VCR-local record (which is the one carrying
                # battle-time equipment).
                name_start = None
                name = ''
                for p in range(i - 1, max(start, i - 64), -1):
                    if p < 4:
                        continue
                    decoded = bytes(b ^ XOR for b in raw[p:i]).decode('latin1')
                    comid = struct.unpack_from('<I', raw, p - 4)[0]
                    if not (len(decoded) >= 2 and decoded.isprintable()
                            and comid < 100_000):
                        continue
                    if relaxed:
                        # Reject zero padding (0x00 decodes to "O") and the
                        # 0xFF padding of an unrelated block (0xFF decodes to
                        # "°"): a real placeholder name is plain ASCII and
                        # sits behind a non-zero comid.
                        if (raw[p] == 0 or comid == 0
                                or not all(32 <= ord(ch) < 127
                                           for ch in decoded)):
                            continue
                    elif not (decoded[0].isupper() and decoded[1].islower()):
                        continue
                    name_start = p
                    name = decoded
                    break
                if name_start is not None and name_start - 4 >= start:
                    record_start = name_start - 4
                    tail = raw[uidpos + 24:uidpos + 24 + 181]
                    if len(tail) == 181 and not (
                            relaxed
                            and any(tail[130 + k] > 15 for k in range(10))):
                        found[uid] = {
                            'start': record_start,
                            'end': uidpos + COM_BODY,
                            'comid': struct.unpack_from(
                                '<I', raw, record_start)[0],
                            'name': name,
                            'uid': uid,
                            'squads': [s for s in slots
                                       if s != 0xFFFFFFFF],
                            'tail': tail,
                            'type': _vcr_unit_type(raw, uid, rep['vcr'],
                                                   end, nations),
                        }
            i = raw.find(b'\x4f', i + 1, end - 4)
        return found

    found = scan(False)
    for uid, candidate in scan(True).items():
        found.setdefault(uid, candidate)
    return sorted(found.values(), key=lambda c: c['start'])


_NEUTRAL_ALIASES = frozenset({
    'neutral', 'neutrals', 'indie', 'indies', 'independent', 'independents',
    '中立', '中立方', '中立国',
})


def _side_nation(value, field: str, province: int) -> int:
    """Resolve a battle_report ``attacker``/``defender`` value to a nation id.

    The .trn stores the numeric nation id (independents/neutral provinces are
    nation 0), but writing ``0`` in the config is not self-explanatory, so the
    symbolic aliases above are also accepted, as is a unique nation name from
    nations.csv (e.g. ``"Independents"``).  Everything else is a hard error.
    """
    if isinstance(value, bool):
        raise ValueError(
            f'battle report at province {province}: "{field}" {value!r} is '
            f'not a nation id')
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        text = value.strip()
        try:
            return int(text)
        except ValueError:
            pass
        if text.lower() in _NEUTRAL_ALIASES:
            return 0
        matches = [n.id for n in gamedata.nations().values()
                   if n.name.lower() == text.lower()]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise ValueError(
                f'battle report at province {province}: "{field}" {value!r} '
                f'matches several nations {matches}; use the nation id')
    raise ValueError(
        f'battle report at province {province}: "{field}" must be a nation '
        f'id, a unique nation name, or a neutral alias '
        f'{sorted(_NEUTRAL_ALIASES)}; got {value!r}')


def _nation_text(nation: int) -> str:
    """``id (name)`` for an error/log label; neutral shows as Independents."""
    nat = gamedata.nations().get(nation)
    return f'{nation} ({nat.name})' if nat else str(nation)


def _report_details(raw: bytes, entries, side: str) -> tuple[list[int], list[dict | None]]:
    """Units taken from ``battle_report`` entries, plus visible unit records.

    The BCD block is the only source for a wiped-out side.  When the copied
    side is still present in the province, however, its 173-byte unit records
    carry the uids needed to transplant commander names, squads and equipment;
    some reports (for example a defender that held the province) omit that
    side from the BCD block entirely, so visible records are also the fallback
    for an empty BCD side.

    ``timing`` picks which BCD list is copied: ``'before'`` (default) is the
    army at battle start, ``'after'`` only the units left when the battle
    ended.  A side whose whole army died has an empty ``'after'`` list, and
    that is copied as-is -- falling back to the visible records would bring
    the dead units back.
    """
    if isinstance(entries, dict):  # legacy single-object form
        entries = [entries]

    def _label(i: int, rep: dict) -> str:
        return (f'seq {i}: defender {_nation_text(rep["defender"])} vs '
                f'attacker {_nation_text(rep["attacker"])} '
                f'(cstlmode {rep["cstlmode"]}, seed {rep["seed"]})')

    units: list[int] = []
    detailed: list[dict | None] = []
    for br in entries:
        prov = int(br['province'])
        reports = trn_parse.battle_reports(raw, prov)
        if not reports:
            raise ValueError(f'no battle report at province {prov}')
        cand = list(enumerate(reports))
        want_attacker = (_side_nation(br['attacker'], 'attacker', prov)
                         if 'attacker' in br else None)
        want_defender = (_side_nation(br['defender'], 'defender', prov)
                         if 'defender' in br else None)
        if want_attacker is not None or want_defender is not None:
            cand = [(i, r) for i, r in cand
                    if (want_attacker is None or r['attacker'] == want_attacker)
                    and (want_defender is None or r['defender'] == want_defender)]
            if not cand:
                raise ValueError(
                    f'no battle report at province {prov} with attacker '
                    f'{want_attacker if want_attacker is not None else "any"} '
                    f'/ defender '
                    f'{want_defender if want_defender is not None else "any"}; '
                    f'in file: '
                    + '; '.join(_label(i, r) for i, r in enumerate(reports)))
        if 'seq' in br:
            seq = int(br['seq'])
            picked = [(i, r) for i, r in cand if i == seq]
            if not picked:
                raise ValueError(
                    f'no battle report seq {seq} at province {prov} '
                    f'({len(reports)} in file): '
                    + '; '.join(_label(i, r) for i, r in enumerate(reports)))
            cand = picked
        if len(cand) > 1:
            raise ValueError(
                f'{len(cand)} battle reports at province {prov} match; '
                'add "attacker"/"defender" (or "seq") to pick one: '
                + '; '.join(_label(i, r) for i, r in enumerate(reports)))
        seq, rep = cand[0]
        copy = br.get('copy')
        if copy not in ('attacker', 'defender'):
            raise ValueError(
                f'battle report at province {prov}: "copy" must be '
                f'"attacker" or "defender", got {copy!r} '
                f'({_label(seq, rep)})')
        side_nat = rep[copy]
        phase = br.get('timing', 'before')
        if isinstance(phase, dict):        # per nation, as _pick_battle_reports
            phase = phase.get(side_nat, 'before')
        if phase not in ('before', 'after'):
            raise ValueError(
                f'battle report at province {prov}: "timing" must be '
                f'"before" or "after", got {phase!r}')
        army = rep['end' if phase == 'after' else 'start'][side_nat]
        # Distinguishes "the BCD block lists no such side at all" (fall back to
        # the visible records) from "every unit of that side died" (copy
        # nothing when the survivors are wanted).
        has_bcd = bool(rep['start'][side_nat] or rep['end'][side_nat])
        side_records = [r for r in trn_parse.unit_records(raw)
                        if r['province'] == prov and r['nation'] == side_nat]
        cmdr_table = rep['end_commanders' if phase == 'after'
                          else 'start_commanders']
        if army:
            picked_units = []
            by_type: dict[int, list[dict]] = {}
            for record in side_records:
                by_type.setdefault(record['type'], []).append(record)

            # Select the com records by the SIDE each belongs to, read from the
            # VCR snapshot (uid -> nation), never by a positional slice.  The
            # candidate list is ordered by byte position, which is
            # attacker-first in this save, so the old "defender-first" offset
            # grabbed the other side's commanders -- that is exactly why
            # Meliath (the attacker's commander) got no com at all.
            side_uids = set(_scan_vcr_snapshots(raw, rep['vcr'], rep['bcd'],
                                                side_nat))
            candidates = [c for c in _battle_com_candidates(raw, rep)
                          if c['uid'] in side_uids]
            if not candidates:
                # No usable snapshot block: keep the old positional split so
                # behaviour is unchanged for older reports.
                def_cmdrs = sum(
                    cmdr_table[rep['defender']].values())
                side_cmdrs = sum(
                    cmdr_table[side_nat].values())
                first = 0 if side_nat == rep['defender'] else def_cmdrs
                candidates = _battle_com_candidates(
                    raw, rep)[first:first + side_cmdrs]

            # A com record is aligned to a unit slot by unit TYPE, read from
            # the VCR snapshot of that uid.  "No unit record in this province"
            # does NOT mean "dead": the player's .trn only lists the player's
            # own units plus enemies it can see, so every commander of the
            # copied side is normally absent here even when it survived the
            # battle (province 253: Nergash and Fritjof both lived).  Never
            # hand a com record to a commander of another type: it carries
            # that commander's name, magic paths and equipment.
            used_uids = {r['uid'] for recs in by_type.values() for r in recs}
            spare_by_type: dict[int | None, list[dict]] = {}
            for c in candidates:
                if c['uid'] not in used_uids:
                    spare_by_type.setdefault(c.get('type'), []).append(c)
            commander_types = cmdr_table[side_nat]

            segment = raw[rep['vcr']:rep['bcd']]
            # VCR snapshot block: uid → {type, squad, province} for EVERY
            # unit of side_nat that fought this battle, including ones the
            # player cannot see (no .trn record).  We use it to fill the
            # missing slots of invisible troops that would otherwise land
            # as bare None entries and lose their unit identity AND their
            # squad attachment when the formation is assembled below.
            vcr_snaps = _scan_vcr_snapshots(raw, rep['vcr'], rep['bcd'],
                                            side_nat)
            vcr_by_type: dict[int, list[int]] = {}
            for uid, info in vcr_snaps.items():
                vcr_by_type.setdefault(info['type'], []).append(uid)
            vcr_used: set[int] = set()
            for t, count in army.items():
                picked_units += [t] * count
                candidates_for_type = by_type.get(t, [])
                if side == 'own' and vcr_snaps:
                    # Every own unit is visible, but the raw byte search can
                    # also match a uid that merely occurs elsewhere in the
                    # segment.  Trust the snapshot set so the exact unit that
                    # fought (e.g. "Meliath") is picked, not a same-type one.
                    mentioned = [r for r in candidates_for_type
                                 if r['uid'] in vcr_snaps]
                else:
                    mentioned = [r for r in candidates_for_type
                                 if struct.pack('<I', r['uid']) in segment]
                visible = mentioned or candidates_for_type
                picked = visible[:count]
                detailed += picked
                for r in picked:
                    vcr_used.add(r['uid'])
                missing = count - len(picked)
                for _ in range(missing):
                    # Troops, and own-side commanders, are filled from the VCR
                    # snapshot block first: the snapshot carries the exact uid
                    # that fought, so a commander keeps its own com record
                    # (name, equipment, script) instead of a same-type one.
                    # A common commander type (e.g. Fortune Teller) has many
                    # instances, and type-only pairing attached "Meliath"'s com
                    # to a different slot once the province's own records were
                    # no longer copied.  Enemy commanders keep the spare-com
                    # path: they are not visible in the .trn, so the VCR com
                    # block is their only source.
                    pool = [u for u in vcr_by_type.get(t, [])
                            if u not in vcr_used]
                    if pool and (t not in commander_types or side == 'own'):
                        uid = pool.pop(0)
                        vcr_used.add(uid)
                        detailed.append({
                            'uid': uid, 'type': t, 'province': prov,
                            'nation': side_nat, 'pos': None,
                            'hp': vcr_snaps[uid]['hp']})
                        continue
                    if t in commander_types:
                        com = _take_spare_commander(spare_by_type, t)
                        if com is None:
                            print(f'  NOTE: {_label(seq, rep)}: no com record '
                                  f'of type {t} '
                                  f'({gamedata.units()[t].name}) left to align '
                                  f'with this commander; its name and '
                                  f'equipment are not copied')
                            detailed.append(None)
                            continue
                        detailed.append({
                            'uid': com['uid'], 'type': t, 'province': prov,
                            'nation': side_nat, 'pos': None, 'com': com})
                        vcr_used.add(com['uid'])
                    else:
                        detailed.append(None)
        elif phase == 'after' and has_bcd:
            # The side fought but has no survivors: copying the visible
            # records here would reintroduce units the battle killed.
            picked_units = []
            print(f'  {side} battle report {prov} [{_label(seq, rep)}]: '
                  f'no {copy} {_nation_text(side_nat)} unit survived the '
                  f'battle, nothing copied')
        else:
            picked_units = [r['type'] for r in side_records]
            detailed += side_records
            print(f'  battle report block has no {copy} entries; using '
                  f'{len(side_records)} visible .trn record(s)')
        local_com = {c['uid']: c for c in _battle_com_candidates(raw, rep)}
        for i, record in enumerate(detailed):
            if record and record['uid'] in local_com:
                detailed[i] = {**record, 'com': local_com[record['uid']]}
        if army and phase == 'before':
            # Formation completeness.  The BCD start list can omit a squad
            # leader (its count byte is 0 there even though its squad fought),
            # so the copied troops keep a squad id that no copied commander
            # claims -- the host then leaves them outside any formation.  The
            # VCR com records still name the leader of every squad, so add the
            # leaders of copied squads that the start list does not contain.
            need = set()
            for r in detailed:
                if not r:
                    continue
                sq = None
                if r['pos'] is not None:
                    sq = struct.unpack_from('<I', raw, r['pos'] + 32)[0]
                elif r['uid'] in vcr_snaps:
                    sq = vcr_snaps[r['uid']]['squad']
                if sq is not None and sq != 0xFFFFFFFF:
                    need.add(sq)
            led = set()
            for r in detailed:
                if r and r.get('com'):
                    led.update(r['com']['squads'])
            copied_uids = {r['uid'] for r in detailed if r}
            added = []
            for c in candidates:
                if not need - led:
                    break
                if (c['type'] is None or c['uid'] in copied_uids
                        or not (set(c['squads']) & need)):
                    continue
                picked_units.append(c['type'])
                detailed.append({'uid': c['uid'], 'type': c['type'],
                                 'province': prov, 'nation': side_nat,
                                 'pos': None, 'com': c,
                                 'hp': vcr_snaps.get(c['uid'], {}).get('hp')})
                copied_uids.add(c['uid'])
                led.update(c['squads'])
                added.append(f'{c["name"]} ({gamedata.units()[c["type"]].name})')
            if added:
                print(f'  NOTE: {len(added)} squad leader(s) missing from the '
                      f'battle start list but named by the VCR were added so '
                      f'their squads keep their formation: '
                      f'{"; ".join(added)}')
        print(f'  {side} battle report {prov} [{_label(seq, rep)}], copying '
              f'{copy} {_nation_text(side_nat)} '
              f'({"before" if phase == "before" else "after"} battle): '
              f'{len(picked_units)} units '
              f'({sorted(set(picked_units))})')
        units += picked_units
    return units, detailed


def _scan_vcr_snapshots(raw: bytes, vcr_start: int, bcd_start: int,
                        nation: int) -> dict[int, dict]:
    """Scan VCR snapshot records inside a battle report block.

    A VCR snapshot is a 173-byte ftherlnd-like unit record written before
    the BCD block.  Field offsets (verified against real saves):
        +0  u32 unit id
        +28 u32 squad id (0xFFFFFFFF = commander)
        +32 u16 unit type
        +36 u16 province
        +64 u16 owning nation

    The player's own .trn carries only its own units plus enemies it can
    see, so the VCR is the *only* source for squad ids and uid/type pairs
    of unseen enemy units.

    Returns ``{uid: {'type': int, 'squad': int, 'province': int, 'hp': int}}``
    for every snapshot matching ``nation``.
    """
    out: dict[int, dict] = {}
    seg = raw[vcr_start:bcd_start]
    if len(seg) < 173:
        return out
    pos = 0
    while pos + 173 <= len(seg):
        uid = struct.unpack_from('<I', seg, pos)[0]
        if not (1 <= uid < 10_000_000):
            pos += 1
            continue
        sq = struct.unpack_from('<I', seg, pos + 28)[0]
        typ = struct.unpack_from('<H', seg, pos + 32)[0]
        prov = struct.unpack_from('<H', seg, pos + 36)[0]
        nat = struct.unpack_from('<H', seg, pos + 64)[0]
        if (typ in gamedata.units()
                and 1 <= prov <= 5000
                and nat == nation):
            out[uid] = {'type': typ, 'squad': sq, 'province': prov,
                        'hp': struct.unpack_from('<H', seg, pos + 34)[0]}
        pos += 1
    return out


def _take_spare_commander(pool: dict[int | None, list[dict]],
                          unit_type: int) -> dict | None:
    """The com record of the unit slot of ``unit_type``, matched by type.

    A commander of the copied side normally has no unit record in the player's
    .trn (only the player's own units and visible enemies are listed), so its
    .trn record cannot be used to pair the com record -- the unit is simply not
    visible here, not necessarily dead.  The VCR snapshot of the uid carries
    the type (see :func:`_vcr_unit_type`); matching on it keeps a commander's
    com record -- name, magic paths and equipment -- from landing on a
    commander of a different type.  Province 253 (battle report, attacker 9)
    is the reference case: the Necromancer and the Captain were swapped.

    A candidate whose snapshot record could not be found has type ``None`` and
    is the only fallback.
    """
    for key in (unit_type, None):
        bucket = pool.get(key)
        if bucket:
            return bucket.pop(0)
    return None


def _report_units(raw: bytes, entries, side: str) -> list[int]:
    """Unit types selected by ``battle_report`` entries."""
    return _report_details(raw, entries, side)[0]


def _split_report_entries(picks: list[dict], own_nation: int
                          ) -> tuple[list[dict], list[dict], set[int]]:
    """Split picks into ``(player_entries, enemy_entries, skipped_provinces)``.

    The rule is per read side, not per province list.  A commander must never
    be copied into both armies (the engine rejects that with "twin
    commanders"):

    * a read side whose nation is the own nation goes to the player army, and
      that province is skipped from the player's current-garrison copy;
    * a read side whose nation is not the own nation goes to the enemy army,
      and that province is skipped from the enemy scout copy (the enemy side
      derives its skip set from the returned enemy entries' provinces).

    ``'both'`` reads the own side and the other side, so it applies both
    rules.  A province in both lists whose pick reads only one side keeps the
    other side's current copy (an enemy-occupied province with our troops in
    the castle: read the enemy -> only the scout is suppressed, the own
    garrison stays).
    """
    player_entries: list[dict] = []
    enemy_entries: list[dict] = []
    skipped: set[int] = set()
    for pick in picks:
        prov = int(pick['province'])
        sides = ([pick['own_side'], pick['other_side']]
                 if pick['copy'] == 'both' else [pick['copy']])
        for side in sides:
            nation = pick['attacker'] if side == 'attacker' else pick['defender']
            entry = {**pick, 'copy': side,
                     'timing': pick.get('timing', {}).get(nation, 'before')}
            if nation == own_nation:
                player_entries.append(entry)
                skipped.add(prov)
            else:
                enemy_entries.append(entry)
    return player_entries, enemy_entries, skipped


def _pick_battle_reports(raw: bytes, provs,
                         own_nation: int | None = None) -> list[dict]:
    """Interactively pick one battle report per scout province.

    Every battle report whose province is listed in ``enemy.provinces``
    is offered.  Each report is shown as ``[seq, name, uuid, attacker,
    defender]``: the seq is a 1-based counter per province, the uuid is the
    VCR offset that later pinpoints the report inside the .trn, attacker and
    defender are the nation names, and the name is 'battle' or
    'assassinate'.  The .trn stores no battle title text, but assassination
    reports are the follow-up VCR records written after the province's main
    battle: their primary province field is 0 (the real province sits at
    +39) and the u32 at +31 is 1.  Verified against ground truth in
    saltedfish_reborn province 95 (1 battle + 5 assassinations) and the four
    1-commander-vs-1-commander VCRs of Wherecrowfeast.

    The returned dicts carry the usual ``province``/``attacker``/``defender``/
    ``copy`` keys for ``_report_details``, plus ``seq`` (the report's 0-based
    index at that province) so a province with several battles between the
    same nations still resolves to exactly the picked report.

    ``own_nation`` enables the second-level "copy both sides" choice: it
    matches that nation id against the report's attacker/defender and stores
    ``copy='both'`` with ``own_side``/``other_side``.  When neither side is the
    own nation the choice is refused and the second level is shown again.  The
    caller expands a ``'both'`` pick into its two concrete sides before
    ``_report_details`` (which only accepts attacker/defender).
    """
    picked: list[dict] = []

    def _nat_name(nation: int) -> str:
        nat = gamedata.nations().get(nation)
        if nat:
            return nat.name
        return 'Independents' if nation == 0 else str(nation)

    def _ask(prompt: str = '> ') -> str | None:
        """``input`` that returns None at end of input instead of raising.

        The build is also driven with piped input (automation, tests); running
        out of lines must not end in an EOFError traceback.
        """
        try:
            return input(prompt)
        except EOFError:
            print()
            return None

    def _ask_timing(nation: int) -> str:
        """Ask whether the copied army is the battle start or the survivors."""
        while True:
            print(f"you want to copy '{_nat_name(nation)}'")
            print('0 copy units before battle')
            print('1 copy units after battle')
            line = _ask()
            if line is None:
                return 'before'
            try:
                n = int(line.strip())
            except ValueError:
                n = -1
            if n == 0:
                return 'before'
            if n == 1:
                return 'after'
            print('input error')

    for prov in provs:
        prov = int(prov)
        reports = trn_parse.battle_reports(raw, prov)
        if not reports:
            continue
        battles = [
            (i + 1,
             'assassinate'
             if struct.unpack_from('<I', raw, rep['vcr'] + 31)[0] else 'battle',
             rep['vcr'], _nat_name(rep['attacker']), _nat_name(rep['defender']),
             i, rep)
            for i, rep in enumerate(reports)]
        while True:
            print(f"There are battles in province: '{prov}', "
                  f'do you want to:')
            print('0 skip copy battle report  usually you may skip  '
                  'assasination')
            for seq, name, uuid, att_name, def_name, _, _ in battles:
                print(f'{seq} copy {name} '
                      f'attacker: {att_name} VS defender: {def_name}')
            line = _ask()
            if line is None:          # end of input: copy no more reports
                return picked
            try:
                n = int(line.strip())
            except ValueError:
                n = -1
            if n == 0:
                break
            hit = [b for b in battles if b[0] == n]
            if not hit:
                print('input error')
                continue
            _, _, _, _, _, rep_index, rep = hit[0]
            while True:
                print('1 copy attacker')
                print('2 copy defender')
                print('3 copy both sides (match own nation)')
                side_line = _ask()
                if side_line is None:     # end of input: stop asking
                    return picked
                side_input = side_line.strip()
                if side_input in ('1', '2'):
                    side = 'attacker' if side_input == '1' else 'defender'
                    nation = rep[side]
                    picked.append({
                        'province': prov, 'attacker': rep['attacker'],
                        'defender': rep['defender'],
                        'copy': side,
                        'seq': rep_index,
                        'timing': {nation: _ask_timing(nation)}})
                    break
                if side_input == '3':
                    if own_nation is None:
                        print('  own nation id is unknown, cannot match; '
                              'choose 1 or 2')
                        continue
                    if rep['attacker'] == own_nation:
                        own_side, other_side = 'attacker', 'defender'
                    elif rep['defender'] == own_nation:
                        own_side, other_side = 'defender', 'attacker'
                    else:
                        print(f'  没有匹配到己方 (own nation {own_nation}); '
                              f'attacker {rep["attacker"]} '
                              f'({_nat_name(rep["attacker"])}), defender '
                              f'{rep["defender"]} '
                              f'({_nat_name(rep["defender"])}) -- choose again')
                        continue
                    # Both sides are copied, so both are asked separately.
                    timing = {rep['attacker']: _ask_timing(rep['attacker'])}
                    timing[rep['defender']] = _ask_timing(rep['defender'])
                    picked.append({
                        'province': prov, 'attacker': rep['attacker'],
                        'defender': rep['defender'], 'copy': 'both',
                        'own_side': own_side, 'other_side': other_side,
                        'seq': rep_index, 'timing': timing})
                    break
                print('input error')
            break
    return picked


def _estimate_scout_counts(entries: list[list], total: int | None) -> None:
    """Fill a scout report's unknown counts in place.

    ``entries`` is ``[[unit_type, count], ...]`` in report order, with
    ``None`` where the .trn stores no count.  The report's first line prints
    the garrison size ("The province contains about N enemy units"), so the
    missing counts are spread over those types towards it, decaying by 0.8
    per position because the report lists types by descending count.

    Every estimate is capped by the count before it: the printed size is an
    approximation and legitimate reports contradict a strict descending list
    (province 294: 71 + 33 exact, three more types, "about 240"), so a share
    that would outgrow the previous type is left at that type's count and the
    army simply ends up smaller than the headline.  Without a stored total
    the estimate just follows the preceding count.
    """
    unknown = [entry for entry in entries if entry[1] is None]
    if not unknown:
        return
    first = next(i for i, entry in enumerate(entries) if entry is unknown[0])
    prev = next((entry[1] for entry in reversed(entries[:first])
                 if entry[1] is not None), 30)
    remaining = None
    if total is not None:
        remaining = total - sum(entry[1] for entry in entries
                                if entry[1] is not None)
    if remaining is None:
        for entry in unknown:
            entry[1] = max(1, round(prev * 0.8))
            prev = entry[1]
        return
    weights = [0.8 ** i for i in range(len(unknown))]
    budget = remaining
    for i, entry in enumerate(unknown):
        share = round(budget * weights[i] / sum(weights[i:]))
        entry[1] = max(1, min(prev, share))
        budget -= entry[1]


def _visible_enemy_units(raw: bytes, province: int,
                         nation: int | None) -> tuple[list[dict], int]:
    """Enemy units standing in ``province``, read from our own .trn.

    The .trn unit table is the exact composition the province screen shows
    (mounts included), so it wins over a scout report whenever it lists the
    enemy nation's units here -- typically a province where we hold the fort
    but the enemy holds the land.  An army only scouted from afar has no
    records in the table, and the report is used then.

    Returns ``(specs, orphan mounts)`` in the shape :func:`_write_nation_army`
    takes, so the rider/mount pair survives the copy:

    - a mount is a record whose ``master`` is positive (it points at its
      rider's uid); it is kept with ``master = <rider src_uid>`` and
      :func:`_apply_master_chain` rewrites that to the rider's new ftherlnd
      uid, while ``+26:0`` marks it as a mount.
    - a rider is any unit a kept mount points at, or one already flagged
      ``+25:7``; ``master = -2`` and ``+25:7`` are exactly what the engine
      writes for its own mounted pairs, so a mounted *troop* goes in as ``-2``
      too.  ``-2`` does not mean "commander" -- 9001 Debug Sensei is a
      commander with ``master = -1``; commander identity is the com record.
    - everything else is a plain unit (``master = -1``).

    A .trn record is the same 173 byte record as in ``ftherlnd`` behind a 4
    byte prefix, so ftherlnd offset ``N`` is ``pos + 4 + N`` (master +81 ->
    +85, rider bit +25 -> +29, mount bit +26 -> +30).

    Mounts whose rider is not in the province (dead rider) are counted and
    dropped -- they cannot be chained.
    """
    if not nation:
        return [], 0
    units = gamedata.units()
    picked: list[dict] = []
    for record in trn_parse.current_unit_records(raw):
        if record['province'] != province or record['nation'] != nation:
            continue
        if record['type'] not in units:
            continue
        pos = record['pos'] + 4
        picked.append({
            'type': record['type'],
            'src_uid': record['uid'],
            'master': struct.unpack_from('<i', raw, pos + 81)[0],
            'rider': 1 if (raw[pos + 25] & 0x80) else 0,
        })
    uids = {spec['src_uid'] for spec in picked}
    specs = [spec for spec in picked
             if spec['master'] <= 0 or spec['master'] in uids]
    orphans = len(picked) - len(specs)
    mounted = {spec['master'] for spec in specs if spec['master'] > 0}
    for spec in specs:
        if spec['master'] <= 0:
            if spec['src_uid'] in mounted:
                spec['rider'] = 1
            spec['master'] = -2 if spec['rider'] else -1
    return specs, orphans


def _enemy_army(raw: bytes, enemy_cfg: dict,
                report_records: list[dict] | None = None,
                extra_specs: list[dict] | None = None,
                extra_start: list[int] | None = None,
                enemy_nation: int | None = None
                ) -> tuple[list[int], list[dict], dict | None]:
    """Enemy side: scout report + battle reports + configured extras.

    The scout report names every garrison type (the decrypted report text is
    matched against the Inspector names in data/units.csv, singular or
    plural) but stores exact counts only for the top two.  The remaining
    types take their count from ``scout_extra`` when configured, otherwise
    from the report's own garrison size.

    A province with no scout report at all falls back to the .trn unit table
    (``_visible_enemy_units``): that is what a province looks like when we
    hold the fort but the enemy holds the land -- the game shows the besieging
    army directly, without writing an intel record.  ``enemy_nation`` is what
    those records are filtered by.

    Report entries carry no commander/rider metadata, so every type is
    classified by its id with the Dom6 Inspector's unit logic before it is
    placed (``_unit_role``; no nation lookup -- the reporting nation is not in
    the report and the arena enemy nation is random): a commander-class type
    is written as an actual commander record for *every* unit, a plain troop
    as a plain unit record.  A god chassis is neither: the sighted one is the
    army's god ("A huge Monolith was seen towering over the army. The army
    appears to be commanded by Tathai the Monolith who radiates power.").  It
    is returned as ``god``; any further chassis sighting is skipped and logged
    -- a nation has one god, and copying a chassis as a statue-troop would
    distort the battle.  The commander rule matters: a commander-class unit
    written as a plain troop has no leader slot, and a shape-changing
    commander then reverts to its other shape when the turn is hosted (3680
    Wolf Clan Seithberender became 3687 Wolf).  Returns ``(army, commanders,
    god)``, each commander spec indexing into ``army``.
    """
    army: list[int] = []
    cmdrs: list[dict] = []
    explicit_god = bool(enemy_cfg.get('pretender'))
    god: dict | None = None

    def add(unit_type: int, count: int, where: str,
            spec: dict | None = None) -> None:
        nonlocal god
        unit = gamedata.units()[unit_type]
        role = _unit_role(unit_type)
        if role == 'pretender':
            if explicit_god or god is not None:
                # A nation has one god.  Extra sighted chassis are not copied
                # as troops either: an immobile chassis would sit in the
                # province forever as a statue-soldier and distort the battle.
                print(f'  NOTE: {where}: {unit_type} ({unit.name}) is a god '
                      f'chassis, but the enemy god is already decided; '
                      f'skipped (a nation has one god)')
                return
            god = {'id': unit_type, 'where': where, 'name': None}
            print(f'  {where}: {unit_type} ({unit.name}) is a god chassis '
                  f'-- taken as the enemy pretender')
            if count > 1:
                print(f'  NOTE: {where}: {count} x {unit_type} ({unit.name}) '
                      f'sighted; one is taken as the god, the other '
                      f'{count - 1} skipped')
            return
        if role != 'cmdr':
            if spec is not None:
                army.append(spec)
            else:
                army.extend([unit_type] * count)
            return
        for _ in range(count):
            cmdrs.append({'id': unit_type, 'index': len(army),
                          'label': f'{where}: {unit.name}',
                          'name': unit.name, 'paths': unit.paths,
                          'cmdr_override': True, 'base': 0})
            army.append(spec if spec is not None else unit_type)

    provs = enemy_cfg.get('provinces') or []
    if isinstance(provs, int):
        provs = [provs]
    # Battle reports are picked interactively (one per scout province), not
    # read from the config.  The pick is cached on enemy_cfg so the arena
    # recreation retries of main() do not ask again.  A province whose battle
    # report the user picked is not scout-copied as well.
    if '_battle_report_picks' not in enemy_cfg:
        enemy_cfg['_battle_report_picks'] = _pick_battle_reports(raw, provs)
    battle_pick_provs = {int(p['province'])
                         for p in enemy_cfg['_battle_report_picks']}
    overrides = {_unit_id(k): int(v)
                 for k, v in (enemy_cfg.get('scout_extra') or {}).items()}
    for prov in provs:
        prov = int(prov)
        if prov in battle_pick_provs:
            print(f'  province {prov}: battle report picked; the scout '
                  f'report is not copied')
            continue
        where = f'scout report province {prov}'
        report = trn_parse.scout_report(raw, prov)
        entries = [[unit_type, count] for unit_type, count in report.units]
        # The .trn unit table wins whenever it lists the enemy nation's units
        # in this province: it is the exact composition the province screen
        # shows, mounts included, while a report only knows the top two types
        # and rounds them ("about N").  The usual reason both exist is that we
        # hold the fort while the enemy holds the land.  An army scouted from
        # afar has no unit table rows, so the report is used then.
        visible, orphans = _visible_enemy_units(raw, prov, enemy_nation)
        if visible:
            before = len(army)
            mounts = 0
            for spec in visible:
                if spec['master'] > 0:
                    # A mount is not a unit of its own: keep its master
                    # chain so _apply_master_chain can point it at the
                    # rider's new uid.
                    army.append(spec)
                    mounts += 1
                    continue
                add(spec['type'], 1, where, spec)
            units = [s['type'] if isinstance(s, dict) else s
                     for s in army[before:]]
            print(f'  province {prov}: {len(units) - mounts} unit(s) + '
                  f'{mounts} mount(s) from the .trn unit table '
                  f'({sorted(set(units))})')
            if report.total is not None:
                print(f'  NOTE: scout report province {prov} says about '
                      f'{report.total} unit(s); the .trn unit table wins '
                      f'(exact counts, mounts included)')
            if orphans:
                print(f'  NOTE: {orphans} mount(s) in that province have '
                      f'no rider there (the rider is dead or has left); '
                      f'skipped')
            continue
        if not entries:
            if report.total is not None or report.unmatched:
                print(f'  NOTE: {where}: the report names no unit that can be '
                      f'placed; nothing copied for it')
            else:
                print(f'  NOTE: province {prov}: no scout report and no enemy '
                      f'unit of nation {enemy_nation} in the .trn unit table; '
                      f'nothing copied for it')
            continue
        if report.unmatched:
            print(f'  NOTE: scout report province {prov}: no unit in '
                  f'data/units.csv is named {", ".join(report.unmatched)}; '
                  f'skipped')
        for entry in entries:
            if entry[1] is None:
                entry[1] = overrides.pop(entry[0], None)
        guessed = [entry for entry in entries if entry[1] is None]
        _estimate_scout_counts(entries, report.total)
        before = len(army)
        for unit_type, count in entries:
            add(unit_type, count, where)
        if god is not None and god['where'] == where and god['name'] is None:
            god['name'] = dict(report.commanders).get(god['id'])
        units = army[before:]
        note = (f'  scout report province {prov}: {len(units)} units '
                f'({sorted(set(units))})')
        if report.total is not None:
            note += f', report says about {report.total}'
        if guessed:
            note += f', counts estimated: {guessed}'
        print(note)
    for unit_type, count in overrides.items():
        add(unit_type, count, 'scout_extra')
    if extra_start is not None:
        extra_start.append(len(army))
    if extra_specs is None:
        extra_specs = _custom_unit_specs(enemy_cfg.get('extra_units'))
    extra = [spec['id'] for spec in extra_specs]
    if extra:
        print(f'  extra units not in .trn: {len(extra)} '
              f'({sorted(set(extra))})')
    army += extra
    report_units, detailed = _report_details(
        raw, enemy_cfg['_battle_report_picks'], 'enemy')
    if report_records is not None:
        for i, record in enumerate(detailed):
            if record is not None:
                report_records.append({**record, 'comp_index': len(army) + i})
    army += report_units
    return army, cmdrs, god


def _find_com(data: bytes, base: int, stride: int, count: int, uid: int,
              verbose: bool = False
              ) -> tuple[int, int, int, str, list[int], bytes] | None:
    """The com record of unit ``uid`` in the ftherlnd com chain.

    Walks the same chain as ``_scrub_commanders``; returns
    (comid, record offset, unitid field offset, name, squads, tail).

    Unlike ``_scrub_commanders`` (which runs BEFORE any records are scrubbed),
    this walker runs AFTER scrubbing.  Scrubbed records and extended dead
    Reserve slots carry ``unitid == 0xFFFFFFFF``.  Those must be skipped, not
    treated as chain terminators, because live records from other nations
    can legitimately appear behind them in the chain.
    """
    pos = base + count * stride
    limit = len(data) - 8
    found_ids = []
    skipped = 0
    while pos + 8 <= limit:
        term = data.find(b'\x4f', pos + 4, pos + 4 + 66)
        if term < 0:
            if verbose:
                print(f'  _find_com: no terminator at pos {pos}')
            return None
        uidpos = term + 1
        rec_end = uidpos + COM_BODY
        if rec_end > limit:
            if verbose:
                print(f'  _find_com: rec_end {rec_end} > limit {limit}')
            return None
        unitid = struct.unpack_from('<I', data, uidpos)[0]
        if unitid == 0xFFFFFFFF:
            # Dead scrubbed record or extended Reserve slot — skip it.
            skipped += 1
            pos = rec_end
            continue
        slots = struct.unpack_from('<5I', data, uidpos + 4)
        if not 0 <= unitid <= count:
            if verbose:
                print(f'  _find_com: bad unitid {unitid} '
                      f'(uid={uid}, skipped={skipped})')
            return None
        if not all(s == 0xFFFFFFFF or s < 10_000_000 for s in slots):
            if verbose:
                print(f'  _find_com: bad slots at com pos {pos}')
            return None
        name = bytes(b ^ XOR for b in data[pos + 4:term])
        if not name or len(name) > 64:
            if verbose:
                print(f'  _find_com: bad name at pos {pos}')
            return None
        letters = sum(1 for c in name if 32 <= c < 127)
        if letters < 1 or len(name) - letters > 2:
            if verbose:
                print(f'  _find_com: non-printable name {name!r} at pos {pos}')
            return None
        comid = struct.unpack_from('<I', data, pos)[0]
        found_ids.append((comid, unitid, name.decode('latin1'), pos))
        if unitid == uid:
            return (comid, pos, uidpos, name.decode('latin1'),
                    list(slots), data[uidpos + 24:rec_end])
        pos = rec_end
    if verbose:
        print(f'  _find_com: chain ended, scanned {len(found_ids)} live, '
              f'skipped {skipped} dead (looking for uid={uid})')
        for comid, u, n, p in found_ids:
            mark = ' ***' if u == uid else ''
            print(f'    com {comid:3d} uid {u:3d} {n!r} @ {p}{mark}')
    return None


def _scrub_commanders(raw: bytearray, base: int, stride: int, count: int,
                      touched: set[int], keep: set[int],
                      limit: int | None = None,
                      required: int = 0) -> list[tuple[int, int, int]]:
    """Null com records whose commander unit record we rewrote.

    The com table follows the unit table as one back-to-back chain of fixed
    layout (verified byte-for-byte on a fresh two-nation save: comids 1..38
    plus a dead comid -1 slot in front):
        [u32 comid][xor-encoded name][0x4f][u32 unitid]
        [5 x u32 squad slots][181 byte tail]   (205 bytes after the name)
    The chain is parsed FORWARD record by record; names may carry up to two
    non-printing prefix bytes (random-name markers such as 8c d9 seen on
    debug-mod heroes like Ivaldi).  The old search walked comid 0,1,2,... in
    file order and broke at the first comid it could not find, which stopped
    the chain right before those prefixed records (only 5 of ~21 slots were
    scrubbed, so 14 source commanders landed without a com record and lost
    name and equipment).

    A com whose unit was zeroed or turned into a plain troop makes the host
    abort with 'unit2com inconsistency'; the engine marks a dead com with
    unitid -1.  ``keep`` holds the unit ids of the two gods, whose com
    records must survive.

    ``limit`` ends before the nation design array: its u32s (nation ids,
    bless values) must never be overwritten.

    Returns the (comid, record offset, unitid field offset) triples that were
    scrubbed; those slots are re-armed for our own commanders or replaced
    wholesale by transplanted source commander records.
    """
    targets = touched - keep
    scrubbed: list[tuple[int, int, int]] = []
    data = bytes(raw)
    pos = base + count * stride
    limit = len(data) - 8 if limit is None else min(limit, len(data) - 8)
    seen = 0
    max_comid = 0
    while pos + 8 <= limit:
        term = data.find(b'\x4f', pos + 4, pos + 4 + 66)
        if term < 0:
            break
        uidpos = term + 1
        rec_end = uidpos + COM_BODY
        if rec_end > limit:
            break
        unitid = struct.unpack_from('<I', data, uidpos)[0]
        slots = struct.unpack_from('<5I', data, uidpos + 4)
        if not 0 <= unitid <= count:
            break
        if not all(s == 0xFFFFFFFF or s < 10_000_000 for s in slots):
            break
        name = bytes(b ^ XOR for b in data[pos + 4:term])
        if not name or len(name) > 64:
            break
        letters = sum(1 for c in name if 32 <= c < 127)
        if letters < 1 or len(name) - letters > 2:
            break
        comid = struct.unpack_from('<I', data, pos)[0]
        if comid < 0x80000000:
            max_comid = max(max_comid, comid)
        if unitid in targets:
            struct.pack_into('<i', raw, uidpos, -1)
            # The dead slot keeps the old commander's tail, including item
            # slots that may hold stale ids past the item table -- the host
            # validates every record in the chain and aborts with
            # "bad equip" even for this dead one.
            _dead = bytearray(raw[uidpos + 24:rec_end])
            _sanitize_items(_dead, f'scrubbed com {comid}')
            raw[uidpos + 24:rec_end] = _dead
            # A dead slot (comid -1) stays dead: handing its comid out to a
            # transplanted commander makes the host abort (observed: Afe
            # received comid 4294967295 and hosting failed).  Only live
            # comids are re-armed; shortfall is covered by the extension
            # below.
            if comid < 0x80000000:
                scrubbed.append((comid, pos, uidpos))
        pos = rec_end
        seen += 1
    if pos < limit:
        # The design array is preceded by a short non-com section preamble,
        # so a non-empty tail is normal.  What must NOT remain is a
        # well-formed record of a rewritten unit (the old bug: the chain
        # silently stopped at the first prefixed name and such records were
        # left armed, stripping name and equipment from those commanders).
        region_start = base + count * stride
        for uid in targets:
            pat = b'\x4f' + struct.pack('<I', uid)
            q = pos
            while True:
                i = data.find(pat, q, limit)
                if i < 0:
                    break
                q = i + 1
                end = i + 5 + COM_BODY
                if end > limit or i - 4 < region_start:
                    continue
                slots = struct.unpack_from('<5I', data, i + 5)
                if not all(s == 0xFFFFFFFF or s < 10_000_000 for s in slots):
                    continue
                run = 0
                j = i - 1
                while j >= region_start and 32 <= (data[j] ^ XOR) < 127:
                    run += 1
                    j -= 1
                if 1 <= run <= 64:
                    raise ValueError(
                        f'commander record of rewritten unit {uid} at {i} '
                        f'was not reached by the com chain ({seen} records '
                        f'parsed); refusing to build with missing commanders')
    missing = max(0, required - len(scrubbed))
    if missing:
        # Append dead records before the non-com preamble; every one is
        # replaced by a live source commander below.  The trailing commander
        # name record stores the highest comid and the host refuses to load
        # records above it, so advance that last occurrence as well.
        previous_max = max_comid
        for i in range(missing):
            max_comid += 1
            record = _com_record(max_comid, 'Reserve', 0xFFFFFFFF, [],
                                 bytes(COM_TAIL))
            uidpos = pos + 4 + len('Reserve') + 1
            raw[pos:pos] = record
            scrubbed.append((max_comid, pos, uidpos))
            pos += len(record)
        lastcom = raw.rfind(struct.pack('<I', previous_max))
        if lastcom < limit:
            raise ValueError('trailing last-commander id not found')
        struct.pack_into('<I', raw, lastcom, max_comid)
        print(f'  extended commander chain with {missing} slot(s); '
              f'last comid {max_comid}')
    return scrubbed


def _clear_independents(raw: bytearray, base: int, stride: int, count: int,
                        keep_nations: set[int]) -> list[int]:
    """Remove every unit not owned by one of the two arena nations.

    The arena must always have independent strength 0, so the garrisons the
    game created in neutral provinces are all deleted (not just those in the
    two battle provinces).  ``--indepstr`` is only a unit-table size lever
    here, never a gameplay setting: whatever it had to be to make the table
    hold both armies, no independent survives.

    Returns the offsets that were cleared; their type is set to 0, which
    makes the host delete the record and keep the slot available.
    """
    cleared: list[int] = []
    for k in range(count):
        off = base + k * stride
        if struct.unpack_from('<H', raw, off + 64)[0] in keep_nations:
            continue
        p1, _ = struct.unpack_from('<HH', raw, off + 36)
        if p1 == 0xFFFF:                     # already a free slot
            continue
        if struct.unpack_from('<H', raw, off + 32)[0] == 0:
            continue
        cleared.append(off)
    for off in cleared:
        struct.pack_into('<H', raw, off + 32, 0)
        struct.pack_into('<HH', raw, off + 36, 0, 0)
    return cleared


def _write_nation_army(raw: bytearray, base: int, stride: int, count: int,
                       nation: int, composition: list[int | dict],
                       province: int,
                       god_type: int | None = None,
                       protected: list[int] | None = None,
                       skip: set[int] | None = None
                       ) -> tuple[int, list[int], list[int]]:
    """Rewrite ``nation``'s unit records to hold ``composition`` in ``province``.

    ``composition`` may be plain ints (unit types) or dicts with keys ``type``,
    ``master``, ``rider``, ``src_uid``.  Ints are written as plain units;
    dicts preserve commander chains from the source .trn.  Only ``type``,
    province and the rider flag at +25 are written here — the master chain
    at +81 must be patched separately by :func:`_apply_master_chain`, which
    handles uid remapping for mounts that reference their rider by source
    uid.

    Returns ``(god_offset, used_offsets, leftover_offsets)``.
    """
    protected = set(protected or [])
    protected.add(nation)
    skip = skip or set()

    specs = [({'type': it, 'master': -1, 'rider': 0}
              if isinstance(it, int) else it)
             for it in composition]
    needed = len(specs) + 1  # +1 for the pretender record

    records: list[int] = []
    spare: list[int] = []
    for k in range(count):
        off = base + k * stride
        if off in skip:
            continue
        nat = struct.unpack_from('<H', raw, off + 64)[0]
        if nat == nation:
            records.append(off)
        elif nat not in protected:
            spare.append(off)
    if not records:
        raise ValueError(f'no unit records for nation {nation}')

    def _is_god_record(off: int) -> bool:
        """True when the engine currently treats this record as a king.

        The king markers are the com type (``+21 == 4``) and the 0x027C god
        flag (``+42 == 636``) -- in every save checked, the only records that
        carry them are the nations' gods.  The unit type cannot answer this:
        a god record is not necessarily a chassis ``pretenders.csv`` knows
        (the debug mod's god is type 8997, and saves also hold nation-specific
        gods such as 441 Consort or 1967 Slayer Sanguine), and a slot's type
        is exactly what gets rewritten.  Type data says what a slot *should*
        be, the markers say what the engine *thinks* it is; "king is no god"
        is the mismatch between the two.
        """
        return (raw[off + 21] == 4
                and struct.unpack_from('<H', raw, off + 42)[0] == 636)

    # The debug mod's capital god (nation 97/98, neither player) is not
    # protected, so it can end up in the spare pool.  Borrowing it would take
    # that nation's king away, so spare god records are left where they are.
    spare = [off for off in spare if not _is_god_record(off)]
    own_records = list(records)   # before borrowing, so the god stays native
    while len(records) < needed and spare:
        off = spare.pop(0)
        struct.pack_into('<H', raw, off + 64, nation)
        records.append(off)
    if len(records) < needed:
        raise ValueError(
            f'not enough unit records for nation {nation}: '
            f'have {len(records)}, need {needed}')

    # Locate the pretender record by signature (borrowed slots may sit before
    # it).  The markers say which records the engine thinks are kings; a
    # king's type must also be a chassis of this nation (Dom6 Inspector's
    # pretender list), so a chassis-typed marked record wins over one whose
    # type was already zeroed/rewritten.
    chassis = gamedata.pretenders().get(nation, set())
    marked = [off for off in own_records if _is_god_record(off)]
    god_off = next(
        (off for off in marked
         if struct.unpack_from('<H', raw, off + 32)[0] in chassis),
        marked[0] if marked else records[0])
    slots = [off for off in records if off != god_off][:needed - 1]
    used = {god_off, *slots}

    # Exactly one record per nation may be its king, and that king must still
    # be a god.  Every slot below receives an ordinary unit type (a commander
    # or a troop -- never a chassis, ``_unit_role`` keeps those out of the
    # composition), so it must not stay marked as a king: a borrowed or
    # surplus record that keeps com type 4 / flag 636 while its type is, say,
    # 1095 Keeper of the Tombs aborts the host with
    # "bc: king is no god (p113, ...)".  The same applies to the surplus
    # records handed to the other nation (the caller clears their type).
    for off in records:
        if off == god_off:
            continue
        raw[off + 21] = 0
        struct.pack_into('<H', raw, off + 42, 0)

    if god_type is not None:
        # The king record must really hold a god type: the host aborts with
        # "bc: king is no god (p113, ...)" when the nation's king is an
        # ordinary unit.  The type is written by id alone -- the copied army
        # carries no nation, and the arena enemy nation is random, so a
        # chassis is never filtered through this nation's pretender list.
        struct.pack_into('<H', raw, god_off + 32, god_type)

    # Write types and provinces.
    for off, spec in zip(slots, specs):
        struct.pack_into('<H', raw, off + 32, spec['type'])

    # Current hit points (+34).  A slot is usually borrowed from the arena's
    # old garrison, which leaves its own hp behind: 178 of the copied records
    # carried hp 14 and the host recycled every one of them at init ("removed
    # ... hp 0"), silently dropping 88 Sage-Priests, 22 troops and a dozen
    # commanders.  Write the hp read from the unit's source record instead.
    for off, spec in zip(slots, specs):
        hp = spec.get('hp')
        if hp is None:
            unit = gamedata.units().get(spec['type'])
            hp = unit.hp if unit else 0
        if hp:
            struct.pack_into('<H', raw, off + 34, hp)
    for off in [god_off] + slots:
        struct.pack_into('<HH', raw, off + 36, province, province)

    # Creation leaves surplus records empty (nat/prov 0xffff) with the i32
    # alive marker at +66 set to 0; every live record has -1 there (verified
    # on the full table).  Reusing an empty slot without restoring the
    # marker makes the host delete the unit on the first turn (observed:
    # five commanders and two dozen troops vanished right after hosting).
    for off in [god_off] + slots:
        struct.pack_into('<i', raw, off + 66, -1)

    # Rider flag (bit 0x80 of +25) — written here, not in _apply_master_chain,
    # because it only depends on whether this unit IS a rider.  The mount
    # flag (bit 0x01 of +26) is likewise decided by the spec: only a unit that
    # points at its rider (master > 0) is a mount.  Inherited arena records
    # can be mounts themselves, and leaving that bit on a plain troop makes
    # the host abort with "bc: mount with master -1".
    for off, spec in zip(slots, specs):
        flags = raw[off + 25]
        if spec.get('rider', 0):
            raw[off + 25] = flags | 0x80
        else:
            raw[off + 25] = flags & ~0x80
        if spec.get('master', -1) > 0:
            raw[off + 26] |= 0x01
        else:
            raw[off + 26] &= 0xFE

    # Leave master (+81) and the comtype flag untouched — call
    # _apply_master_chain after writing to patch the master chain with proper
    # uid remapping (mounts reference their rider by source uid).
    #
    # The surplus is everything not used above.  It must be computed from
    # ``used`` and not sliced by count: the god record sits past the borrowed
    # slots, so ``records[needed:]`` also contains the king.  The caller
    # reassigns surplus records to the other nation and zeroes their type,
    # which would strip this nation of its king (the borrowed, zeroed king
    # record was then picked as the *other* nation's king -- "king is no
    # god").
    return god_off, [god_off] + slots, [off for off in records
                                       if off not in used]


def _apply_master_chain(raw: bytearray, slots: list[int],
                        specs: list[dict]) -> None:
    """Patch the master chain (unit record +81) for the units in ``slots``.

    Riders whose source records had ``master == -2`` keep ``master = -2`` —
    the engine recognises them as commanders.  Mounts whose source records
    had ``master > 0`` (pointing at their rider's source uid) are rewritten
    to point at the rider's **new** target uid.  Specs without a ``src_uid``
    (int-only composition or enemy extra units) are written as plain units.
    """
    # source uid → target uid map.
    src_to_tgt_uid: dict[int, int] = {}
    for off, spec in zip(slots, specs):
        src_uid = spec.get('src_uid')
        if src_uid is not None:
            tgt_uid = struct.unpack_from('<I', raw, off)[0]
            src_to_tgt_uid[src_uid] = tgt_uid

    for off, spec in zip(slots, specs):
        m = spec.get('master', -1)
        if m == -2 or m == -1:
            struct.pack_into('<i', raw, off + 81, m)
        elif m > 0 and m in src_to_tgt_uid:
            struct.pack_into('<i', raw, off + 81, src_to_tgt_uid[m])
        else:
            struct.pack_into('<i', raw, off + 81, -1)


def _copy_god_record(raw: bytearray, off: int, src_raw: bytes, rec: dict,
                     province: int, nation: int) -> None:
    """Copy a source pretender's unit record fields verbatim into ``raw``.

    A .trn stores the same 173 byte record with a 4 byte prefix, so the source
    values for experience, hit points and the other pretender-owned fields sit
    at ``rec['pos'] + 4``.  Only the 169 bytes that both layouts share are
    taken; the arena's own identity and links are patched back afterwards:
    unit id, com type / flags, squad marker, chassis type, god flag, com link,
    nation, the leader chain and the final 4 bytes.
    """
    pos = rec['pos']
    body = src_raw[pos + 4:pos + 173]
    keep = ((0, 4), (21, 1), (25, 2), (28, 4), (32, 2), (42, 2), (62, 2),
            (64, 2), (66, 2), (80, 8), (169, 4))
    saved = [raw[off + a:off + a + n] for a, n in keep]
    raw[off:off + len(body)] = body
    for (a, _n), old in zip(keep, saved):
        raw[off + a:off + a + len(old)] = old
    struct.pack_into('<HH', raw, off + 36, province, province)
    struct.pack_into('<H', raw, off + 64, nation)


def _keep_offsets(raw: bytes, base: int, stride: int, count: int,
                  keep_types: set[int]) -> set[int]:
    """Offsets of unit records that must survive the army rewrite untouched.

    ``keep_types`` names unit types (e.g. the debug mod's commanders, which
    the engine places in the capitals at game creation).  A kept rider
    (+81 = -2) drags its mount (+81 = rider uid) into the set and vice versa,
    so mounted commanders are never split apart.
    """
    keep: set[int] = set()
    uid_at: dict[int, int] = {}
    for k in range(count):
        off = base + k * stride
        uid_at[struct.unpack_from('<I', raw, off)[0]] = off
        if struct.unpack_from('<H', raw, off + 32)[0] in keep_types:
            keep.add(off)
    changed = True
    while changed:
        changed = False
        for k in range(count):
            off = base + k * stride
            master = struct.unpack_from('<i', raw, off + 81)[0]
            if master > 0:
                owner = uid_at.get(master)
                if off in keep:
                    if owner is not None and owner not in keep:
                        keep.add(owner)
                        changed = True
                elif owner in keep:
                    keep.add(off)
                    changed = True
    return keep


def _mount_pairs(raw: bytes, base: int, stride: int, count: int
                 ) -> list[tuple[int, int]]:
    """``(rider uid, mount uid)`` pairs of the unit table in ``raw``.

    A mount record stores its rider's unit id at +81 (see
    :func:`_repair_mount_pairs`).  The table is always read before the army
    rewrite, so the pairs describe the pairs the arena was created with.
    """
    pairs: list[tuple[int, int]] = []
    for k in range(count):
        off = base + k * stride
        rider = struct.unpack_from('<i', raw, off + 81)[0]
        if rider > 0:
            pairs.append((rider, struct.unpack_from('<I', raw, off)[0]))
    return pairs


def _repair_mount_pairs(raw: bytearray, base: int, stride: int, count: int,
                        pairs: list[tuple[int, int]], touched: set[int]) -> int:
    """Fix mount/rider pairs that the army rewrite split apart.

    A mount record (+81 = its rider's unit id) is only valid while its rider
    carries +81 = -2 (the engine's "this unit is ridden" marker).  When the
    rewrite uses one half of a pair and leaves the other alone, the survivor
    dangles and the host aborts in getfatherland with "Mount ...'s master ...
    is not -2".  The rewritten half is already a plain unit, so turn the
    surviving rider into a plain unit too and delete the surviving mount.
    """
    fixed = 0
    for rider, mount in pairs:
        if rider in touched and mount in touched:
            continue
        if rider not in touched and mount not in touched:
            continue
        if rider in touched:
            off = base + (mount - 1) * stride
            struct.pack_into('<H', raw, off + 32, 0)
            struct.pack_into('<HH', raw, off + 36, 0, 0)
            struct.pack_into('<H', raw, off + 62, 0xFFFF)
            struct.pack_into('<i', raw, off + 81, -1)
            raw[off + 25] &= 0x7F
            raw[off + 26] &= 0xFE
        else:
            off = base + (rider - 1) * stride
            struct.pack_into('<i', raw, off + 81, -1)
            raw[off + 25] &= 0x7F
        fixed += 1
    return fixed


def build(cfg: dict, indepstr: int = 0) -> dict:
    arena = cfg['arena']
    # The test save is always named after the save it copies from
    # (``<save>Arena``), so there is no second name to keep in sync and the
    # arena can never drift from its source.
    game = f"{arena['save']}Arena"
    # Arena creation and hosting run the real engine, so the config can name
    # the install (``game_dir``, a Dominions 6 folder or the exe) instead of
    # requiring the DOM6_DIR environment variable.
    config.set_game_dir(cfg.get('game_dir'))
    player_cfg = cfg.get('player') or cfg.get('source') or {}
    provinces = [int(p) for p in player_cfg['provinces']]
    enemy_cfg = cfg.get('enemy') or {}
    mods = cfg.get('mods') or []
    global ITEM_MAX_ID
    ITEM_MAX_ID = _item_max_from_mods(mods)

    save_dir = _source_dir(arena)
    # Province ids are bounded by the source map, not by a guess: a 300
    # province cut hides every unit of a big map (sanguosha.map, 841
    # provinces, army at 556) while no bound at all lets the byte-step scan
    # pick up garbage.  Must happen before any .trn/.2h is read.
    trn_parse.set_map_provinces(trn_parse.map_provinces(save_dir))
    # The source nation is arena.own_nation (0 = autodetect from the save);
    # its id selects the nation's own files via file_name_base.
    explicit = int(arena.get('own_nation') or 0)
    source_nation = explicit or _detect_nation(save_dir, player_cfg)
    own_nation = _detect_own_nation(game, explicit, source_nation)
    print(f'source {save_dir.name}: nation {source_nation} '
          f'(own side in arena: {own_nation})')

    # Only the player's own files are ever read: ftherlnd is the world
    # state of a hotseat save (every nation's units) and another player's
    # .trn/.2h shows a scrubbed view of our side.
    src_raw, _ = _source_army(save_dir, source_nation, provinces)
    trn_path, trn_raw = _player_trn(save_dir, source_nation)
    # The player's orders file: fresher com records (battle scripts), and
    # the proof of which commanders are alive this turn.
    h2_path = trn_path.with_suffix('.2h')
    h2_raw = h2_path.read_bytes() if h2_path.exists() else None

    # Battle reports are picked interactively ONCE per province, over the
    # union of both province lists: a province listed by both sides must not
    # ask twice, and its pick must feed each army at most once.  The picks are
    # cached on the config dicts so the arena recreation retries of main() do
    # not ask again.  A picked province is not copied from its current
    # garrison/scout state.
    enemy_provs = enemy_cfg.get('provinces') or []
    if isinstance(enemy_provs, int):
        enemy_provs = [enemy_provs]
    all_provs = list(dict.fromkeys([int(p) for p in list(provinces)
                                    + list(enemy_provs)]))
    picks = player_cfg.get('_battle_report_picks')
    if picks is None:
        picks = _pick_battle_reports(trn_raw, all_provs,
                                     own_nation=source_nation)
        player_cfg['_battle_report_picks'] = picks
    (player_report_entries, enemy_report_entries,
     player_report_provs) = _split_report_entries(picks, source_nation)
    enemy_cfg['_battle_report_picks'] = enemy_report_entries
    province_copy = [p for p in provinces if p not in player_report_provs]

    # The .trn is the authoritative view of the player's army.  Copy exactly
    # the records standing in the requested provinces.
    src_units: list[dict] = _province_records(src_raw, province_copy,
                                              source_nation)
    units_raw = src_raw
    print(f'  unit source: {trn_path.name} '
          f'({len(src_units)} unit(s) of nation {source_nation} '
          f'in {province_copy})')
    # Debug mod units are never copied: a copied capital would otherwise
    # bring the pregame grant (46/9001/9002 and their mounts) along.
    n_before = len(src_units)
    src_units = _without_debug(units_raw, src_units)
    if len(src_units) < n_before:
        print(f'  excluded {n_before - len(src_units)} debug mod unit(s) '
              f'from the copied army')
    # A mount points at its rider's source uid (record +85).  If the rider is
    # not part of the copied set -- it fell this turn, it is another nation's
    # unit, or it is the pretender record handled separately -- the engine
    # aborts with "getfather: bad <uid>".  Drop only those orphan mounts; the
    # province's real units are still copied as-is.
    uids = {r['uid'] for r in src_units}
    kept = []
    for r in src_units:
        master = struct.unpack_from('<i', units_raw, r['pos'] + 85)[0]
        if master > 0 and master not in uids:
            continue
        kept.append(r)
    if len(kept) < len(src_units):
        print(f'  dropped {len(src_units) - len(kept)} orphan mount(s) '
              f'whose rider is not in the copied army')
    src_units = kept
    # Build write-specs from the source file so we preserve commander chains
    # (master=-2 for commanders, rider bit, mount→rider uid links).  Plain
    # ints lose this information — every rider would flatten to a soldier.
    src_specs = _army_unitspecs(units_raw, src_units)
    src_types = [s['type'] for s in src_specs]
    src_rec = _design_for(src_raw, source_nation)
    src_name = src_rec['god']
    print(f'  pretender "{src_name}", {len(src_types)} units from provinces '
          f'{provinces} (.trn {trn_path.name})')
    player_extra_specs = _custom_unit_specs(player_cfg.get('extra_units'))
    player_extra_start = len(src_specs)
    extra = [{'type': spec['id']} for spec in player_extra_specs]
    if extra:
        print(f'  extra units not in .trn: {len(extra)} ({[e["type"] for e in extra]})')
    src_specs += extra
    report_types = _report_units(trn_raw, player_cfg.get('battle_report') or [],
                                 'own')
    src_specs += [{'type': t} for t in report_types]

    # The player-side battle-report entries were split out above (a province in
    # both lists keeps its current garrison, so it is not listed here).  Their
    # units are appended to src_specs later, once the pretender chassis is
    # known, so the pretender itself is not duplicated as a soldier.

    # ---- enemy nation ----------------------------------------------------
    enemy_nation = _select_enemy_nation(
        gamedata.nations()[own_nation], arena.get('seed', 0),
        int(arena.get('enemy_nation') or 0))
    # The arena era follows the player's own nation: the source save fixes
    # which era the player's units and designs come from, and an enemy from
    # another era cannot share a game (its nation id is era-specific).
    player_nat = gamedata.nations()[own_nation]
    # ``arena.era`` overrides the era for one-age mods (OneAge_EAMALA puts
    # every nation, early/middle/late, into the Middle Age, so an early
    # nation like Marverni only exists there).
    era = int(arena.get('era') or player_nat.era)
    print(f'enemy nation: {enemy_nation.name} ({enemy_nation.id}), '
          f'arena era {era} (player {player_nat.name})')

    enemy_report_records: list[dict] = []
    enemy_extra_specs = _custom_unit_specs(enemy_cfg.get('extra_units'))
    enemy_extra_start_at: list[int] = []
    enemy_comp, enemy_report_cmdrs, enemy_scout_god = _enemy_army(
        trn_raw, enemy_cfg, enemy_report_records,
        enemy_extra_specs, enemy_extra_start_at, enemy_nation.id)
    enemy_extra_start = (enemy_extra_start_at[0]
                         if enemy_extra_start_at else len(enemy_comp))
    print(f'enemy army: {len(enemy_comp)} units')

    # ---- create / reuse the arena ---------------------------------------
    recreate = bool(arena.get('recreate'))
    fresh = recreate or not (config.save_dir(game) / 'ftherlnd').exists()
    _ensure_arena(game, era, player_nat, enemy_nation, mods,
                  map_name=str(arena.get('map') or '').strip(),
                  player_start=int(player_cfg.get('start_province') or 1),
                  enemy_start=int(enemy_cfg.get('start_province') or 5),
                  recreate=recreate, indepstr=indepstr)

    save = config.save_dir(game)
    ft = save / 'ftherlnd'
    backup = config.OUTPUT_DIR / f'{game}_ftherlnd_before_swap.bin'
    if fresh or not backup.exists():
        shutil.copyfile(ft, backup)
        print(f'NOTE: {backup.name} refreshed from the new ftherlnd')
    shutil.copyfile(backup, ft)
    raw = bytearray(ft.read_bytes())
    # World unit-id -> nation of THIS arena game, read once from the fresh
    # ftherlnd and reused for every turn-file transplant (turn-0 .trn files
    # cannot produce this map themselves).
    arena_uid_nation = _uid_nation_map(bytes(raw))

    # ---- transplant the player's pretender; give the enemy its bless -----
    enemy_rec = _design_for_or_none(src_raw, enemy_nation.id)
    if enemy_rec and not all(v < BLESS_COUNT for v in enemy_rec['vals']):
        # Some saves store an extra array before the pretender name, which the
        # record walk cannot tell apart from the bless array; such a record
        # parses to impossible bless ids (see _parse_design), so its bless must
        # not be copied into the arena design.
        print(f'  enemy design for nation {enemy_nation.id} did not parse '
              f'cleanly (vals {enemy_rec["vals"]})')
        enemy_rec = None
    if enemy_rec and enemy_rec['god']:
        print(f'  enemy bless from source save '
              f'(nation {enemy_nation.id} "{enemy_rec["god"]}"): '
              f'{blesses.describe(enemy_rec["vals"])}'
              + (f', magnitude entries {enemy_rec["extras"]}'
                 if enemy_rec['extras'] else ''))
        unknown = sorted({v for v in enemy_rec['vals'] if v >= blesses.ID_LIMIT})
        if unknown:
            print(f'  warning: source bless ids {unknown} are not real bless '
                  'effects (empty slots of the exe table)')
    else:
        # The source save's design entry for that nation is the Pretenders of
        # the World row the player sees: empty means the bless is not known
        # ("---" in that screen).  An unknown bless is never invented -- the
        # arena enemy keeps the arena's own design and gets no bless at all.
        print(f'  enemy bless for nation {enemy_nation.id} is not known in '
              'the source save -> no bless set')

    # Nation -> bytes that replace its design record in the arena.  Only the
    # player's own pretender is copied whole (scales, title, bless and name);
    # the enemy pretender is not the player's to copy, so the enemy keeps its
    # arena design and just receives the bless read from the source save —
    # unless enemy.pretender has an explicit chassis id configured (see below).
    # If player.pretender overrides the chassis we skip the player-side
    # transplant entirely — the arena's default name/bless/scales stay in
    # place and only the chassis (+ optional magic paths) are rewritten.
    names: list[tuple[int, str]] = [(own_nation, src_rec['god'])]
    swap: dict[int, bytes] = {own_nation: src_raw[src_rec['pos']:src_rec['end']]}
    # Nation -> the source design record whose bless (entries and ids) is
    # spliced into the arena's own record by _with_design.
    patch_design: dict[int, bytes] = {}
    if enemy_rec and (enemy_rec['extras'] or enemy_rec['vals']):
        patch_design[enemy_nation.id] = src_raw[enemy_rec['pos']:enemy_rec['end']]

    def _transplant(buf: bytearray,
                    uid_nation: dict[int, int] | None = None) -> bytearray:
        """Replace both pretenders' designs inside ``buf``.

        The pretender is stored three times per nation: a blurb, a commander
        record holding a live design block, and the nation design array.  The
        client shows the copy in the ``.trn`` of the turn, so ``buf`` may be
        either ftherlnd or a turn file.  A record can hold a second design
        block that the name/record pass does not reach; the last sweep rewrites
        every remaining copy of the old 9 byte path vector.

        ``uid_nation`` is the world unit-id -> nation map, taken from the
        arena ftherlnd and reused for every turn file: a turn-0 .trn omits
        or mis-stamps the god records, so deriving it from such a buffer
        would attribute both placeholder gods to the wrong nation.
        """
        # Both hotseat gods can share one forged placeholder name, so every
        # slot is attributed to ITS nation: unit id -> nation from the unit
        # table (ftherlnd) or the turn file records (.trn).
        if uid_nation is None:
            uid_nation = _uid_nation_map(bytes(buf))
        old = {}   # nation -> (old name, old path vector)
        for arena_nation, god_name in names:
            old_name = _design_for(bytes(buf), arena_nation)['god']
            old[arena_nation] = (old_name, _path_vector(buf, old_name))
        out = buf
        for arena_nation, god_name in names:
            old_name = old[arena_nation][0]
            if not old_name or old_name == god_name:
                continue
            src_slots = _god_slots(src_raw, god_name)
            if 'blurb' not in src_slots or 'name_record' not in src_slots:
                # The source save cannot see this nation's pretender
                # commander (an enemy god seen only through scouting): only
                # its design record is visible, so there is no blurb or
                # commander record to copy.  The design array swap below
                # still brings in the name, scales and bless.
                continue
            out = _copy_pretender(out, src_raw, old_name, god_name,
                                  nation=arena_nation, uid_nation=uid_nation)
        array_start, array_end, records = _design_array(bytes(out))
        new_array = bytearray()
        for rec in records:
            if rec['nation'] in swap:
                new_array += swap[rec['nation']]
            elif rec['nation'] in patch_design:
                new_array += _with_design(out[rec['pos']:rec['end']],
                                          patch_design[rec['nation']])
            else:
                new_array += out[rec['pos']:rec['end']]
        out = bytearray(bytes(out)[:array_start] + new_array
                        + bytes(out)[array_end:])

        # Leftover design blocks still carry the old paths; tell them apart
        # by the nearest new pretender name before the block.  The 9 byte
        # vector is only 9 path levels, so the same bytes occur by chance
        # inside the packed unit table; rewriting them there would garble
        # unit ids, so that range is skipped.
        unit_table = saveedit.find_unit_table(bytes(out))
        skip_lo, skip_hi = (0, 0) if unit_table is None else (
            unit_table[0], unit_table[0] + unit_table[1] * unit_table[2])
        for arena_nation, god_name in names:
            old_vec = old[arena_nation][1]
            new_vec = _path_vector(src_raw, god_name)
            # A source save that only has the nation's design record (an AI
            # nation) carries no blurb, so its path vector is unknown; keep
            # the old one instead of zeroing it.  An all-zero old vector is
            # the placeholder's (it has no paths at all) — matching that
            # would hit every zero run in the file, so leave it to the design
            # array swap, which already carries the source's paths.
            if (len(old_vec) != 9 or len(new_vec) != 9 or not any(old_vec)
                    or not any(new_vec) or old_vec == new_vec):
                continue
            pos = 0
            while True:
                off = bytes(out).find(old_vec, pos)
                if off < 0:
                    break
                if skip_lo <= off < skip_hi:
                    pos = off + 1
                    continue
                owner, best = None, -1
                for other_nation, other_name in names:
                    found = bytes(out).rfind(_enc(other_name), 0, off)
                    if found > best:
                        best, owner = found, other_nation
                if owner == arena_nation:
                    out[off:off + 9] = new_vec
                pos = off + 1
        return out

    for arena_nation, god_name in names:
        old_name = _design_for(bytes(raw), arena_nation)['god']
        if old_name:
            print(f'  arena nation {arena_nation} "{old_name}" -> "{god_name}"')
        else:
            print(f'  arena nation {arena_nation} has no pretender name; '
                  f'only its design record is replaced ("{god_name}")')
    if enemy_nation.id in patch_design:
        enemy_old = _design_for_or_none(bytes(raw), enemy_nation.id)
        print(f'  arena nation {enemy_nation.id} keeps its own pretender '
              f'"{enemy_old["god"] if enemy_old else ""}"; bless copied from '
              f'the source design only: '
              f'{blesses.describe(enemy_rec["vals"])}')
    raw = _transplant(raw, arena_uid_nation)

    # ---- pick target provinces ------------------------------------------
    player_choices = [int(p) for p in arena.get('target_provinces') or []]
    if not player_choices:
        player_choices = _nation_provinces(game, own_nation)
    if not player_choices:
        raise ValueError(f'no provinces for nation {own_nation}; set target_provinces')
    enemy_choices = _nation_provinces(game, enemy_nation.id)
    if not enemy_choices:
        raise ValueError(f'no provinces for enemy nation {enemy_nation.id}')

    # player.target_province / enemy.target_province pin where that side's
    # army is placed; both default to the side's start province.  The old
    # arena.target_province still works as the player's target.
    tp = arena.get('target_province', 'random')
    player_start = int(player_cfg.get('start_province') or 1)
    enemy_start = int(enemy_cfg.get('start_province') or 5)
    player_prov = int(player_cfg['target_province']) \
        if player_cfg.get('target_province') is not None \
        else (int(tp) if tp != 'random' else player_start)
    enemy_prov = int(enemy_cfg['target_province']) \
        if enemy_cfg.get('target_province') is not None else enemy_start
    print(f'player province: {player_prov} '
          f'(target {player_cfg.get("target_province") or player_start}, '
          f'choices {player_choices})')
    print(f'enemy province: {enemy_prov} '
          f'(target {enemy_cfg.get("target_province") or enemy_start}, '
          f'choices {enemy_choices})')

    # ---- write both armies ----------------------------------------------
    base, stride, count = saveedit.find_unit_table(bytes(raw))
    mount_pairs = _mount_pairs(bytes(raw), base, stride, count)
    god_type: int | None = None
    src_god_uid: int | None = None
    # The pretender may stand outside the copied provinces (Bananas:
    # Qinglong in 199, the garrison in 214).  Its own record is the god
    # record, so it replaces the chassis there instead of being counted
    # as an extra unit of the garrison.
    #
    # Pretender source priority: player.pretender config > battle report >
    # own save (.trn/.2h).  The battle report is read first because it also
    # remembers a god that died in the battle: its chassis stands in the
    # report's start-of-battle list and its VCR com record still carries
    # equipment, carried gems, magic paths and the battle script, while the
    # .trn has no record for a dead unit at all.
    own_chassis = gamedata.pretenders().get(own_nation, set())
    player_report_units, player_report_detail = _report_details(
        trn_raw, player_report_entries, 'own')
    save_god_type = ((trn_parse.pretender_type(h2_raw, src_name,
                                               chassis=own_chassis)
                      if h2_raw else None)
                     or trn_parse.pretender_type(src_raw, src_name,
                                                 chassis=own_chassis))
    player_report_god = next((d for d in player_report_detail
                              if d and d['type'] in own_chassis), None)
    src_god_type = (player_report_god['type']
                    if player_report_god is not None else save_god_type)
    god_type = src_god_type
    player_god_com: dict | None = None
    if player_report_god is not None:
        player_god_com = player_report_god.get('com')
        _unit = gamedata.units().get(src_god_type)
        print(f'  player pretender from battle report: {src_god_type} '
              f'({_unit.name if _unit else "?"}) '
              f'uid {player_report_god["uid"]}'
              + ('' if player_god_com else ' -- no com record in the report,'
                 ' equipment and gems unavailable'))
    elif save_god_type is not None:
        _unit = gamedata.units().get(save_god_type)
        print(f'  player pretender chassis from source save: {save_god_type} '
              f'({_unit.name if _unit else "?"})')

    # --- player.pretender override ---------------------------------------
    # If the config supplies a pretender spec (chassis + optional magic
    # paths) it replaces whatever the source save would have transplanted.
    player_pretender = player_cfg.get('pretender')
    player_god_paths: tuple[int, ...] | None = None
    player_override_chassis = False
    if isinstance(player_pretender, dict):
        paths = player_pretender.get('magic_paths')
        if paths is not None:
            player_god_paths = _paths_from_config(paths, 'player.pretender')
        player_pretender = player_pretender.get('id')
    if player_god_paths is not None and not player_pretender:
        raise ValueError('player.pretender magic_paths requires an id')
    if player_pretender:
        player_god_type = int(player_pretender)
        unit = gamedata.units().get(player_god_type)
        label = (f'{player_god_type} ({unit.name})' if unit
                 else str(player_god_type))
        if player_god_type not in gamedata.pretender_chassis():
            raise ValueError(
                f'player.pretender {label} is not a pretender chassis; '
                'the engine removes non-god-class units swapped into the '
                'god slot')
        if player_god_type != god_type:
            # Chassis changed — skip transplanting the source god's design.
            # The arena keeps its own default name/bless/scales and only the
            # chassis (+ magic paths) is rewritten.
            player_override_chassis = True
            god_type = player_god_type
            print(f'  player.pretender chassis override: '
                  f'{label} (source had {src_god_type})')
        else:
            # Same chassis as source — still transplant the source design.
            print(f'  player.pretender chassis matches source: {label}')

    src_god_rec: dict | None = None
    if src_god_type is not None:
        god_source = src_units
        if player_report_god is not None:
            # The god fought in a province whose army comes from a battle
            # report.  Its uid and, when it survived, its record come from
            # the report's start-of-battle snapshot; a god that died has no
            # .trn record at all, so there is nothing to transplant (the
            # report's com record still supplies its equipment and gems).
            src_god_uid = player_report_god.get('uid')
            if player_report_god.get('pos') is not None:
                src_god_rec = player_report_god
        else:
            # Which record is the pretender, though?  A same-type unit may
            # stand in the copied province while the god itself stands
            # elsewhere (Abysia's Slayer Sanguine garrison and a Slayer
            # Sanguine pretender share type 1967).  The pretender's com/name
            # record carries its own unit id, so only that record becomes the
            # arena god record; every other record stays a real unit.
            src_god_uid = _pretender_uid(units_raw, src_name,
                                        {r['uid'] for r in src_units})
            if src_god_uid is None and player_report_provs:
                # The pretender may stand in a province whose army is read
                # from a battle report, so it is not part of src_units.  Look
                # across all configured player provinces so the arena god
                # still gets its .trn record (equipment, magic paths).
                god_source = _province_records(units_raw, provinces,
                                               source_nation)
                src_god_uid = _pretender_uid(
                    units_raw, src_name, {r['uid'] for r in god_source})
        if player_override_chassis:
            # Chassis changed — the source god is no longer the arena god,
            # so its record stays as a plain unit (no drop needed, no
            # conflict with the new arena god slot).  Also skip
            # transplanting the source name/design into the arena.
            names = [(n, nm) for n, nm in names if n != own_nation]
            swap.pop(own_nation, None)
            god_unit = gamedata.units().get(god_type)
            print(f'  arena player pretender chassis: {god_type} '
                  f'({god_unit.name if god_unit else "?"})')
        else:
            drop = (next((r for r in src_units if r['uid'] == src_god_uid),
                         None)
                    if src_god_uid is not None else None)
            if drop is None and src_god_uid is None and any(
                    s['type'] == god_type for s in src_specs):
                drop = next((r for r in src_units if r['type'] == god_type),
                            None)
            if drop is not None:
                src_god_rec = drop
                src_specs = [s for s in src_specs if s.get('src_uid') != drop['uid']]
                src_units.remove(drop)
                player_extra_start -= 1
            elif (src_god_rec is None and src_god_uid is not None
                  and god_source is not src_units):
                # The god's province is battle-report sourced, so its record
                # is outside src_units; still transplant the .trn record.
                src_god_rec = next(
                    (r for r in god_source if r['uid'] == src_god_uid), None)

    enemy_pretender = enemy_cfg.get('pretender')
    enemy_god_paths: tuple[int, ...] | None = None
    enemy_pretender_id: int | None = None
    if isinstance(enemy_pretender, dict):
        paths = enemy_pretender.get('magic_paths')
        if paths is not None:
            enemy_god_paths = _paths_from_config(paths, 'enemy.pretender')
        enemy_pretender_id = enemy_pretender.get('id')
    elif isinstance(enemy_pretender, int):
        enemy_pretender_id = enemy_pretender
    if enemy_god_paths is not None and not enemy_pretender_id:
        raise ValueError('enemy.pretender magic_paths requires an id')
    enemy_paths_from_config = enemy_god_paths is not None

    # Pretender source priority: enemy.pretender config > battle report >
    # scout report.  A chassis in the copied side's start-of-battle list is
    # that nation's only god; unlike a scout sighting, the report also holds
    # the god's com record (equipment, carried gems, magic paths and battle
    # script), so it is preferred over the scout report.
    enemy_report_god = next(
        (d for d in enemy_report_records
         if d and d['type'] in gamedata.pretender_chassis()), None)
    enemy_god_com: dict | None = None
    reported_god = None            # scout report sighting
    if not enemy_pretender_id and enemy_report_god is not None:
        enemy_pretender_id = enemy_report_god['type']
        enemy_god_com = enemy_report_god.get('com')
    elif not enemy_pretender_id and enemy_scout_god:
        reported_god = int(enemy_scout_god['id'])
        enemy_pretender_id = reported_god
    if enemy_pretender_id:
        enemy_god_type = int(enemy_pretender_id)
        unit = gamedata.units().get(enemy_god_type)
        label = (f'{enemy_god_type} ({unit.name})' if unit
                 else str(enemy_god_type))
        if enemy_god_type not in gamedata.pretender_chassis():
            raise ValueError(
                f'enemy.pretender {label} is not a pretender chassis; '
                'the engine removes non-god-class units swapped into the '
                'god slot')
        if enemy_god_com is not None:
            # The report's com record dictates how the god actually spent
            # its paths and what it carried, so the tail is copied whole
            # instead of the chassis defaults.
            enemy_god_paths = tuple(
                enemy_god_com['tail'][T_PATHS:T_PATHS + 10])
            print(f'  enemy pretender from battle report: {label} '
                  f'uid {enemy_report_god["uid"]}; equipment, gems, magic '
                  f'paths {_path_text(enemy_god_paths)} and script copied')
        elif reported_god is not None:
            # A sighting shows the chassis, never how its god spent the
            # paths, so the chassis' own defaults from units.csv are used.
            enemy_god_paths = unit.paths
            print(f'  enemy pretender from scout report '
                  f'({enemy_scout_god["where"]}): {label}; '
                  f'magic paths default to {_path_text(enemy_god_paths)}')
            if enemy_scout_god.get('name'):
                print(f'  NOTE: the report names that god '
                      f'"{enemy_scout_god["name"]}"; the arena keeps its own '
                      f'pretender name')
        # Full design swap when source save exposes this nation's design and
        # the user did NOT provide explicit magic_paths (use native paths).
        if enemy_rec and not enemy_paths_from_config:
            swap[enemy_nation.id] = src_raw[enemy_rec['pos']:enemy_rec['end']]
            patch_design.pop(enemy_nation.id, None)
            names.append((enemy_nation.id, enemy_rec['god']))
            print(f'  enemy.pretender chassis {label}; '
                  f'swapping full design from source save '
                  f'(native paths + bless + scales + name)')
        else:
            print(f'  enemy pretender chassis: {label}')
    else:
        # No enemy.pretender configured — keep arena default chassis/name.
        # Still copy bless from source save when available (patch_bless was
        # populated above from enemy_rec/enemy_bless, so nothing to pop).
        enemy_god_type = None
        print(f'  enemy pretender: not set (arena default kept)')

    enemy_god_index: int | None = None
    enemy_comp = list(enemy_comp)
    enemy_specs: list[dict] = [spec if isinstance(spec, dict) else {'type': spec}
                               for spec in enemy_comp]
    if enemy_god_type is not None and enemy_god_type in enemy_comp:
        # Only meaningful when enemy_god_type comes from battle-report input
        # (not from config — extra_units can't hold a pretender chassis).
        # Use the report's own slot index: a same-type unit may stand in
        # front of the god, and removing by type alone would take that one.
        enemy_god_index = (enemy_report_god['comp_index']
                           if enemy_report_god is not None
                           else enemy_comp.index(enemy_god_type))
        enemy_comp.pop(enemy_god_index)
        enemy_specs.pop(enemy_god_index)

    # Battle-report units must carry their own current hp: the record they
    # land on is borrowed from the arena's old garrison and keeps that
    # garrison unit's hp, and the host recycles (deletes) a unit whose hp
    # happens to be the poison value -- 88 of 127 copied Sage-Priests vanished
    # that way.  ``comp_index`` points into the pre-removal army, so shift it
    # when the god was taken out in front of the entry.
    for rec in enemy_report_records:
        idx = rec['comp_index']
        if enemy_god_index is not None:
            if idx == enemy_god_index:
                continue
            if idx > enemy_god_index:
                idx -= 1
        hp = rec.get('hp')
        if hp and 0 <= idx < len(enemy_specs):
            enemy_specs[idx]['hp'] = hp

    if enemy_god_type is not None and any(
            spec['id'] == enemy_god_type for spec in enemy_extra_specs):
        raise ValueError(
            f'enemy extra unit id {enemy_god_type} conflicts with '
            'enemy.pretender; remove it from extra_units')
    player_extra_cmdrs = _custom_commanders(player_extra_specs)
    # Scout report commanders sit at the front of the army (index into
    # enemy_comp, hence the explicit base 0); configured extras follow
    # enemy_extra_start.
    enemy_extra_cmdrs = (_custom_commanders(enemy_extra_specs)
                         + enemy_report_cmdrs)
    if enemy_god_index is not None and enemy_god_index < enemy_extra_start:
        enemy_extra_start -= 1

    # The debug mod hands every capital free commanders at game creation:
    # 9001 Debug Sensei, 9002 mounted tester and 46 Mounted Commander.
    # Both players' grants are arena setup, not part of either copied army,
    # so they stay untouched in their capitals; their mounts follow
    # automatically.  Restrict the keep set to the two players because type
    # 46 can also occur in independent garrisons.
    keep_offs = {o for o in _keep_offsets(bytes(raw), base, stride, count,
                                          DEBUG_TYPES)
                 if struct.unpack_from('<H', raw, o + 64)[0]
                 in (own_nation, enemy_nation.id)}
    if keep_offs:
        kept = sorted({struct.unpack_from('<H', raw, o + 32)[0]
                       for o in keep_offs})
        print(f'  keeping {len(keep_offs)} unit record(s) untouched '
              f'(types {kept})')

    # Append the player's own-side battle-report units now that the pretender
    # chassis is known.  Only the pretender itself is skipped (it becomes the
    # arena god, with its .trn record transplanted) -- every other chassis
    # type is kept as a soldier, exactly like the enemy side.  The list is
    # the report's start-of-battle composition, so units that died in the
    # battle are part of it too.
    player_report_records: list[dict] = []
    player_report_count = 0
    for unit_type, detail in zip(player_report_units, player_report_detail):
        if unit_type == god_type and not player_override_chassis:
            continue
        local_index = player_report_count
        src_specs.append({'type': unit_type, 'hp': (detail or {}).get('hp')})
        player_report_count += 1
        if detail is not None:
            player_report_records.append({**detail, 'report_index': local_index})
    player_report_expected_cmdrs = sum(
        1 for r in player_report_records
        if r.get('com') is not None
        or _trn_commander(trn_raw, r['uid']) is not None)
    if player_report_count:
        counts: dict[int, int] = {}
        for t in player_report_units:
            if t == god_type and not player_override_chassis:
                continue
            counts[t] = counts.get(t, 0) + 1
        print(f'  player battle report: {player_report_count} unit(s) '
              f'{sorted(counts.items())}')

    # The unit table must hold both full armies, both god records and the
    # kept debug grant.  Its size is fixed at creation (the random
    # independent garrisons are most of it), so a short table can only be
    # fixed by recreating the arena.
    required = len(src_specs) + 1 + len(enemy_specs) + 1 + len(keep_offs)
    if count < required:
        raise ArenaCapacityError(
            f'unit table holds {count} records, need {required} '
            f'(own {len(src_specs)} + enemy {len(enemy_specs)} + 2 gods '
            f'+ {len(keep_offs)} kept debug)', count, required)

    # The smaller army goes first: it keeps only the records it needs, and
    # the surplus records it owns are handed over to the other nation (the
    # table's total capacity is fixed).
    #
    # IMPORTANT: leftover records MUST NOT be left with province (0,0), or
    # the host treats them as "in enemy territory" (lnr 0) and kills them.
    # Instead they get the province of whichever nation ends up owning them,
    # so the engine never flags them.
    if len(enemy_specs) <= len(src_specs):
        e_god, e_used, e_left = _write_nation_army(
            raw, base, stride, count, enemy_nation.id, enemy_specs,
            enemy_prov, god_type=enemy_god_type, protected=[own_nation],
            skip=keep_offs)
        e_slots = e_used[1:]
        _apply_master_chain(raw, e_slots, enemy_specs)
        for off in e_left:
            struct.pack_into('<H', raw, off + 64, 0)
            struct.pack_into('<H', raw, off + 32, 0)
            struct.pack_into('<HH', raw, off + 36, player_prov, player_prov)
        p_god, p_used, p_left = _write_nation_army(
            raw, base, stride, count, own_nation, src_specs,
            player_prov, god_type=god_type, protected=[enemy_nation.id],
            skip=keep_offs)
        p_slots = p_used[1:]
        _apply_master_chain(raw, p_slots, src_specs)
        for off in p_left:
            struct.pack_into('<H', raw, off + 64, 0)
            struct.pack_into('<H', raw, off + 32, 0)
            struct.pack_into('<HH', raw, off + 36, player_prov, player_prov)
    else:
        p_god, p_used, p_left = _write_nation_army(
            raw, base, stride, count, own_nation, src_specs,
            player_prov, god_type=god_type, protected=[enemy_nation.id],
            skip=keep_offs)
        p_slots = p_used[1:]
        _apply_master_chain(raw, p_slots, src_specs)
        for off in p_left:
            struct.pack_into('<H', raw, off + 64, 0)
            struct.pack_into('<H', raw, off + 32, 0)
            struct.pack_into('<HH', raw, off + 36, enemy_prov, enemy_prov)
        e_god, e_used, e_left = _write_nation_army(
            raw, base, stride, count, enemy_nation.id, enemy_specs,
            enemy_prov, god_type=enemy_god_type, protected=[own_nation],
            skip=keep_offs)
        e_slots = e_used[1:]
        _apply_master_chain(raw, e_slots, enemy_specs)
        for off in e_left:
            struct.pack_into('<H', raw, off + 64, 0)
            struct.pack_into('<H', raw, off + 32, 0)
            struct.pack_into('<HH', raw, off + 36, enemy_prov, enemy_prov)

    # No player.pretender spec in the config means the pretender is the source
    # save's own god, so its record is copied too (experience, hit points and
    # everything else the chassis carries).  Only the identity and links the
    # arena needs stay local.
    if not player_pretender and src_god_rec is not None:
        _copy_god_record(raw, p_god, units_raw, src_god_rec,
                         player_prov, own_nation)
        print(f'  player pretender record copied from source save '
              f'(uid {src_god_rec["uid"]})')

    # Every independent garrison the game created is removed, not just those
    # in the two battle provinces: the arena must always have independent
    # strength 0 (the creation-time --indepstr is only a table size lever).
    neutral = _clear_independents(raw, base, stride, count,
                                  {own_nation, enemy_nation.id})
    if neutral:
        print(f'  cleared {len(neutral)} independent unit(s); '
              f'independent strength stays 0')

    # Records we rewrote must not stay claimed by a commander record: the
    # host aborts with 'unit2com inconsistency' otherwise.  The gods' own
    # com records (their unit ids) are the only ones worth keeping.
    def _ids(offsets: list[int]) -> set[int]:
        return {(off - base) // stride + 1 for off in offsets}

    # e_slots / p_slots are the combat unit slots (excluding god) — these we
    # INTEND to be commanders with their master chains intact.  Only the
    # leftover records (type=0, province set to the owning nation's home)
    # should be fully cleared from their old command structure.  The neutral
    # clears are also full wipes.
    touched = _ids(e_used + e_left + p_used + p_left + neutral)
    # A surplus record handed to the other nation is written AGAIN by that
    # nation's _write_nation_army (the caller moves it before the second
    # write).  It must not be wiped here afterwards: clearing it would drop
    # the mount chain (master -> -1, rider/mount bits -> 0) that the second
    # write just set, leaving those cavalry units unmounted in a state the
    # engine never produces itself.
    written = set(e_used) | set(p_used)
    clear_all = [off for off in e_left + p_left + neutral
                 if off not in written]

    for off in clear_all:
        if off in (e_god, p_god):
            continue
        struct.pack_into('<H', raw, off + 62, 0xFFFF)
        struct.pack_into('<I', raw, off + 81, 0xFFFFFFFF)
        raw[off + 25] &= 0x7F
        raw[off + 26] &= 0xFE

    # For the player/enemy combat slots we WROTE (and _apply_master_chain
    # already patched), ONLY clear the com/squad reference at +62 — leave
    # master/rider alone because that's what we just set intentionally.
    for off in e_slots + p_slots:
        struct.pack_into('<H', raw, off + 62, 0xFFFF)
    orphaned = _repair_mount_pairs(raw, base, stride, count, mount_pairs,
                                   touched)
    if orphaned:
        print(f'  detached {orphaned} orphaned mount/rider pair(s)')
    keep = {(e_god - base) // stride + 1, (p_god - base) // stride + 1}
    # Commander identity = has a com record (NOT master field — master==-2
    # means "rider", i.e. a unit that rides a mount, not a commander).
    # The orders file is the proof of which commanders are alive: it carries
    # a com record for every live commander (even marching ones — what it can
    # lack is their *unit* record).  The .trn additionally holds stale text
    # records — dead mercenary companies ("Rozul's Red Raptors"), province
    # names ("Emerald Lake") — whose bytes false-positive the com record
    # match; transplanted, those abort the host ("bad gems"/"twin
    # commanders").  Only a save without any orders file falls back to .trn.
    expected_cmdrs = 0
    for r in src_units:
        if r['uid'] == src_god_uid:
            continue
        if _source_com(h2_raw, src_raw, r['uid']) is not None:
            expected_cmdrs += 1
    enemy_expected_cmdrs = sum(
        1 for r in enemy_report_records
        if r['comp_index'] != enemy_god_index
        and (r.get('com') is not None
             or _trn_commander(trn_raw, r['uid']) is not None))
    scrubbed = _scrub_commanders(
        raw, base, stride, count, touched, keep,
        limit=_design_array(bytes(raw))[0],
        required=(expected_cmdrs + enemy_expected_cmdrs
                  + len(player_extra_cmdrs) + len(enemy_extra_cmdrs)
                  + player_report_expected_cmdrs))
    if scrubbed:
        print(f'  prepared {len(scrubbed)} commander record slot(s)')

    # Which types actually led units: the orders file list when present,
    # else the .trn one.
    cmdr_counts = (trn_parse.commander_type_counts(h2_raw, set(province_copy))
                   if h2_raw else {})
    if not cmdr_counts:
        cmdr_counts = trn_parse.commander_type_counts(src_raw,
                                                      set(province_copy))

    # ---- transplant named commanders: name, squads and battle orders ------
    # A .trn source stores each commander as a com record (name, squad slots,
    # orders tail) plus the squad id at +32 of each member's unit record.
    # Re-arming a blank com slot loses all of that, so every source commander
    # that carries a com record gets its slot replaced wholesale: its own
    # name, freshly allocated squad ids and the copied orders tail.  The
    # splices change the file length, so they are applied last.
    com_splices: list[tuple[int, int, bytes]] = []   # (start, end, record)
    reserved: set[int] = set()                       # arena uids with a real com
    arena_uid: dict[int, int] = {}                   # source uid -> arena uid
    if src_units and scrubbed:
        uid_at = {r['uid']: r for r in src_units}
        # STRICT per-id mapping: source uid -> the arena slot that received
        # exactly that source unit's type (p_used was written from src_comp,
        # i.e. src_units in order).  A mismatch here would hand a commander
        # record to the wrong unit ("equip copied wrong"), so it is fatal
        # rather than silently positional.
        # src_comp is src_units' types in order, possibly followed by
        # battle-report / extra units; the first len(src_units) slots are
        # therefore exactly the copied province units.
        arena_slots = p_used[1:1 + len(src_units)]
        if len(arena_slots) != len(src_units):
            raise ValueError(
                f'strict army mapping mismatch: {len(src_units)} source '
                f'units but {len(arena_slots)} arena slots')
        for r, off in zip(src_units, arena_slots):
            slot_type = struct.unpack_from('<H', raw, off + 32)[0]
            if slot_type != r['type']:
                raise ValueError(
                    f'strict army mapping mismatch: source uid {r["uid"]} '
                    f'type {r["type"]} landed on an arena slot holding type '
                    f'{slot_type}')
            arena_uid[r['uid']] = (off - base) // stride + 1
        # The validated god uid (its name record points at a unit that is
        # actually present in the copied provinces); fall back to the raw
        # name-record uid only when that lookup had nothing.
        god_uid = src_god_uid
        if god_uid is None:
            god_slot = _god_slots(src_raw, src_name).get('name_record')
            god_uid = (struct.unpack_from('<I', src_raw,
                                          god_slot + len(_enc(src_name)) + 1)[0]
                       if god_slot is not None else None)
        # Squad membership: the orders file is the current state and wins over
        # the .trn, which is the turn-start snapshot (Bananas: the .trn has
        # -1 for every Bakemono-Sho that the .2h has already put in a squad).
        # Its squad ids are also the ones the com records above quote, so both
        # sides of the assignment must come from the same file.
        h2_squad: dict[int, int] = {}
        if h2_raw:
            for r2 in trn_parse.unit_records(h2_raw):
                h2_squad[r2['uid']] = struct.unpack_from(
                    '<I', h2_raw, r2['pos'] + 32)[0]
        stamped: dict[int, list[int]] = {}
        for r in src_units:
            sq = h2_squad.get(r['uid'])
            if sq is None:                 # not in the orders file: use .trn
                sq = struct.unpack_from('<I', src_raw, r['pos'] + 32)[0]
            if sq != 0xFFFFFFFF:
                stamped.setdefault(sq, []).append(r['uid'])
        max_squad = 0
        for k in range(count):
            v = struct.unpack_from('<I', raw, base + k * stride + 28)[0]
            if v != 0xFFFFFFFF:
                max_squad = max(max_squad, v)
        taken: set[int] = set()   # arena uids already assigned to a squad
        h2_commanders: list[tuple[int, str, int, list[int], bytes]] = []
        # Every live source commander must receive a record.  Slots scrubbed
        # from replaced arena commanders are used first; _scrub_commanders
        # extends the chain when the preserved Debug grants leave too few.
        #
        # SQUAD ASSIGNMENT STRATEGY:
        #   1. Collect all (r, com) pairs first; do NOT consume scrubbed yet.
        #   2. Sort by priority:
        #        pri 0 = com['squads'] has at least one slot still present in
        #                stamped (the .2h/.trn com record is authoritative for
        #                which squad slots were INTENDED; only the stale ones
        #                differ)
        #        pri 1 = com['squads'] exists but none of its slots are in
        #                stamped (e.g. Kinyasu's slot 1339838 was recycled;
        #                this commander needs renewal from stamped leftovers)
        #        pri 2 = com['squads'] is empty (Scout, etc.; no original
        #                squad plan — skip auto-assignment)
        #   3. For each commander in order:
        #        Part A — consume valid_slots from stamped (most certain)
        #        Part B — (pri 0 & 1 only) pick up remaining stamped squads
        #                from the same province, smallest first
        #        Part C — pri 2 only gets squads if literally none were taken
        #                by pri 0/1 (shouldn't happen for a healthy army)
        def _try_assign_squad(sq_id: int, cmdr_prov: int) -> list[int]:
            """Try to assign a stamped squad to this commander's province.

            Returns the list of chosen arena uids (may be empty), updates
            ``taken``, increments ``max_squad``, and patches ``raw``.
            """
            members = [m for m in stamped.get(sq_id, [])
                       if m in arena_uid
                       and arena_uid[m] not in taken
                       and uid_at[m]['province'] == cmdr_prov]
            if not members:
                return []
            # The .2h squad is copied as it is, mixed unit types included:
            # Hanif's squad 1337346 is 49 Bakemono-Sho + 1 O-bakemono, and
            # keeping only the majority type silently dropped the O-bakemono
            # from the formation.
            nonlocal max_squad
            max_squad += 1
            chosen_auids = []
            for u in members:
                a = arena_uid[u]
                taken.add(a)
                chosen_auids.append(a)
                struct.pack_into('<I', raw, base + (a - 1) * stride + 28,
                                 max_squad)
            return chosen_auids

        # --- Phase 1: collect and sort commanders by priority ---
        cmdr_queue: list[tuple[int, dict, dict, list[int], int]] = []
        # (priority, r, com, valid_slots, cmdr_prov)
        for r in src_units:
            if r['uid'] == god_uid or r['uid'] not in arena_uid:
                continue
            # Commander identity = has a com record (NOT master field —
            # master==-2 means "rider", a unit that rides a mount).  The
            # orders file proves the commander is alive (see the matching
            # note above); the .trn alone only proves the name was mentioned.
            com = _source_com(h2_raw, src_raw, r['uid'])
            if com is None:
                continue
            valid = [s for s in com['squads'] if s in stamped]
            stale = [s for s in com['squads'] if s not in stamped]
            if valid:
                pri = 0
            elif stale:
                pri = 1
            else:
                pri = 2
            cmdr_queue.append((pri, r, com, valid, r['province']))
        cmdr_queue.sort(key=lambda x: (x[0], -len(x[3])))

        # --- Phase 2: process each commander in priority order ---
        for pri, r, com, valid_slots, cmdr_prov in cmdr_queue:
            if not scrubbed:
                raise RuntimeError(
                    f'ran out of freed com slots before transplanting '
                    f'commander uid {r["uid"]} (type {r["type"]}); '
                    f'{len(h2_commanders)} of {expected_cmdrs} done')
            comid, c_start, c_uidpos = scrubbed.pop(0)
            auid = arena_uid[r['uid']]
            cmdr_type = r['type']
            new_squads: list[tuple[int, int]] = []
            n_members = 0
            unit_name = gamedata.units().get(cmdr_type)

            # --- Part A: consume valid_slots (most certain) ---
            for sq in valid_slots:
                assigned = _try_assign_squad(sq, cmdr_prov)
                if assigned:
                    new_squads.append((max_squad, len(assigned)))
                    n_members += len(assigned)

            # --- Part B (pri 0 & 1 only): leftover stamped squads same prov ---
            # Only take enough to reach the com record's original slot count.
            # A pri-0 commander whose valid_slots already match or exceed its
            # original count gets nothing here.  A pri-1 commander (all stale)
            # gets exactly ``len(com['squads'])`` slots from stamped.
            if pri <= 1:
                target_slots = len(com['squads'])
                need = max(0, target_slots - len(valid_slots))
                if need > 0:
                    leftover = sorted(
                        (sq for sq, members in stamped.items()
                         if any(m in arena_uid and arena_uid[m] not in taken
                                and uid_at[m]['province'] == cmdr_prov
                                for m in members)),
                        key=lambda sq: len(stamped[sq])
                    )
                    for sq in leftover:
                        if need <= 0:
                            break
                        assigned = _try_assign_squad(sq, cmdr_prov)
                        if assigned:
                            new_squads.append((max_squad, len(assigned)))
                            n_members += len(assigned)
                            need -= 1

            # --- Part C (pri 2 only): safety net — skip, this commander has
            # no original slots so should not inherit leftovers by default ---

            tail = bytearray(com['tail'])
            if struct.unpack_from('<I', tail, T_PROV)[0]:
                struct.pack_into('<I', tail, T_PROV, player_prov)
            if struct.unpack_from('<I', tail, T_UIDREF)[0]:
                struct.pack_into('<I', tail, T_UIDREF,
                                 arena_uid.get(struct.unpack_from('<I', tail, T_UIDREF)[0], 0))
            # a commander's own unit record carries the no-squad marker
            struct.pack_into('<I', raw, base + (auid - 1) * stride + 28,
                             0xFFFFFFFF)
            com_splices.append((c_start, c_uidpos + COM_BODY,
                                _com_record(comid, com['name'], auid,
                                            _squad_slots(new_squads),
                                            bytes(tail))))
            h2_commanders.append((comid, com['name'], auid,
                                  _squad_slots(new_squads), bytes(tail)))
            reserved.add(auid)
            if cmdr_counts.get(r['type'], 0) > 0:
                cmdr_counts[r['type']] -= 1
            print(f'  commander "{com["name"]}" '
                  f'({unit_name.name if unit_name else cmdr_type}) kept as com '
                  f'{comid}: {len(new_squads)} squad(s), {n_members} units, '
                  f'name + orders copied')

        # The client draws squad attachment and battle scripts from the
        # orders file, so the arena .2h gets the same records: the source
        # god's record plus one per transplanted commander.
        if h2_raw is not None and len(h2_commanders) != expected_cmdrs:
            raise RuntimeError(
                f'commander copy incomplete: {len(h2_commanders)} of '
                f'{expected_cmdrs} source records transplanted')
        if h2_raw and (h2_commanders or player_god_com is not None):
            # Priority for the god's own com record: the battle report's VCR
            # record (battle-time equipment, gems, paths and script), else the
            # .2h, else the .trn.
            god_com = (player_god_com
                       or (_trn_commander(h2_raw, god_uid) if god_uid else None))
            if god_com is None and god_uid:
                # The .2h only lists commanders with orders; a sleeping
                # pretender has no record there at all.  Without the fallback
                # the arena .2h got an all-zero tail, and the client draws the
                # pretender's paths, items, gems and battle script from it --
                # the copy showed a blank god.  The .trn record carries them.
                god_com = _trn_commander(src_raw, god_uid)
            gt = bytearray(god_com['tail']) if god_com else bytearray(COM_TAIL)
            if struct.unpack_from('<I', gt, T_PROV)[0]:
                struct.pack_into('<I', gt, T_PROV, player_prov)
            if struct.unpack_from('<I', gt, T_UIDREF)[0]:
                struct.pack_into('<I', gt, T_UIDREF,
                                 arena_uid.get(struct.unpack_from('<I', gt, T_UIDREF)[0], 0))
            _write_arena_h2(
                save / (gamedata.nations()[own_nation].file_name_base + '.2h'),
                src_name, (p_god - base) // stride + 1, bytes(gt),
                h2_commanders)

    # Battle-report commanders on the enemy side carry their full com record
    # in the player's own .trn: name, squads, battle orders and equipment.
    # Transplant those records as well; simply re-arming a blank com slot
    # would leave the copied commander without its source items.
    enemy_h2_cmdrs: list[tuple[int, str, int, list[int], bytes]] = []
    if enemy_report_records and scrubbed:
        slots_by_index = {i: off
                          for i, off in enumerate(e_used[1:1 + len(enemy_specs)])}
        uid_at = {r['uid']: r for r in enemy_report_records}
        report_uid: dict[int, int] = {}
        for r in enemy_report_records:
            idx = r['comp_index']
            if idx == enemy_god_index:
                continue
            if enemy_god_index is not None and idx > enemy_god_index:
                idx -= 1
            off = slots_by_index.get(idx)
            if off is None:
                raise ValueError(
                    f'battle-report unit uid {r["uid"]} maps outside the '
                    f'enemy army (composition index {r["comp_index"]})')
            slot_type = struct.unpack_from('<H', raw, off + 32)[0]
            if slot_type != r['type']:
                raise ValueError(
                    f'strict battle-report mapping mismatch: source uid '
                    f'{r["uid"]} type {r["type"]} landed on arena slot '
                    f'holding type {slot_type}')
            report_uid[r['uid']] = (off - base) // stride + 1

        # Build the squad membership table.  Each unit's "real" squad id
        # lives in the VCR snapshot block of the battle report (fsterlnd
        # format: uid at +0, squad at +28).  The player's own .trn only
        # carries units it can see, so many copied enemy units have no
        # .trn record at all (pos is None); their squad id must come
        # from the VCR block instead.  Build that lookup table first.
        vcr_sq: dict[int, int] = {}
        for pick in enemy_cfg.get('_battle_report_picks') or []:
            prov = int(pick['province'])
            side = pick['copy']
            rep = [r for r in trn_parse.battle_reports(trn_raw, prov)
                   if (side == 'attacker' and r['attacker'] == pick.get('attacker'))
                   or (side == 'defender' and r['defender'] == pick.get('defender'))]
            if not rep:
                continue
            if 'seq' in pick and pick['seq'] < len(rep):
                rep = rep[pick['seq']]
            else:
                rep = rep[0]
            side_nat = rep[side]
            snaps = _scan_vcr_snapshots(trn_raw, rep['vcr'], rep['bcd'],
                                        side_nat)
            for uid, info in snaps.items():
                if info['squad'] != 0xFFFFFFFF:
                    vcr_sq[uid] = info['squad']

        stamped: dict[int, list[int]] = {}
        for r in enemy_report_records:
            sq = None
            if r['pos'] is not None:
                sq = struct.unpack_from('<I', trn_raw, r['pos'] + 32)[0]
            if sq is None and r.get('uid') in vcr_sq:
                sq = vcr_sq[r['uid']]
            if sq is not None and sq != 0xFFFFFFFF:
                stamped.setdefault(sq, []).append(r['uid'])
        max_squad = 0
        for k in range(count):
            v = struct.unpack_from('<I', raw, base + k * stride + 28)[0]
            if v != 0xFFFFFFFF:
                max_squad = max(max_squad, v)
        taken: set[int] = set()
        copied = 0
        skipped = 0
        for r in enemy_report_records:
            auid = report_uid.get(r['uid'])
            if auid is None:
                continue
            com = r.get('com') or _trn_commander(trn_raw, r['uid'])
            if com is None:
                continue
            com_tail = com.get('tail') or b''
            if len(com_tail) != 181:
                skipped += 1
                print(f'  NOTE: battle-report commander uid {r["uid"]} '
                      f'(type {r["type"]}) has a {len(com_tail)}-byte com '
                      f'tail (expected 181); name and equipment not copied')
                continue
            # Plan the squads first; a com leading no unit would attach
            # equipment to an empty leader, which the host rejects with
            # "bad equip".
            plan: list[list[int]] = []
            for sq in com['squads']:
                members = [u for u in stamped.get(sq, [])
                           if u in report_uid and report_uid[u] not in taken]
                if not members:
                    continue
                plan.append(members)
                for u in members:
                    taken.add(report_uid[u])
            n_members = sum(len(m) for m in plan)
            if not scrubbed:
                raise RuntimeError(
                    f'ran out of freed com slots before enemy commander '
                    f'uid {r["uid"]} (type {r["type"]})')
            comid, c_start, c_uidpos = scrubbed.pop(0)
            new_squads: list[int] = []
            for chosen in plan:
                max_squad += 1
                new_squads.append(max_squad)
                for u in chosen:
                    a = report_uid[u]
                    struct.pack_into('<I', raw, base + (a - 1) * stride + 28,
                                     max_squad)
            tail = bytearray(com_tail)
            if struct.unpack_from('<I', tail, T_PROV)[0]:
                struct.pack_into('<I', tail, T_PROV, enemy_prov)
            if struct.unpack_from('<I', tail, T_UIDREF)[0]:
                struct.pack_into('<I', tail, T_UIDREF,
                                 report_uid.get(struct.unpack_from('<I', tail, T_UIDREF)[0], 0))
            struct.pack_into('<I', raw, base + (auid - 1) * stride + 28,
                             0xFFFFFFFF)
            slots = _squad_slots(list(zip(new_squads, map(len, plan))))
            com_splices.append((c_start, c_uidpos + COM_BODY,
                                _com_record(comid, com['name'], auid,
                                            slots, bytes(tail),
                                            keep_layout=True)))
            enemy_h2_cmdrs.append((comid, com['name'], auid, slots,
                                   bytes(tail)))
            reserved.add(auid)
            copied += 1
            unit = gamedata.units().get(r['type'])
            print(f'  enemy commander "{com["name"]}" '
                  f'({unit.name if unit else r["type"]}) kept as com {comid}: '
                  f'{len(new_squads)} squad(s), {n_members} units, '
                  f'name + orders + equipment copied')
        if skipped:
            print(f'  skipped {skipped} battle-report commander(s) that lead '
                  f'no unit or carry a malformed com record')
        if copied + skipped != enemy_expected_cmdrs:
            raise RuntimeError(
                f'enemy commander copy incomplete: {copied} copied + '
                f'{skipped} skipped of {enemy_expected_cmdrs} source records')

    # Configured extra commanders have no source com record to copy.  Give
    # each one a fresh record whose tail carries the requested final magic
    # paths (or the Inspector default when magic_paths is omitted).  The
    # client reads the commander list from the orders file, so the record is
    # also appended to that side's .2h; without it the host drops the new
    # commander from the .trn it writes and the unit never shows in game.
    extra_h2: dict[str, list[tuple[int, str, int, list[int], bytes]]] = {
        'player': [], 'enemy': list(enemy_h2_cmdrs)}
    for side, commanders, start, used, province in (
            ('player', player_extra_cmdrs, player_extra_start, p_used,
             player_prov),
            ('enemy', enemy_extra_cmdrs, enemy_extra_start, e_used,
             enemy_prov)):
        for spec in commanders:
            comp_index = spec.get('base', start) + spec['index']
            slot_index = comp_index
            if side == 'enemy' and enemy_god_index is not None:
                if comp_index == enemy_god_index:
                    raise ValueError(
                        f'enemy extra unit id {spec["id"]} maps to the '
                        'enemy pretender slot')
                if comp_index > enemy_god_index:
                    slot_index -= 1
            if slot_index >= len(used) - 1:
                raise ValueError(
                    f'{side} extra unit {spec["label"]} maps outside its '
                    'arena army')
            off = used[1 + slot_index]
            typ = struct.unpack_from('<H', raw, off + 32)[0]
            if typ != spec['id']:
                raise ValueError(
                    f'{side} extra unit {spec["label"]} mapping mismatch: '
                    f'expected type {spec["id"]}, found {typ}')
            if not scrubbed:
                raise RuntimeError(
                    f'ran out of freed com slots before {side} extra '
                    f'commander {spec["label"]}')
            comid, c_start, c_uidpos = scrubbed.pop(0)
            auid = (off - base) // stride + 1
            tail = bytearray(COM_TAIL)
            struct.pack_into('<I', tail, T_PROV, province)
            tail[T_PATHS:T_PATHS + 10] = bytes(spec['paths'])
            struct.pack_into('<I', raw, off + 28, 0xFFFFFFFF)
            com_splices.append((c_start, c_uidpos + COM_BODY,
                                _com_record(comid, spec['name'], auid, [],
                                            bytes(tail))))
            extra_h2[side].append((comid, spec['name'], auid, [],
                                   bytes(tail)))
            reserved.add(auid)
            print(f'  {side} extra commander "{spec["name"]}" '
                  f'(id {spec["id"]}) as com {comid}: '
                  f'paths {_path_text(spec["paths"])}')

    if enemy_god_com is not None:
        # The enemy god came from a battle report: its com record holds the
        # battle-time equipment, carried gems, magic paths and script.  Keep
        # the arena's forged god identity (name/squads) and take the whole
        # tail, exactly like the player's god.
        e_god_uid = (e_used[0] - base) // stride + 1
        found = _find_com(bytes(raw), base, stride, count, e_god_uid)
        if found is None:
            raise ValueError(
                f'battle report pretender: no com record for the enemy god '
                f'(unit id {e_god_uid})')
        comid, c_start, c_uidpos, name, squads, tail = found
        tail = bytearray(enemy_god_com['tail'])
        if struct.unpack_from('<I', tail, T_PROV)[0]:
            struct.pack_into('<I', tail, T_PROV, enemy_prov)
        ref = struct.unpack_from('<I', tail, T_UIDREF)[0]
        if ref in arena_uid:
            struct.pack_into('<I', tail, T_UIDREF, arena_uid[ref])
        com_splices.append((c_start, c_uidpos + COM_BODY,
                            _com_record(comid, name, e_god_uid, [],
                                        bytes(tail))))
        print(f'  enemy pretender com record copied from the battle report '
              f'("{name}")')
    elif enemy_god_paths is not None:
        # The enemy god keeps its forged com record; rewrite the ten path
        # bytes in its tail, in ftherlnd and in the enemy orders file.
        e_god_uid = (e_used[0] - base) // stride + 1
        found = _find_com(bytes(raw), base, stride, count, e_god_uid)
        if found is None:
            raise ValueError(
                f'enemy.pretender magic_paths: no com record for the '
                f'enemy god (unit id {e_god_uid})')
        comid, c_start, c_uidpos, name, squads, tail = found
        tail = bytearray(tail)
        tail[T_PATHS:T_PATHS + 10] = bytes(enemy_god_paths)
        com_splices.append((c_start, c_uidpos + COM_BODY,
                            _com_record(comid, name, e_god_uid,
                                        squads, bytes(tail))))
        _h2_set_god_paths(
            save / f'{enemy_nation.file_name_base}.2h', enemy_god_paths,
            e_god_uid)
        print(f'  enemy pretender magic paths: '
              f'{_path_text(enemy_god_paths)}')

    if player_god_paths is not None:
        # Same treatment for the player's pretender: rewrite its com record's
        # magic paths in ftherlnd and in the player's orders file.
        p_god_uid = (p_used[0] - base) // stride + 1
        found = _find_com(bytes(raw), base, stride, count, p_god_uid)
        if found is None:
            raise ValueError(
                f'player.pretender magic_paths: no com record for the '
                f'player god (unit id {p_god_uid})')
        comid, c_start, c_uidpos, name, squads, tail = found
        tail = bytearray(tail)
        tail[T_PATHS:T_PATHS + 10] = bytes(player_god_paths)
        com_splices.append((c_start, c_uidpos + COM_BODY,
                            _com_record(comid, name, p_god_uid,
                                        squads, bytes(tail))))
        _h2_set_god_paths(
            save / f'{gamedata.nations()[own_nation].file_name_base}.2h',
            player_god_paths, p_god_uid)
        print(f'  player pretender magic paths: '
              f'{_path_text(player_god_paths)}')

    if not player_pretender:
        # Unconfigured pretender: its com record is the source save's own, so
        # take that tail (items, gems, scripts bytes, magic paths) instead of
        # the forged arena loadout.  Only the arena-local references are
        # rewritten.  The orders file is preferred, like every other commander
        # tail: it is the newest state (the .trn copy is a turn older).  The
        # source god may stand outside the copied provinces -- its unit record
        # is then not part of the army -- so its unit id falls back to the
        # one behind the pretender name record.
        src_god = src_god_uid
        if src_god is None:
            god_slot = _god_slots(src_raw, src_name).get('name_record')
            if god_slot is not None:
                src_god = struct.unpack_from(
                    '<I', src_raw, god_slot + len(_enc(src_name)) + 1)[0]
        src_com = (player_god_com
                   or (_source_com(h2_raw, src_raw, src_god)
                       if src_god is not None else None))
        p_god_uid = (p_used[0] - base) // stride + 1
        found = _find_com(bytes(raw), base, stride, count, p_god_uid)
        if src_com is not None and found is not None:
            comid, c_start, c_uidpos, name, squads, tail = found
            tail = bytearray(src_com['tail'])
            if struct.unpack_from('<I', tail, T_PROV)[0]:
                struct.pack_into('<I', tail, T_PROV, player_prov)
            ref = struct.unpack_from('<I', tail, T_UIDREF)[0]
            if ref in arena_uid:
                # A god tail may carry data where a commander tail holds a
                # unit reference, so only a reference we actually copied is
                # remapped; everything else stays byte-identical.
                struct.pack_into('<I', tail, T_UIDREF, arena_uid[ref])
            # The design holds the authoritative god name; _trn_commander's
            # fallback can pick up bytes in front of a lowercase name.
            com_splices.append((c_start, c_uidpos + COM_BODY,
                                _com_record(comid, src_name, p_god_uid,
                                            [], bytes(tail))))
            print(f'  player pretender com record copied from '
                  f'{"the battle report" if player_god_com is not None else "source save"} '
                  f'("{src_name}")')

    # Battle-report commanders on the player side carry their com record
    # (name, magic paths, equipment, carried gems and battle script) in the
    # player's own .trn.  Mirror the enemy transplant above so a province
    # read from a battle report keeps its commanders armed.
    if player_report_records and scrubbed:
        report_start = len(src_specs) - player_report_count
        slots_by_index = {i: off
                          for i, off in enumerate(p_used[1:1 + len(src_specs)])}
        report_uid: dict[int, int] = {}
        for r in player_report_records:
            idx = report_start + r['report_index']
            off = slots_by_index.get(idx)
            if off is None:
                raise ValueError(
                    f'battle-report unit uid {r["uid"]} maps outside the '
                    f'player army (composition index {idx})')
            slot_type = struct.unpack_from('<H', raw, off + 32)[0]
            if slot_type != r['type']:
                raise ValueError(
                    f'strict battle-report mapping mismatch: source uid '
                    f'{r["uid"]} type {r["type"]} landed on arena slot '
                    f'holding type {slot_type}')
            report_uid[r['uid']] = (off - base) // stride + 1

        vcr_sq: dict[int, int] = {}
        for entry in player_report_entries:
            prov = int(entry['province'])
            side = entry['copy']
            rep = [r for r in trn_parse.battle_reports(trn_raw, prov)
                   if (side == 'attacker'
                       and r['attacker'] == entry.get('attacker'))
                   or (side == 'defender'
                       and r['defender'] == entry.get('defender'))]
            if not rep:
                continue
            if 'seq' in entry and entry['seq'] < len(rep):
                rep = rep[entry['seq']]
            else:
                rep = rep[0]
            side_nat = rep[side]
            snaps = _scan_vcr_snapshots(trn_raw, rep['vcr'], rep['bcd'],
                                        side_nat)
            for uid, info in snaps.items():
                if info['squad'] != 0xFFFFFFFF:
                    vcr_sq[uid] = info['squad']

        stamped: dict[int, list[int]] = {}
        for r in player_report_records:
            sq = None
            if r['pos'] is not None:
                sq = struct.unpack_from('<I', trn_raw, r['pos'] + 32)[0]
            if sq is None and r.get('uid') in vcr_sq:
                sq = vcr_sq[r['uid']]
            if sq is not None and sq != 0xFFFFFFFF:
                stamped.setdefault(sq, []).append(r['uid'])
        max_squad = 0
        for k in range(count):
            v = struct.unpack_from('<I', raw, base + k * stride + 28)[0]
            if v != 0xFFFFFFFF:
                max_squad = max(max_squad, v)
        taken: set[int] = set()
        copied = 0
        skipped = 0
        for r in player_report_records:
            auid = report_uid.get(r['uid'])
            if auid is None:
                continue
            com = r.get('com') or _trn_commander(trn_raw, r['uid'])
            if com is None:
                continue
            com_tail = com.get('tail') or b''
            if len(com_tail) != 181:
                # A malformed com body would splice garbage into the orders
                # file; the host then aborts with "bad equip".
                skipped += 1
                print(f'  NOTE: battle-report commander uid {r["uid"]} '
                      f'(type {r["type"]}) has a {len(com_tail)}-byte com '
                      f'tail (expected 181); name and equipment not copied')
                continue
            # Plan the squads this commander leads WITHOUT touching state yet.
            # A com that leads no unit would attach equipment to an empty
            # leader -- exactly what the host rejects as "bad equip".
            plan: list[list[int]] = []
            for sq in com['squads']:
                members = [u for u in stamped.get(sq, [])
                           if u in report_uid and report_uid[u] not in taken]
                if not members:
                    continue
                plan.append(members)
                for u in members:
                    taken.add(report_uid[u])
            n_members = sum(len(m) for m in plan)
            if not scrubbed:
                raise RuntimeError(
                    f'ran out of freed com slots before player commander '
                    f'uid {r["uid"]} (type {r["type"]})')
            comid, c_start, c_uidpos = scrubbed.pop(0)
            new_squads: list[int] = []
            for chosen in plan:
                max_squad += 1
                new_squads.append(max_squad)
                for u in chosen:
                    a = report_uid[u]
                    struct.pack_into('<I', raw, base + (a - 1) * stride + 28,
                                     max_squad)
            tail = bytearray(com_tail)
            if struct.unpack_from('<I', tail, T_PROV)[0]:
                struct.pack_into('<I', tail, T_PROV, player_prov)
            if struct.unpack_from('<I', tail, T_UIDREF)[0]:
                struct.pack_into(
                    '<I', tail, T_UIDREF,
                    report_uid.get(struct.unpack_from('<I', tail, T_UIDREF)[0],
                                   0))
            struct.pack_into('<I', raw, base + (auid - 1) * stride + 28,
                             0xFFFFFFFF)
            slots = _squad_slots(list(zip(new_squads, map(len, plan))))
            com_splices.append((c_start, c_uidpos + COM_BODY,
                                _com_record(comid, com['name'], auid,
                                            slots, bytes(tail))))
            reserved.add(auid)
            extra_h2['player'].append(
                (comid, com['name'], auid, slots, bytes(tail)))
            copied += 1
            unit = gamedata.units().get(r['type'])
            print(f'  player commander "{com["name"]}" '
                  f'({unit.name if unit else r["type"]}) kept as com {comid}: '
                  f'{len(new_squads)} squad(s), {n_members} units, '
                  f'name + orders + equipment copied')
        if skipped:
            print(f'  skipped {skipped} battle-report commander(s) that lead '
                  f'no unit or carry a malformed com record')
        if copied + skipped != player_report_expected_cmdrs:
            raise RuntimeError(
                f'player commander copy incomplete: {copied} copied + '
                f'{skipped} skipped of {player_report_expected_cmdrs} '
                f'source records')

    for side, nation in (('player', gamedata.nations()[own_nation]),
                         ('enemy', enemy_nation)):
        records = extra_h2[side]
        god_tail = None
        if side == 'enemy' and enemy_god_com is not None:
            # Same battle-report tail as the ftherlnd record; the client
            # reads the god's equipment, gems, paths and script here.
            tail = bytearray(enemy_god_com['tail'])
            if struct.unpack_from('<I', tail, T_PROV)[0]:
                struct.pack_into('<I', tail, T_PROV, enemy_prov)
            ref = struct.unpack_from('<I', tail, T_UIDREF)[0]
            if ref in arena_uid:
                struct.pack_into('<I', tail, T_UIDREF, arena_uid[ref])
            god_tail = bytes(tail)
        if records or god_tail is not None:
            god_unit = ((p_used[0] if side == 'player' else e_used[0]) - base) \
                // stride + 1
            _h2_add_commanders(
                save / f'{nation.file_name_base}.2h', records, god_unit,
                god_tail=god_tail)

    # Re-arm commander units.  In the source save these units carried com
    # records; without one the host treats them as plain units, so hand them
    # the com slots that were just freed.  Gods keep their original com.
    for off in p_used[1:] + e_used[1:]:
        if not scrubbed or not cmdr_counts:
            break
        uid = (off - base) // stride + 1
        if uid in reserved:
            continue
        typ = struct.unpack_from('<H', raw, off + 32)[0]
        if cmdr_counts.get(typ, 0) > 0:
            comid, _c_start, cpos = scrubbed.pop(0)
            struct.pack_into('<I', raw, cpos, uid)
            _tail = bytearray(raw[cpos + 24:cpos + 205])
            _sanitize_items(_tail, f're-armed com {comid}')
            raw[cpos + 24:cpos + 205] = _tail
            cmdr_counts[typ] -= 1
            print(f'  com {comid} re-armed for unit {uid} '
                  f'({gamedata.units().get(typ).name if typ in gamedata.units() else typ})')

    # The transplanted com records replace their scrubbed slots wholesale;
    # the name length differs, so this is a splice and must happen after
    # every offset-based edit above (unit table entries sit before the com
    # table and are not affected).
    for start, end, record in sorted(com_splices, reverse=True):
        raw[start:end] = record

    ft.write_bytes(bytes(raw))

    # The client reads the pretender (name, scales and bless effects) from
    # the .trn of the turn, which the host writes from its own state.  This
    # build is followed by a host (see main), and that host regenerates both
    # ftherlnd and every .trn from its own copy of the designs -- dropping the
    # magnitude bless entries of a copied design (``Morale +2`` and
    # ``Animal Awe +1`` came back missing, only ``Poison resistance +10``
    # survived).  The transplant is therefore applied here, before the host
    # writes the world, AND again after the host through the returned
    # callable, so what the game stores and what the client shows is the
    # source design.  Each pretender's unit record also keeps the placeholder
    # chassis, so that is retagged.  A .trn ends with a checksum over
    # everything before it, and the client rejects a turn file whose checksum
    # does not match, so it is rewritten last.
    god_types = {own_nation: god_type, enemy_nation.id: enemy_god_type}

    def _patch_turn_files() -> None:
        """Re-apply the design transplant to ftherlnd and every turn file."""
        world = save / 'ftherlnd'
        data = world.read_bytes()
        buf = _transplant(bytearray(data), arena_uid_nation)
        if bytes(buf) != data:
            world.write_bytes(bytes(buf))
            print(f'  pretender design written into {world.name} '
                  f'(after host)')
        for trn in sorted(save.glob('*.trn')):
            data = trn.read_bytes()
            buf = _transplant(bytearray(data), arena_uid_nation)
            for arena_nation, chosen in god_types.items():
                # The name of each pretender as it now stands in this turn
                # file: the player's was replaced by the source one, the enemy
                # kept the arena's own name because only its bless is copied.
                rec = _design_for_or_none(bytes(buf), arena_nation)
                god_name = rec['god'] if rec else ''
                changed = _retag_trn_god(buf, god_name, chosen,
                                         arena_nation) if chosen else 0
                if changed:
                    print(f'  pretender unit type {chosen} set in {trn.name} '
                          f'({changed} record(s))')
            fixed = savecrc.fix(bytes(buf))
            if fixed != data:
                trn.write_bytes(fixed)
                print(f'  pretender design written into {trn.name}')

    _patch_turn_files()

    # ---- copy current player scripts (.2h) ------------------------------
    # Scripts (battle orders) live in ftherlnd's pretender design record,
    # which was already transplanted from the source save.
    print('scripts already in ftherlnd (from pretender design transplant)')

    return {
        'game': game,
        'player_nation': own_nation,
        'enemy_nation': enemy_nation.id,
        'source_nation': source_nation,
        'player_province': player_prov,
        'enemy_province': enemy_prov,
        'player_composition': src_types,
        'enemy_composition': [s['type'] for s in enemy_specs],
        # Re-applies the design transplant after a host (see _patch_turn_files).
        'patch_turn_files': _patch_turn_files,
    }


def main(config_path: str | Path, attempts: int = 30) -> dict:
    """Build and host the arena, recreating it on a retryable failure.

    Two failure modes are fixed by recreation: the engine's game creation
    is not fully deterministic, so the same config sometimes yields a
    ftherlnd the host cannot read back ("getarray: bad fsize", hostack 2),
    and the unit table size varies with the random independent garrisons,
    which can leave too few records for both armies (ArenaCapacityError).

    The unit table is sized at creation and most of it is the independent
    garrisons, so a table too small for the armies cannot be fixed by mere
    recreation when the armies are large.  Each capacity failure raises the
    creation-time ``--indepstr`` by one step, which adds records until both
    armies fit.  That value is a pure size lever: every independent garrison
    is deleted afterwards, so the arena's independent strength is always 0.
    """
    # Commander names are echoed to the console and some saves carry accented
    # (UTF-8) names; a cp936 console would raise on them.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors='replace')
        except (AttributeError, ValueError):
            pass
    cfg_path = Path(config_path)
    cfg = json.loads(cfg_path.read_text(encoding='utf-8'))
    from collections import Counter
    tries = attempts if cfg.get('host', True) else 1
    indepstr = 0
    last_count = -1
    for attempt in range(1, tries + 1):
        try:
            result = build(cfg, indepstr=indepstr)
        except ArenaCapacityError as exc:
            if attempt >= tries:
                raise
            if exc.count <= last_count:
                raise ArenaCapacityError(
                    f'{exc}; the unit table stopped growing at {exc.count} '
                    f'records — copy fewer units or use a larger arena map',
                    exc.count, exc.required) from None
            last_count = exc.count
            nxt = _next_indepstr(indepstr, exc.count, exc.required)
            if nxt <= indepstr:
                raise ArenaCapacityError(
                    f'{exc}; the arena map cannot hold this army even at '
                    f'indepstr {MAX_INDEPSTR} — copy fewer provinces or '
                    f'fewer units', exc.count, exc.required) from None
            print(f'  {exc}')
            indepstr = nxt
            print(f'  recreating the arena and retrying '
                  f'(attempt {attempt}/{tries}, indepstr {indepstr})')
            cfg = {**cfg, 'arena': {**cfg['arena'], 'recreate': True}}
            continue
        raw = config.save_dir(result['game']).joinpath('ftherlnd').read_bytes()
        pp = result['player_province']
        ep = result['enemy_province']
        pgot = saveedit.province_composition(raw, pp)
        epgot = saveedit.province_composition(raw, ep)
        print(f"player province {pp}: {len(pgot)} units "
              f"(army {len(result['player_composition'])} + pretender)")
        print(f"  counts: {sorted(Counter(pgot).items())}")
        print(f"enemy province {ep}: {len(epgot)} units "
              f"(army {len(result['enemy_composition'])} + pretender)")
        print(f"  counts: {sorted(Counter(epgot).items())}")

        if not cfg.get('host', True):
            return result
        log, over = newgame.host_once(result['game'], timeout=180.0,
                                      mods=cfg.get('mods') or [])
        print('game_over:', over)
        for line in log.splitlines():
            s = line.strip()
            if any(k in s for k in ('has god', 'hostack', 'put turn data',
                                    'Error', 'error', 'Något gick fel')):
                print(' ', s[:160])
        if 'bad equip' in log.lower():
            # Recreating the arena just reproduces the same rejection, so
            # fail loudly instead of spinning through the retry loop.
            raise RuntimeError(
                f'{result["game"]}: the host rejected the arena with '
                f'"bad equip" — a transplanted commander carries an item its '
                f'slot cannot use; not retrying (copy one side, fewer '
                f'provinces or a smaller battle)')
        if 'hostack 1' in log:
            # The host rebuilt the designs from its own state and dropped part
            # of a copied bless; write the source design back into ftherlnd and
            # the turn files before the client opens the save.
            result['patch_turn_files']()
        raw = config.save_dir(result['game']).joinpath('ftherlnd').read_bytes()
        print('after host (as seen in each side\'s own .trn):')
        for nat_id, prov in ((result['player_nation'], pp),
                             (result['enemy_nation'], ep)):
            trn = config.save_dir(result['game']).joinpath(
                gamedata.nations()[nat_id].file_name_base + '.trn')
            seen = trn_parse.province_units(trn.read_bytes(), prov)
            print(f'  nation {nat_id} province {prov}: {len(seen)} units')
        if 'hostack 1' in log:
            return result
        if attempt < tries:
            print(f'  host did not advance (attempt {attempt}/{tries}); '
                  f'recreating the arena and retrying')
            cfg = {**cfg, 'arena': {**cfg['arena'], 'recreate': True}}
    raise RuntimeError(f'{result["game"]}: host failed {tries} times')


if __name__ == '__main__':
    # No argument: use the config next to this checkout, whether the tool is
    # started from the project root or from inside the package.
    default = Path(__file__).resolve().parent.parent / 'arena_config.json'
    main(sys.argv[1] if len(sys.argv) > 1 else str(default))
