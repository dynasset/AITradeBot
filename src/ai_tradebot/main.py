"""
Entrypoint voor AITradeBot met Telegram workflow en echte strategieën
"""
import os
import requests
from ai_tradebot.notifications.telegram_service import TelegramService
from ai_tradebot.kraken.kraken_service import KrakenService
from ai_tradebot.notifications.telegram.order_proposal import render_order_proposal
from ai_tradebot.strategies.strategy_workflow import load_strategies, fetch_kraken_ohlc_multi

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

telegram = TelegramService(token=TELEGRAM_TOKEN, chat_id=TELEGRAM_CHAT_ID)
kraken = KrakenService()


current_order = {}
bot_active = True



def start_bot():
    global bot_active
    bot_active = True
    # Start dashboard status
    try:
        resp = requests.post("http://localhost:5000/api/start_bot")
        if resp.ok:
            telegram.send_message("Bot gestart! Dashboard status: actief.")
        else:
            telegram.send_message(f"Bot gestart! Maar dashboard status kon niet worden gezet: {resp.text}")
    except Exception as e:
        telegram.send_message(f"Bot gestart! (dashboard status error: {e})")
    analyse_and_push_opportunity()



def stop_bot():
    global bot_active
    bot_active = False
    # Stop dashboard status
    try:
        resp = requests.post("http://localhost:5000/api/stop_bot")
        if resp.ok:
            telegram.send_message("Bot gestopt! Dashboard status: inactief.")
        else:
            telegram.send_message(f"Bot gestopt! Maar dashboard status kon niet worden gezet: {resp.text}")
    except Exception as e:
        telegram.send_message(f"Bot gestopt! (dashboard status error: {e})")

def approve_order():
    if current_order:
        result = kraken.place_order(
            pair=current_order['pair'],
            order_type=current_order['order_type'],
            volume=current_order['volume'],
            price=current_order['entry'],
            stoploss=current_order['stop'],
            take_profit=current_order['tp']
        )
        telegram.send_message(f"Order geplaatst: {result}")
    else:
        telegram.send_message("Geen actieve order om te plaatsen.")

def reject_order():
    telegram.send_message("Order afgekeurd.")


def analyse_and_push_opportunity():
    global bot_active
    if not bot_active:
        return
    asset_pairs = kraken.get_asset_pairs()
    strategies = load_strategies()
    for pair in list(asset_pairs.keys())[:1]:  # Voorbeeld: alleen eerste pair
        multi_df = fetch_kraken_ohlc_multi(pair, intervals=[1, 5, 15], limit=50)
        for strategy in strategies:
            res = strategy(multi_df, 10000)  # Voorbeeld equity
            if res and res.get('kans'):
                order_data = res.get('order')
                global current_order
                current_order = {
                    'pair': pair,
                    'strategy': strategy.__name__,
                    'order_type': order_data.get('type'),
                    'entry': order_data.get('entry'),
                    'stop': order_data.get('stop'),
                    'tp': order_data.get('tp'),
                    'volume': order_data.get('volume')
                }
                tpl = render_order_proposal(
                    pair=pair,
                    strategy=strategy.__name__,
                    order_type=order_data.get('type'),
                    entry=order_data.get('entry'),
                    stop=order_data.get('stop'),
                    tp=order_data.get('tp'),
                    volume=order_data.get('volume')
                )
                telegram.send_message(tpl['text'], buttons=tpl.get('buttons'))
                return

if __name__ == "__main__":
    analyse_and_push_opportunity()
    telegram.poll_updates(
        on_start=start_bot,
        on_stop=stop_bot,
        on_order_approve=approve_order,
        on_order_reject=reject_order
    )
