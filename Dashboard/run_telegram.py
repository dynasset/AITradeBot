import os
import sys
LOCKFILE = '/tmp/ai_tradebot_telegram.lock'
if os.path.exists(LOCKFILE):
    print('AITradeBot Telegram is al actief. Dubbele start wordt geblokkeerd.')
    sys.exit(1)
with open(LOCKFILE, 'w') as f:
    f.write(str(os.getpid()))
import atexit
def remove_lock():
    if os.path.exists(LOCKFILE):
        os.remove(LOCKFILE)
atexit.register(remove_lock)
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
def get_actuele_orderkansen():
    try:
        from ai_tradebot.kraken.kraken_service import KrakenService
        from ai_tradebot.strategies.strategy_workflow import load_strategies, fetch_kraken_ohlc_multi
        ks = KrakenService()
        balances = ks.get_balances()
        asset_pairs = ks.get_asset_pairs()
        strategies = load_strategies()
        tradable_pairs = [pair for pair in asset_pairs.keys() if any(asset in pair for asset in balances.keys() if float(balances[asset]) > 0)]
        equity = float(balances.get("USD", 10000))
        kansen = []
        for pair in tradable_pairs:
            multi_df = fetch_kraken_ohlc_multi(pair, intervals=[1,3,5,15,60], limit=100)
            multi_df['pair'] = pair
            for strategy in strategies:
                res = strategy(multi_df, equity)
                if res and res.get('kans'):
                    order = res.get('order')
                    kansen.append(f"{order.get('pair', pair)} {order.get('type')} @ {order.get('entry')} (strategie: {strategy.__name__})")
        if kansen:
            return "Alle orderkansen:\n" + "\n".join(kansen)
        else:
            return "Geen orderkansen gevonden."
    except Exception as e:
        return f"Fout bij ophalen van alle orderkansen: {e}"
from ai_tradebot.notifications.telegram_service import TelegramService
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import logging

