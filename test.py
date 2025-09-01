from dataclasses import dataclass

@dataclass
class ProfileData:
    # base ID number. for some reason in this codebase... that's a string name. whatever
    id: str
    name: str

    base_hp: int = 30
    hp_increment_by_level: int = 1

    base_stagger: int = 15
    stagger_increment_by_level: int = 1

    base_max_light: int = 2
    base_light_gain: int = 1
    base_page_draw: int = 1

    base_min_speed: int = 1
    base_max_speed: int = 2

    # extra stuff
    attack_slot: int = 1
    hidden: list
    evade_queue: list
    temphidden: list

    # dicts
    stats_dict: dict
    nextturn: dict
    buffs: dict
    passives: set
    faction: set
    resistances: dict
    stagger_resistances: dict
    sin_resistances: dict
    hand: dict
    original_resistances: dict
    _effect_limits: dict
    _effect_limits_perm: dict

    # calculated values done independently
    current_hp: int
    current_stagger: int
    current_light: int
    current_light_gain: int
    current_max_light: int
    current_pages_drawn: int
    current_speed: int
    level: int = 10

    # bools
    is_active: bool = False
    is_staggered: bool = False




    