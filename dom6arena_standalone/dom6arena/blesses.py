"""Bless effects of Dominions 6, as data.

Two tables, joined by name:

``BLESS_IDS``   the bless id -> name order of the ``Dominions6.exe`` bless
                table (99 slots; 0 is the free +1 morale every blessed sacred
                gets, 1..92 are the purchasable effects, 93 ``end`` and 94..98
                are empty).
``BLESS_INFO``  id -> (path, path levels required, side requirements, effect,
                tags) from https://illwiki.com/bless, so a copied bless can be
                printed and checked by name instead of by number.

A design record stores the purchased blesses as ``<count> 0 <ids>`` (repeats
stack) plus ``<id> <value> 0`` entries for effects that carry a magnitude;
those magnitude entries use ids from 1000 up and are not part of this table
(they are attribute bonuses -- Morale +2, Poison resistance +10 -- and are
copied verbatim by :func:`arena_build._with_design`).
"""

from __future__ import annotations

BLESS_IDS: tuple[str, ...] = (
    'Increased Morale',
    'Superior Morale', 'Wasteland Survival', 'Fire Resistance', 'Attack Skill',
    'Inspirational Presence', 'Righteous Wrath', 'Death Explosion', 'Heat Aura',
    'Fire Shield', 'Flaming Weapons', 'Unbearable Splendour',
    'Precision', 'Shock Resistance', 'Farshot', 'Swiftness', 'Storm Flight',
    'Wind Walker', 'Weightlessness', 'Air Shield', 'Thunder Weapons',
    'Charged Bodies', 'Flight',
    "Winter's Gift", 'Swamp Survival', 'Cold Resistance', 'Swimming',
    'Defence Skill', 'Chill Aura', 'Slowing Weapons', 'Vitriol Weapons',
    'Water Breathing', 'Frost Mist Weapons', 'Quickness',
    'Mountain Survival', 'Reinvigoration', 'Reconstruction',
    'Strength of the Earth', 'Unbreakable', 'Resilience of the Earth',
    'Larger', 'Hard Skin', 'Fortitude',
    'Arcane Command', 'Magic Resistance', 'Spirit Sight', 'Solar Weapons',
    'Far Caster', 'Arcane Finesse', 'Magic Weapons', 'Twist Fate',
    'Fateweaving', 'Etherealness',
    'Undying', 'Undead Command', 'Half Dead', 'Mending Bones',
    'Withering Weapons', 'Stygian Flesh', 'Reforming Flesh', 'Reanimators',
    'Death Weapons', 'Fear',
    'Resilient', 'Low Light Vision', 'Poison Resistance', 'Forest Survival',
    'Unaging', 'Poison Weapons', 'Recuperation', 'Berserker', 'Barkskin',
    'Regeneration',
    'Undreaming', 'Quiet Stride', 'True Sight', 'Blur', 'Obfuscate', 'Awe',
    'Displacement', 'Dread', 'Luck',
    'Strong Vitae', 'Strength of the Flesh', 'Strong Blood', 'Enchanted Blood',
    'Blood Surge', 'Blood Bond', 'Unholy Weapons', 'Blood Vengeance',
    'Vampiric Weapons', 'Awareness', 'Heroism',
    'end',
    '', '', '', '', '',
)

#: Number of real bless ids (0 is the free morale bonus, 1..92 purchasable).
ID_LIMIT = 93

