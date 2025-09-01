import copy
import random

class ProfileData:
    def __init__(
        self, data: dict, name: str
    ):
        self.id = data.get("id")
        self.name = data.get("name", "???")

        self.base_hp = data.get("base_hp", 20)
        self.hp_increment_by_level = data.get("hp_increment_by_level", 2)
        self.base_stagger = data.get("base_stagger", 15)
        self.stagger_increment_by_level = data.get("stagger_increment_by_level", 1)
        self.base_max_light = data.get("base_max_light", 2)
        self.base_light_gain = data.get("base_light_gain", 1)
        self.base_page_draw = data.get("base_page_draw", 1)
        self.base_min_speed = data.get("base_min_speed", 1)
        self.base_max_speed = data.get("base_max_speed", 2)
        self.attack_slot = data.get("attack_slot", 1)
        self.level = data.get("level", 10)

        self.base_hp_overwrite = data.get("base_hp_overwrite", 0)
        self.base_stagger_overwrite = data.get("base_stagger_overwrite", 0)
        self.base_max_light_overwrite = data.get("base_max_light_overwrite", 0)
        self.base_light_gain_overwrite = data.get("base_light_gain_overwrite", 0)
        self.base_page_draw_overwrite = data.get("base_page_draw_overwrite", 0)
        self.base_min_speed_overwrite = data.get("base_min_speed_overwrite", 0)
        self.base_max_speed_overwrite = data.get("base_max_speed_overwrite", 0)

        # safe mutable defaults
        self.hidden = data.get("hidden", []) or []
        self.evade_queue = data.get("evade_queue", []) or []
        self.temphidden = data.get("temphidden", []) or []
        self.stats_dict = data.get("stats_dict", {}) or {}
        self.nextturn = data.get("nextturn", {}) or {}
        self.buffs = data.get("buffs", {}) or {}
        self.passives = data.get("passives", [])
        self.faction = data.get("faction", [])
        self.resistances = data.get("resistances", {}) or {}
        self.stagger_resistances = data.get("stagger_resistances", {}) or {}
        self.sin_resistances = data.get("sin_resistances", {}) or {}
        self.deck = data.get("deck", {}) or {}
        self.hand = data.get("hand", {}) or {}
        self.original_resistances = data.get("original_resistances", {}) or {}
        self.original_sin_resistances = data.get("original_sin_resistances", {}) or {}
        self._effect_limits = data.get("_effect_limits", {}) or {}
        self._effect_limits_perm = data.get("_effect_limits_perm", {}) or {}

        # calculated values
        self._max_hp = self._calc_max_hp()
        self.current_hp = data.get("current_hp", self._max_hp)

        self.max_stagger = self._calc_max_stagger()
        self.current_stagger = data.get("current_stagger", self.max_stagger)

        self._current_max_light = self._calc_max_light()
        self.current_light = data.get("current_light", self._current_max_light)

        self._current_light_gain = self._calc_light_gain()
        self._current_pages_drawn = self._calc_pages_drawn()
        self.current_speed = data.get("current_speed", 1)

        self._current_min_speed = data.get("speed_min", self._calc_min_speed())
        self._current_max_speed = data.get("speed_max", self._calc_max_speed())

        self._offense_level = self.calc_Base_offense_level
        self.offense_level_sources = data.get("offense_level_sources", self.calc_offense_levelDict())
        self._defense_level = self.calc_Base_defense_level
        self.defense_level_sources = data.get("defense_level_sources", self.calc_defense_levelDict())

        self.calc_total_offense_level()
        self.calc_total_defense_level()

        self.attackslotchange = 0
        self.used = []

        # bools
        self.is_active = data.get("is_active", False)
        self.is_staggered = data.get("is_staggered", False)
        self.staggeredThisTurn = False
        self.PlayerOrEnemy = "Enemy" if "Enemy" in self.faction else "Player"

    @property
    def max_hp(self):
        return self._max_hp

    @max_hp.setter
    def max_hp(self, value):
        self._max_hp = value

    @property
    def _current_max_light(self):
        return self.__current_max_light

    @_current_max_light.setter
    def _current_max_light(self, value):
        self.__current_max_light = value

    @property
    def offense_level(self):
        return self._offense_level

    @property
    def defense_level(self):
        return self._defense_level

    def calc_Base_offense_level(self):
        return self.level * 3

    def calc_offense_levelDict(self):
        newDict = dict()
        newDict["base"] = self.offense_level()
        return newDict

    def calc_Base_defense_level(self):
        return self.level * 3

    def calc_defense_levelDict(self):
        newDict = dict()
        newDict["base"] = self.defense_level()
        return newDict

    def calc_total_offense_level(self):
        sum = 0
        for key, value in self.offense_level_sources.items():
            sum += value

        return sum

    def calc_total_defense_level(self):
        sum = 0

        for key, value in self.defense_level_sources.items():
            sum += value

        return sum


    def add_page(self, pageName, pages):
        if pageName in self.deck:
            self.deck[pageName]["amount"] += 1
        else:
            self.deck[pageName] = {
                "cost": pages[pageName]["light_cost"],
                "amount": 1,
            }

        print(self.deck)

    def get_page_cost(self, string):
        return self.deck[string]["cost"]

    def to_dict(self) -> dict:
        result = {}
        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue  # skip private/internal
            else:
                result[key] = value
        return result

    def calc_stat_mod(self, dictKey):
        return (self.stats_dict[dictKey] - 10) / 2

    def _calc_max_hp(self):
        if (self.base_hp_overwrite > 0):
            return self.base_hp_overwrite

        if self.calc_stat_mod("con") <= 0:
            return int(self.base_hp + (self.hp_increment_by_level * self.level))
        return int(self.base_hp + ((self.hp_increment_by_level + self.calc_stat_mod("con")) * self.level))

    def _calc_max_stagger(self):
        if (self.base_stagger_overwrite > 0):
            return self.base_stagger_overwrite

        if self.calc_stat_mod("str") <= 0:
            return int(self.base_stagger + (self.stagger_increment_by_level * self.level))
        return int(self.base_stagger + ((self.stagger_increment_by_level + self.calc_stat_mod("str")) * self.level))

    def _calc_min_speed(self):
        if (self.base_min_speed_overwrite > 0):
            return int(self.base_min_speed_overwrite)

        if self.calc_stat_mod("dex") <= 0:
            return int(self.base_min_speed)
        return int(self.base_min_speed + self.calc_stat_mod("dex"))

    def _calc_max_speed(self):
        if (self.base_max_speed_overwrite > 0):
            return int(self.base_max_speed_overwrite)

        if self.calc_stat_mod("dex") <= 0:
            return int(self.base_max_speed + 1)
        return int(self.base_max_speed + (self.calc_stat_mod("dex") * 2) - 1)

    def _calc_max_light(self):
        if (self.base_max_light_overwrite > 0):
            return self.base_max_light_overwrite

        return int(self.base_max_light + (self.level / 6))

    def _calc_light_gain(self):
        if (self.base_max_light_overwrite > 0):
            return self.base_max_light_overwrite

        return self.base_light_gain

        # return int(self.base_light_gain + ((self.calc_stat_mod("int") - 1) / 3))

    def _calc_pages_drawn(self):
        if (self.base_page_draw_overwrite > 0):
            return self.base_page_draw_overwrite

        return self.base_page_draw
        # return int(self.base_page_draw + ((self.calc_stat_mod("cha") - 1) / 3))

    def remove_card(self, page: str):
        if page in self.deck:
            self.deck[page]["amount"] -= 1
            if self.deck[page]["amount"] < 1:
                del self.deck[page]

    def is_enemy_of(self, faction: str) -> bool:
        return self.PlayerOrEnemy != faction

    def spend_light(self, pageName):
        # we return TRUE if it doesn't pass, otherwise we return false

        page = self.hand.get(pageName)
        if pageName.startswith("Ordered"):
            return False

        if page is None:
            return True
            # raise KeyError(f"Ability '{pageName}' not found in hand")

        if self.hand[pageName]["cost"] > self.current_light:
            return True
        else:
             self.current_light -= self.hand[pageName]["cost"]

        return False

    def spend_page(self, pageName):
        if pageName.startswith("Ordered"):
            return False

        if self.hand[pageName]["amount"] <= 0:
            return True
        else:
             self.hand[pageName]["amount"] -= 1

        if self.hand[pageName]["amount"] <= 0:
            del self.hand[pageName]

        return False

    def heal_hp(self, hpHealing: int):
        if (self.current_hp + hpHealing) >= self._max_hp:
            self.current_hp = self._max_hp
        else:
            self.current_hp += hpHealing

        if (hpHealing < 0):
            self.take_hp_damage(abs(hpHealing))
    
    def heal_stagger(self, stHealing: int):
        if (self.current_stagger + stHealing) >= self.max_stagger:
            self.current_stagger = self.max_stagger
        else:
            self.current_stagger += stHealing

        if (stHealing < 0):
            self.take_st_damage(abs(stHealing))

    def take_hp_damage(self, dmgTaken: int):

        if (dmgTaken > 0):
            print(f"[NOT A DEBUG MESSAGE THIS SHIT IS ACTUALLY READABLE!!!] {self.name} takes {dmgTaken} damage")
            self.current_hp -= dmgTaken

        else:
            self.heal_hp(abs(dmgTaken))
    
    def take_st_damage(self, dmgTaken: int):
        if (dmgTaken > 0):
            self.current_stagger -= dmgTaken
        else:
            self.heal_hp(abs(dmgTaken))

    def take_max_st_damage(self, dmgTaken: int):
        if (dmgTaken > 0):
            self.max_stagger -= dmgTaken
            self.max_stagger = max(1, self.max_stagger)
        else:
            self.max_stagger += abs(dmgTaken)

    def take_max_HP_damage(self, dmgTaken: int):
        if (dmgTaken > 0):
            self.max_hp -= dmgTaken
            self.max_hp = max(1, self.max_stagger)
        else:
            self.max_hp += abs(dmgTaken)

    def roll_unit_speed(self):
        self.current_speed = random.randint(self._current_min_speed, self._current_max_speed)
        print(f"    Speed: {self.current_speed}")

    def gain_newTurnLight(self):
        self.heal_light(self._current_light_gain)
        self.heal_light(self.nextturn["light"])
        self.nextturn["light"] = 0

    def apply_nextturn_buffs(self):
        for buff_name, buff_data in self.nextturn["buffs"].items():
            existing = self.buffs.get(buff_name)
            if existing:
                updated = existing.copy()
                updated["stack"] = (updated.get("stack") or 0) + (buff_data.get("stack") or 0)
                updated["count"] = (updated.get("count") or 0) + (buff_data.get("count") or 0)
                updated["volatile"] = updated.get("volatile", False) or buff_data.get("volatile", False)
                self.buffs[buff_name] = updated
            else:
                self.buffs[buff_name] = copy.deepcopy(buff_data)

        self.nextturn["buffs"] = {}

    def heal_light(self, amount: int, ignoreLimits: bool = False):
        if (ignoreLimits == False):
            if amount > 0:
                # heal light (cannot exceed max)
                self.current_light = min(self.current_light + amount, self._current_max_light)
            else:
                # lower light (cannot go below 0)
                self.current_light = max(self.current_light + amount, 0)
        else:
            if amount > 0:
                self.current_light += amount
            else:
                self.current_light -= amount