def main():
    print("TelegramService gestart.")
    # Laad .env als die bestaat
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("python-dotenv niet geïnstalleerd, .env wordt niet geladen.")
    token = os.environ.get("TELEGRAM_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    service = TelegramService(token=token, chat_id=chat_id)
    if not token or not chat_id:
        msg = f"WAARSCHUWING: TELEGRAM_TOKEN of TELEGRAM_CHAT_ID is niet gezet! token='{token}', chat_id='{chat_id}'"
        print(msg)
        import logging
        logging.error(msg)
        try:
            service.send_message(msg)
        except Exception as e:
            print(f"Kon waarschuwing niet naar Telegram sturen: {e}")
        # Stop de bot direct, want berichten kunnen niet worden afgeleverd
        sys.exit(1)
    import threading
    import time
    import logging

    # Globale status: actief/gestopt
    bot_status = {"actief": True}

    # Logging setup: bestand én console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[
            logging.FileHandler("logs/telegram_service.log"),
            logging.StreamHandler()
        ]
    )

    service.send_message("Testbericht vanuit run_telegram.py!")

    POLLING_INTERVAL = 3600  # seconden, standaard 60 minuten

    def send_periodic_status():
        while True:
            try:
                logging.info("Periodieke analyse gestart.")
                print("Periodieke analyse gestart.")
                from ai_tradebot.notifications.telegram.templates import render_start
                tpl = render_start()
                info_lines = []
                if bot_status["actief"]:
                    info_lines.append("Automatische status-update: de bot luistert naar nieuwe kansen.")
                    logging.info("Bot status: actief")
                    print("Bot status: actief")
                else:
                    info_lines.append("Automatische status-update: de bot is gestopt. Alleen status en balans worden getoond.")
                    logging.info("Bot status: gestopt")
                    print("Bot status: gestopt")
                ks = None
                balances = None
                try:
                    from ai_tradebot.kraken.kraken_service import KrakenService
                    ks = KrakenService()
                    logging.info("KrakenService geïnitialiseerd.")
                    print("KrakenService geïnitialiseerd.")
                except Exception as e:
                    error_msg = f"Fout bij initialiseren KrakenService: {e}"
                    info_lines.append(error_msg)
                    logging.error(error_msg)
                    print(error_msg)
                    service.send_message(error_msg)
                if ks:
                    try:
                        open_orders = ks.get_open_orders()
                        if open_orders:
                            orders_text = "Actieve orders:\n" + "\n".join([
                                f"{o.get('descr', {}).get('pair', 'onbekend')} - {o.get('descr', {}).get('type', '')} @ {o.get('descr', {}).get('price', '')} (TP: {o.get('descr', {}).get('price2', '')})" for o in open_orders.values()
                            ])
                        else:
                            orders_text = "Geen actieve orders."
                        info_lines.append(orders_text)
                        logging.info(orders_text)
                        print(orders_text)
                    except Exception as e:
                        error_msg = f"Fout bij ophalen actieve orders: {e}"
                        info_lines.append(error_msg)
                        logging.error(error_msg)
                        print(error_msg)
                        service.send_message(error_msg)
                if ks:
                    try:
                        balances = ks.get_balances()
                        balance_text = "Balans:\n" + "\n".join([f"{k}: {v}" for k, v in balances.items()])
                        info_lines.append(balance_text)
                        logging.info(balance_text)
                        print(balance_text)
                    except Exception as e:
                        error_msg = f"Fout bij ophalen balans: {e}"
                        info_lines.append(error_msg)
                        logging.error(error_msg)
                        print(error_msg)
                        service.send_message(error_msg)
                polling_text = f"Polling interval: elke {POLLING_INTERVAL} seconden wordt er een nieuwe analyse gedaan."
                info_lines.append(polling_text)
                logging.info(polling_text)
                print(polling_text)
                if bot_status["actief"] and ks and balances:
                    try:
                        from ai_tradebot.strategies.strategy_workflow import load_strategies, fetch_kraken_ohlc_multi
                        asset_pairs = ks.get_asset_pairs()
                        strategies = load_strategies()
                        open_orders = ks.get_open_orders() if ks else {}
                        pairs_with_open_orders = set()
                        for order in open_orders.values():
                            descr = order.get('descr', {})
                            pair = descr.get('pair')
                            if pair:
                                pairs_with_open_orders.add(pair)
                        tradable_pairs = [
                            pair for pair in asset_pairs.keys()
                            if any(asset in pair for asset in balances.keys() if float(balances[asset]) > 0)
                            and pair not in pairs_with_open_orders
                        ]
                        equity = float(balances.get("USD", 10000))
                        import concurrent.futures
                        found = False
                        feedback = []
                        resultaten = []
                        def analyse_pair(pair):
                            multi_df = fetch_kraken_ohlc_multi(pair, intervals=[1,3,5,15,60], limit=100)
                            for strategy in strategies:
                                res = strategy(multi_df, equity)
                                logging.info(f"Analyse {strategy.__name__} voor pair {pair}: resultaat: {res}")
                                print(f"Analyse {strategy.__name__} voor pair {pair}: resultaat: {res}")
                                if res and res.get('kans'):
                                    order = res.get('order')
                                    msg = f"Orderkans gevonden: {pair} {order.get('type')} @ {order.get('entry')} (strategie: {strategy.__name__})"
                                    logging.info(msg)
                                    print(msg)
                                    try:
                                        # Stuur een ordervoorstel met buttons
                                        service.send_template(
                                            'order_proposal',
                                            pair=pair,
                                            strategy=strategy.__name__,
                                            order_type=order.get('type'),
                                            entry=order.get('entry'),
                                            stop=order.get('stop', ''),
                                            tp=order.get('tp', ''),
                                            volume=order.get('volume', '')
                                        )
                                    except Exception as e:
                                        logging.error(f"Fout bij versturen Telegram ordervoorstel: {e}")
                                    return {
                                        'order': order,
                                        'pair': pair,
                                        'strategy': strategy.__name__,
                                        'result': res
                                    }
                                else:
                                    reason = res.get('reden', 'Geen kans door strategiecondities (trend/RSI/BB)') if res else 'Geen kans, geen analyse-resultaat.'
                                    resultaten.append({'pair': pair, 'strategy': strategy.__name__, 'reason': reason})
                            return None

                        with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
                            future_to_pair = {executor.submit(analyse_pair, pair): pair for pair in tradable_pairs}
                            for future in concurrent.futures.as_completed(future_to_pair):
                                res = future.result()
                                if res and res.get('order') and not found:
                                    order = res['order']
                                    info_lines.append(f"Eerst mogelijke order: {res['pair']} {order.get('type')} @ {order.get('entry')} (strategie: {res['strategy']})")
                                    found = True
                        if not found:
                            info_lines.append("Geen directe orderkans gevonden.")
                            info_lines.append("\nFeedback per pair/strategie:")
                            for f in resultaten:
                                feedback.append(f"{f['pair']} ({f['strategy']}): {f['reason']}")
                            info_lines.extend(feedback)
                            logging.info("Geen directe orderkans gevonden. Feedback: %s", feedback)
                            print("Geen directe orderkans gevonden. Feedback:", feedback)
                    except Exception as e:
                        error_msg = f"Fout bij strategie-analyse: {e}"
                        info_lines.append(error_msg)
                        logging.error(error_msg)
                        print(error_msg)
                        try:
                            service.send_message(error_msg)
                        except Exception as send_err:
                            logging.error(f"Fout bij versturen Telegram error: {send_err}")
                # Forceer altijd een periodieke status-update naar Telegram en console
                buttons = [{"text": "Toon alle orderkansen", "callback_data": "show_all_opportunities"}]
                status_msg = "\n\n".join(info_lines)
                logging.info(f"Periodieke analyse uitgevoerd. Status: {status_msg}")
                print(f"Periodieke analyse uitgevoerd. Status: {status_msg}")
                try:
                    service.send_message(status_msg, buttons=buttons)
                except Exception as e:
                    logging.error(f"Fout bij versturen periodieke status-update: {e}")
            except Exception as e:
                error_msg = f"Fout bij automatische status-update: {e}"
                service.send_message(error_msg)
                logging.error(error_msg)
                print(error_msg)
            time.sleep(POLLING_INTERVAL)

    status_thread = threading.Thread(target=send_periodic_status, daemon=True)
    status_thread.start()

    def on_start():
        logging.info("/start ontvangen!")
        print("/start ontvangen!")
        bot_status["actief"] = True
        service.send_message("Bot is gestart. Trading en analyse zijn weer actief.")

    def on_stop():
        logging.info("/stop ontvangen!")
        print("/stop ontvangen!")
        bot_status["actief"] = False
        service.send_message("Bot is gestopt. Alleen status en balans worden nog getoond.")

    def on_order_approve():
        pass
    def on_order_reject():
        pass

    # Callback voor alle kansen knop
    def handle_update_callback(update):
        if "callback_query" in update:
            cq = update["callback_query"]
            data = cq.get("data")
            if data == "show_all_opportunities":
                service.send_message(get_actuele_orderkansen())
        # /statuskansen als text message
        if "message" in update:
            msg = update["message"]
            text = msg.get("text", "").lower()
            if text == "/statuskansen":
                service.send_message(get_actuele_orderkansen())

    def poll_updates_with_callback(*args, **kwargs):
        import types
        import time
        orig_handle_update = service.handle_update
        def new_handle_update(self, update, on_start=None, on_stop=None, on_order_approve=None, on_order_reject=None):
            orig_handle_update(update, on_start, on_stop, on_order_approve, on_order_reject)
            handle_update_callback(update)
        service.handle_update = types.MethodType(new_handle_update, service)
        while True:
            try:
                service.poll_updates(on_start=kwargs.get('on_start'), on_stop=kwargs.get('on_stop'), on_order_approve=kwargs.get('on_order_approve'), on_order_reject=kwargs.get('on_order_reject'))
            except Exception as e:
                import logging
                logging.error(f"Polling error: {e}")
                print(f"Polling error: {e}")
                alert_text = f"AITradeBot herstart polling na error: {e}"
                try:
                    service.send_message(alert_text)
                except Exception as send_err:
                    logging.error(f"Kon alert niet sturen: {send_err}")
                if '409' in str(e):
                    print("409 Conflict: Waarschijnlijk meerdere bots actief. Wacht 30s en probeer opnieuw.")
                    logging.error("409 Conflict: Waarschijnlijk meerdere bots actief. Wacht 30s en probeer opnieuw.")
                    time.sleep(30)
                else:
                    print("Onbekende polling error. Herstart over 10s.")
                    time.sleep(10)

    poll_updates_with_callback(on_start=on_start, on_stop=on_stop, on_order_approve=on_order_approve, on_order_reject=on_order_reject)

if __name__ == "__main__":
    main()
