from modifierScripts.GlobalRegistry import *
from everythingexcepthim import resolve_value
from UnitProfileCode import ProfileData
import random

@register_modifier
class DrawPageHandler(ModifierHandler):
    name = "draw"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        value = resolve_value(value, acquired_values)
        draw_val = resolve_value(value, acquired_values)
        if not draw_val:
            # fallback: if a static draw value is provided
            if value is not None:
                # modifier_target.hand.append(value)
                if log is not None:
                    log.append(f"📜 {modifier_target.name} draws: {value}")
            return

        deck = modifier_target.deck
        hand = modifier_target.hand
        drawn_cards = []

        deck_counts = {page: data["amount"] for page, data in deck.items()}

        for _ in range(draw_val):
            # build hand_counts each loop from hand
            hand_counts = {page: data["amount"] for page, data in hand.items()}

            # only allow draws if hand has less than deck's max count
            eligible_pages = [
                page for page, max_count in deck_counts.items()
                if hand_counts.get(page, 0) < max_count
            ]

            # remove pages that were already used
            eligible_pages = [page for page in eligible_pages if page not in modifier_target.used]

            # fill with "Nothing" until total deck count reaches 9
            total_deck_count = sum(data["amount"] for data in deck.values())
            if total_deck_count < 9:
                missing = 9 - total_deck_count
                eligible_pages.extend(["Nothing"] * missing)

            if not eligible_pages:
                break

            drawn = random.choice(eligible_pages)

            if drawn == "Nothing":
                drawn_cards.append(drawn)
                continue

            if drawn in hand:
                hand[drawn]["amount"] += 1
            else:
                hand[drawn] = {"cost": deck[drawn]["cost"], "amount": 1}

            # update hand_counts
            hand_counts[drawn] = hand_counts.get(drawn, 0) + 1

            drawn_cards.append(drawn)

        if log is not None and drawn_cards:
            log.append(f"📜 {modifier_target.name} draws: {', '.join(drawn_cards)}")