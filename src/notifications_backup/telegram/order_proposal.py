def render_order_proposal(pair, strategy, order_type, entry, stop, tp, volume):
    return {
        "text": (
            f"Order voorstel:\n"
            f"Pair: {pair}\n"
            f"Strategie: {strategy}\n"
            f"Type: {order_type}\n"
            f"Entry: {entry}\n"
            f"Stop: {stop}\n"
            f"TP: {tp}\n"
            f"Volume: {volume}\n"
            "\nWil je deze order plaatsen?"
        ),
        "buttons": [
            {"text": "✅ Ja", "callback_data": "approve"},
            {"text": "❌ Nee", "callback_data": "reject"},
        ],
    }