# id: (path, levels, side requirements, effect, tags)
#   ``side`` is the extra requirement the wiki lists next to the paths (a
#   scale choice or encumbrance, e.g. ``Weightlessness`` needs 1 point of
#   Sloth).  ``tags`` holds ``stackable`` / ``innate`` / ``incarnate``.
BLESS_INFO: dict[int, tuple[str, int, str, str, str]] = {
    0: ('F', 1, '', '+1 Morale for every blessed sacred unit, always applied',
        'innate'),
    1: ('F', 1, '', '+1 Morale', 'stackable'),
    2: ('F', 1, '1', 'Wasteland Survival', 'innate'),
    3: ('F', 2, '', '+5 Fire Resistance', 'stackable'),
    4: ('F', 2, '', '+1 Attack Skill', 'stackable'),
    5: ('F', 3, '', 'Inspirational (+1), +50 Leadership',
        'innate stackable'),
    6: ('F', 4, '', 'Righteous Fury when a sacred within 2 squares dies '
        '(Temporary Att +3, Str +3, Morale +6)', ''),
    7: ('F', 5, '', 'Explode on Death (10 AP Fire DMG, AOE = 4+Size)',
        'incarnate'),
    8: ('F', 5, '', 'Heat Aura, +10 Fire Resistance', 'incarnate'),
    9: ('F', 6, '', 'Fire Shield (7)', 'incarnate'),
    10: ('F', 7, '', 'Flaming Weapons (8 AP Fire DMG on hit)', 'incarnate'),
    11: ('F', 8, '4', 'Sight Vengeance (attacker is blinded unless MR negates)',
         'incarnate'),
    12: ('A', 1, '', '+1 Precision', 'stackable'),
    13: ('A', 2, '', '+5 Shock Resistance', 'stackable'),
    14: ('A', 2, '', '+30% Range (weapons only)', 'stackable'),
    15: ('A', 4, '', 'Swiftness (30), +1 Defence Skill', 'stackable'),
    16: ('A', 4, '', 'Storm Immunity', ''),
    17: ('A', 5, '', '+6 Map Movement', 'innate incarnate'),
    18: ('A', 5, '1', 'Floating, Halved Armor Encumbrance', 'incarnate'),
    19: ('A', 6, '', 'Air Shield (80)', 'incarnate'),
    20: ('A', 7, '', 'Shock Weapons (1 capped Shock DMG and 3 Shock FAT on '
        'hit)', 'incarnate'),
    21: ('A', 8, '', 'Overcharged (20), +5 Shock Resistance', 'incarnate'),
    22: ('A', 9, '', 'Flying', 'incarnate'),
    91: ('A', 3, '', 'Unsurroundable (2)', 'stackable'),
    23: ('W', 1, '1', 'Snow Move', 'innate'),
    24: ('W', 1, '1', 'Swamp Survival', 'innate'),
    25: ('W', 2, '', '+5 Cold Resistance', 'stackable'),
    26: ('W', 2, '', 'Swimming', 'innate'),
    27: ('W', 2, '', '+1 Defence Skill', 'stackable'),
    28: ('W', 5, '', 'Chill Aura, +10 Cold Resistance', 'incarnate'),
    29: ('W', 5, '', 'Weapons cast Slow on hit (-2 Att, -2 Def, acts 50% '
        'slower, MR negates)', 'incarnate'),
    30: ('W', 6, '2', 'Acid Weapons (7 AP Acid DMG on hit)', 'incarnate'),
    31: ('W', 6, '', 'Water Breathing', 'innate incarnate'),
    32: ('W', 7, '1', 'Weapons spread Cold Clouds (AOE 1, level 3)',
         'incarnate'),
    33: ('W', 9, '1', 'Quickness', 'incarnate'),
    34: ('E', 1, '', 'Mountain Survival', 'innate'),
    35: ('E', 2, '', 'Reinvigoration (1)', 'stackable'),
    37: ('E', 2, '', '+1 Strength', 'stackable'),
    38: ('E', 4, '', 'Affliction Resistance (3)', ''),
    40: ('E', 4, '3', 'Permanently Enlarged', 'innate'),
    36: ('E', 5, '', 'Regeneration for Inanimates', 'incarnate'),
    39: ('E', 6, '', '+10 Fire Resistance, +10 Shock Resistance', 'incarnate'),
    41: ('E', 6, '', '+5 Natural Protection', 'incarnate'),
    42: ('E', 8, '', 'All Three Physical Resistances', 'incarnate'),
    43: ('S', 1, '', 'Magic Leadership (0->10, +25 otherwise)',
         'innate stackable'),
    44: ('S', 2, '', '+1 Magic Resistance', 'stackable'),
    45: ('S', 3, '1', 'Spirit Sight', ''),
    46: ('S', 3, '1', 'Solar Weapons (4 AP Holy Fire DMG on hit)', ''),
    47: ('S', 4, '', 'Far Caster (1, All)', ''),
    48: ('S', 4, '', '+1 Penetration (also affects non-weapon attacks negated '
        'by MR)', ''),
    49: ('S', 5, '', 'Weapons deal Magic damage', 'incarnate'),
    50: ('S', 6, '', 'Twist Fate', 'incarnate'),
    51: ('S', 7, '1', 'Curses the Luck of attackers (MR negates)', 'incarnate'),
    52: ('S', 8, '2', 'Ethereal', 'incarnate'),
    53: ('D', 1, '', 'Reduces minimum Hit Points by 2; non-Undead & Unhealing '
        'units with negative HP die at the end of the battle', 'stackable'),
    54: ('D', 1, '', '+50 Undead Leadership (0->50 too)', 'innate stackable'),
    55: ('D', 2, '2', 'Need not Eat, Disease Resistance (80)', 'innate'),
    56: ('D', 3, '', 'Recuperation for the Undead', 'innate'),
    57: ('D', 4, '', 'Weapons cast Decay if they deal damage (MR negates)', ''),
    58: ('D', 5, '', 'Invulnerability (10)', 'incarnate'),
    59: ('D', 6, '', 'Regeneration (10%) for the Undead (includes Undead '
        'Inanimates)', 'incarnate'),
    60: ('D', 7, '', '50% of hits deal Unlife Damage (including spells), '
        '+5 Undead Leadership', 'incarnate'),
    61: ('D', 8, '', 'Deadly Weapons (2 AN DMG and Disease on hit, MR negates '
        'each independently)', 'incarnate'),
    62: ('D', 9, '1', 'Fear (5)', 'incarnate'),
    63: ('N', 1, '', '+1 Hit Point', 'stackable'),
    64: ('N', 1, '', 'Darkvision (50)', ''),
    65: ('N', 2, '', '+5 Poison Resistance', 'stackable'),
    66: ('N', 2, '', 'Forest Survival', 'innate'),
    67: ('N', 3, '1', 'Unaging (75); also lowers the starting age of Sacred '
        'recruits', 'innate'),
    68: ('N', 4, '1', 'Poisoned Weapons (5 AN Poison DMG on damage)', ''),
    69: ('N', 5, '', 'Recuperation (requires a living body)', 'innate '
        'incarnate'),
    70: ('N', 5, '', 'Berserker (+2)', 'incarnate'),
    71: ('N', 6, '', 'Barkskin', 'incarnate'),
    72: ('N', 7, '', 'Regeneration (10%) (not for Inanimates)', 'incarnate'),
    73: ('G', 1, '', 'Unsleeping (4)', ''),
    92: ('G', 1, '', '+35% Experience Gain', 'stackable'),
    74: ('G', 2, '', '+20 Stealth (does not affect the Stealth-less)',
         'innate stackable'),
    75: ('G', 3, '', 'True Sight', ''),
    76: ('G', 3, '', '-2 Attack Skill for attackers (negated by True Sight, '
        'Spirit Sight, or a lack of sight)', ''),
    77: ('G', 6, '', 'Stealthy (40), +40 Stealth for the already-Stealthy',
         'innate incarnate'),
    78: ('G', 6, '2', 'Awe (3)', 'incarnate'),
    79: ('G', 7, '', '-5 Attack Skill for attackers (replaces Blur, same '
        'drawbacks)', 'incarnate'),
    80: ('G', 7, '', 'Dread (5); True Sight or Spirit Sight negates',
         'incarnate'),
    81: ('G', 8, '2', 'Luck', 'incarnate'),
    82: ('B', 1, '', '+1 Hit Point', 'stackable'),
    83: ('B', 2, '', '+1 Strength', 'stackable'),
    84: ('B', 3, '', '+5 Poison Resistance, Disease Resistance (80)', 'innate'),
    85: ('B', 3, '', 'Regeneration (0.5), +1 Magic Resistance, Bleeding '
        'immunity', ''),
    86: ('B', 4, '', 'Blood Surge when killing a non-Inanimate (Temporary '
        'Att +3, Str +3, Def +1, +1 Reinvigoration)', ''),
    87: ('B', 5, '', 'Half of damage taken is dispersed to other Blood-Bonded '
        'within 5 squares', 'incarnate'),
    88: ('B', 6, '', 'Unholy Weapons (15 AP DMG on hit, affects Sacreds & the '
        'Blessed only)', 'incarnate'),
    89: ('B', 7, '', 'Blood Vengeance (attacker also takes damage unless MR '
        'negates)', 'incarnate'),
    90: ('B', 8, '4', 'Life-Draining Weapons (3 AN Drain DMG on damage)',
         'incarnate'),
}


def name(bless_id: int) -> str:
    """Table name of a bless id, ``'?<id>'`` when it is not a bless."""
    if 0 <= bless_id < len(BLESS_IDS) and BLESS_IDS[bless_id]:
        return BLESS_IDS[bless_id]
    return f'?{bless_id}'


def label(bless_id: int) -> str:
    """Name plus path requirement, e.g. ``'Defence Skill (W2)'``."""
    info = BLESS_INFO.get(bless_id)
    if info is None:
        return name(bless_id)
    return f'{name(bless_id)} ({info[0]}{info[1]})'


def describe(ids) -> str:
    """Readable list of bless ids, repeats collapsed to ``xN``."""
    counts: dict[int, int] = {}
    for v in ids:
        counts[int(v)] = counts.get(int(v), 0) + 1
    parts = []
    for bless_id, n in counts.items():
        parts.append(label(bless_id) + (f' x{n}' if n > 1 else ''))
    return ', '.join(parts)
