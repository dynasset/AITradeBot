import requests
import time

class TelegramService:
    def handle_update(self, update, on_start=None, on_stop=None, on_order_approve=None, on_order_reject=None):
        # Afhandeling van inkomende Telegram updates (messages/callbacks)
        if 'message' in update:
            msg = update['message']
            text = msg.get('text', '').lower()
            if 'start' in text:
                if on_start:
                    on_start()
                # 1. Welkomsttemplate en alle info in één bericht
                from ai_tradebot.notifications.telegram.templates import render_start
                tpl = render_start()
                info_lines = []
                info_lines.append("De bot is gestart en luistert naar nieuwe kansen.")
                # Init KrakenService één keer
                ks = None
                balances = None
                try:
                    from ai_tradebot.kraken.kraken_service import KrakenService
                    ks = KrakenService()
                except Exception as e:
                    info_lines.append(f"Fout bij initialiseren KrakenService: {e}")
                # Actieve orders (live)
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
                    except Exception as e:
                        info_lines.append(f"Fout bij ophalen actieve orders: {e}")
                # Balans (live)
                if ks:
                    try:
                        balances = ks.get_balances()
                        balance_text = "Balans:\n" + "\n".join([f"{k}: {v}" for k, v in balances.items()])
                        info_lines.append(balance_text)
                    except Exception as e:
                        info_lines.append(f"Fout bij ophalen balans: {e}")
                # Polling interval (live/config)
                try:
                    from ai_tradebot.config.kraken_config import POLLING_INTERVAL
                    info_lines.append(f"Polling interval: elke {POLLING_INTERVAL} seconden wordt er een nieuwe analyse gedaan.")
                except Exception:
                    info_lines.append("Polling interval: elke 60 seconden wordt er een nieuwe analyse gedaan.")
                # Eerst mogelijke order (live strategie)
                if ks and balances:
                    try:
                        from ai_tradebot.strategies.strategy_workflow import load_strategies, fetch_kraken_ohlc_multi
                        asset_pairs = ks.get_asset_pairs()
                        strategies = load_strategies()
                        # Analyseer alleen pairs waar balans op is
                        tradable_pairs = [pair for pair in asset_pairs.keys() if any(asset in pair for asset in balances.keys() if float(balances[asset]) > 0)]
                        equity = float(balances.get("USD", 10000))
                        found = False
                        feedback = []
                        for pair in tradable_pairs:
                            multi_df = fetch_kraken_ohlc_multi(pair, intervals=[1,3,5,15,60], limit=100)
                            for strategy in strategies:
                                res = strategy(multi_df, equity)
                                if res and res.get('kans'):
                                    order = res.get('order')
                                    info_lines.append(f"Eerst mogelijke order: {pair} {order.get('type')} @ {order.get('entry')} (strategie: {strategy.__name__})")
                                    found = True
                                    break
                                else:
                                    # Extra feedback waarom geen kans
                                    reason = res.get('reden', 'Geen kans door strategiecondities (trend/RSI/BB)') if res else 'Geen kans, geen analyse-resultaat.'
                                    feedback.append(f"{pair} ({strategy.__name__}): {reason}")
                            if found:
                                break
                        if not found:
                            info_lines.append("Geen directe orderkans gevonden.")
                            info_lines.append("\nFeedback per pair/strategie:")
                            info_lines.extend(feedback)
                    except Exception as e:
                        info_lines.append(f"Fout bij strategie-analyse: {e}")
                # Stuur alles in één bericht
                self.send_message("\n\n".join(info_lines))
            elif 'stop' in text:
                if on_stop:
                    on_stop()
                from ai_tradebot.notifications.telegram.templates import render_stop
                tpl = render_stop()
                self.send_message(tpl['text'])
            elif 'status' in text:
                from ai_tradebot.notifications.telegram.templates import render_status
                tpl = render_status()
                self.send_message(tpl['text'])
        elif 'callback_query' in update:
            cq = update['callback_query']
            data = cq.get('data')
            if data == 'approve' and on_order_approve:
                on_order_approve()
                self.send_message("Order goedgekeurd en geplaatst!")
            elif data == 'reject' and on_order_reject:
                on_order_reject()
                self.send_message("Order afgekeurd.")

    def __init__(self, token, chat_id=None):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.chat_id = chat_id
        with open("logs/telegram_service.log", "a") as log:
            log.write(f"TelegramService init: token={self.token}, chat_id={self.chat_id}\n")

    def send_message(self, text, buttons=None, buttons_mode="auto"):
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text}
        if buttons:
            # buttons_mode: "auto" (detect), "flat" (platte lijst), "matrix" (lijst van lijsten)
            if buttons_mode == "matrix" or (buttons_mode == "auto" and isinstance(buttons[0], list)):
                # lijst van lijsten van dicts
                payload["reply_markup"] = {"inline_keyboard": buttons}
            elif buttons_mode == "flat" or (buttons_mode == "auto" and isinstance(buttons[0], dict)):
                # platte lijst van dicts
                payload["reply_markup"] = {"inline_keyboard": [[b] for b in buttons]}
            else:
                # fallback: geen knoppen
                payload["reply_markup"] = {"inline_keyboard": []}
        with open("logs/telegram_service.log", "a") as log:
            log.write(f"send_message: token={self.token}, chat_id={self.chat_id}, payload={payload}\n")
        try:
            resp = requests.post(url, json=payload)
            with open("logs/telegram_service.log", "a") as log:
                log.write(f"SEND_MESSAGE payload: {payload}\n")
                log.write(f"SEND_MESSAGE response: {resp.text}\n")
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            with open("logs/telegram_service.log", "a") as log:
                log.write(f"ERROR send_message: {e}\n")
            return {"error": str(e)}

    def send_template(self, template_name, **params):
        # Dynamisch template ophalen en renderen uit notifications/telegram
        if template_name == 'order_proposal':
            from ai_tradebot.notifications.telegram.order_proposal import render_order_proposal
            tpl = render_order_proposal(**params)
            self.send_message(tpl['text'], buttons=tpl.get('buttons'))
        # Voeg hier meer templates toe

    def get_updates(self, offset=None):
        url = f"{self.base_url}/getUpdates"
        params = {"timeout": 30}
        if offset:
            params["offset"] = offset
        try:
            resp = requests.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            status_code = getattr(e.response, 'status_code', None)
            with open("logs/telegram_service.log", "a") as log:
                log.write(f"ERROR get_updates: {e}\n")
            if status_code == 409:
                # Telegram conflict: waarschijnlijk dubbele bot instance
                with open("logs/telegram_service.log", "a") as log:
                    log.write("CONFLICT 409: getUpdates. Polling wordt 30s gepauzeerd en opnieuw geprobeerd.\n")
                time.sleep(30)
                return {"error": "409 Conflict"}
            return {"error": str(e)}
        except Exception as e:
            with open("logs/telegram_service.log", "a") as log:
                log.write(f"ERROR get_updates: {e}\n")
            return {"error": str(e)}

    def poll_updates(self, last_update_id=None, on_start=None, on_stop=None, on_order_approve=None, on_order_reject=None):
        # Poll Telegram voor nieuwe updates en handel ze af
        import datetime
        offset = last_update_id
        backoff = 2
        while True:
            with open("logs/telegram_service.log", "a") as log:
                log.write(f"[{datetime.datetime.now()}] poll_updates: token={self.token}, chat_id={self.chat_id}, offset={offset}\n")
            updates = self.get_updates(offset)
            if updates.get("error") == "409 Conflict":
                with open("logs/telegram_service.log", "a") as log:
                    log.write(f"[{datetime.datetime.now()}] 409 Conflict gedetecteerd. Polling opnieuw na {backoff}s.\n")
                backoff = min(backoff * 2, 60)
                time.sleep(backoff)
                continue
            else:
                backoff = 2
            if 'result' in updates:
                for update in updates['result']:
                    offset = update['update_id'] + 1
                    self.handle_update(update, on_start, on_stop, on_order_approve, on_order_reject)
            time.sleep(60)

    def await_approval(self, proposal_id, timeout=300):
        start = time.time()
        offset = None
        while time.time() - start < timeout:
            updates = self.get_updates(offset)
            if "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    msg = update.get("message", {})
                    text = msg.get("text", "")
                    if proposal_id in text and ("ja" in text.lower() or "yes" in text.lower()):
                        return True
                    if proposal_id in text and ("nee" in text.lower() or "no" in text.lower()):
                        return False
            time.sleep(2)
        return False
