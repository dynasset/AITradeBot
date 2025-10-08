def render_start():
    return {
        "text": "Welkom bij AITradeBot! Je bent live verbonden.",
        "buttons": []
    }

def render_stop():
    return {
        "text": "De bot is gestopt. Je ontvangt geen meldingen meer.",
        "buttons": []
    }

def render_status(status_info=None):
    text = "Bot status: Actief" if not status_info else f"Bot status: {status_info}"
    return {
        "text": text,
        "buttons": []
    }

# order_proposal blijft in order_proposal.py
