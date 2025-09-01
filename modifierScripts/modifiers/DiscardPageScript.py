from modifierScripts.GlobalRegistry import *
from everythingexcepthim import process_effects, resolve_value
from UnitProfileCode import ProfileData
import random

@register_modifier
class DiscardPageHandler(ModifierHandler):
    name = "discard"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        """
               Discards cards from the hand based on mode and amount.
               `value` should be a dict with "amount" and optional "mode".
               """
        discard_config = value
        if discard_config is None:
            return

        amount = discard_config.get("amount")
        mode = discard_config.get("mode", "random")
        discard_val = resolve_value(amount, acquired_values)

        if not discard_val:
            # fallback: discard a specific card if amount is a string page
            if amount in modifier_target.hand:
                modifier_target.hand[amount]["amount"] -= 1
                if modifier_target.hand[amount]["amount"] < 1:
                    del modifier_target.hand[amount]
                if log:
                    log.append(f"📜 {modifier_target.name} discards: {amount}")
            return

        hand = modifier_target.hand
        discarded_cards = []

        for _ in range(discard_val):
            if not hand:
                break

            # Choose card to discard
            if mode == "random":
                discarded = random.choice(list(hand.keys()))
            elif mode in ("lowest", "highest"):
                sorted_hand = sorted(
                    hand.keys(),
                    key=lambda page: hand[page]["cost"],
                    reverse=(mode == "highest")
                )
                discarded = sorted_hand[0]
            else:
                # fallback: random
                discarded = random.choice(list(hand.keys()))

            cost = hand[discarded]["cost"]
            hand[discarded]["amount"] -= 1
            if hand[discarded]["amount"] < 1:
                del hand[discarded]

            discarded_cards.append(discarded)

            # Update StorageBox in data
            storage = kwargs.get("data", {}).setdefault("StorageBox", {}).setdefault(modifier_target.name, {})
            storage["discardedThisTurn"] = storage.get("discardedThisTurn", 0) + 1
            storage["lastDiscardedCost"] = cost

            # Trigger on_discard effects
            pages = kwargs.get("pages", {})
            # source = kwargs.get("source")
            target = kwargs.get("target") or modifier_target
            dice = kwargs.get("dice")
            damage = kwargs.get("damage")
            stagger = kwargs.get("stagger")
            pageusetype = kwargs.get("pageusetype")
            interaction = kwargs.get("interaction")
            log_obj = kwargs.get("log", log)

            if discarded in pages:
                await process_effects(
                    modifier_target, target, dice, "on_discard",
                    roll_container, pages[discarded], damage, stagger,
                    log_obj, pageusetype=pageusetype,
                    data=kwargs.get("data"), interaction=interaction
                )

        if log is not None and discarded_cards:
            log.append(f"📜 {modifier_target.name} discards: {', '.join(discarded_cards)}")