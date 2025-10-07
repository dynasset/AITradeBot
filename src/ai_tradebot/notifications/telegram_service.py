import requests
import time

class TelegramService:
    def handle_update(self, update, on_start=None, on_stop=None, on_order_approve=None, on_order_reject=None):
        # Afhandeling van inkomende Telegram updates (messages/callbacks)
        if 'message' in update:
            msg = update['message']
            text = msg.get('text', '').lower()
            if 'start' in text and on_start:
                on_start()
                self.send_message("Bot gestart!")
            elif 'stop' in text and on_stop:
                on_stop()
                self.send_message("Bot gestopt!")
        elif 'callback_query' in update:
            cq = update['callback_query']
            data = cq.get('data')
            if data == 'approve' and on_order_approve:
                on_order_approve()
                self.send_message("Order goedgekeurd en geplaatst!")
            elif data == 'reject' and on_order_reject:
                on_order_reject()
                self.send_message("Order afgekeurd.")

    def poll_updates(self, last_update_id=None, on_start=None, on_stop=None, on_order_approve=None, on_order_reject=None):
        # Poll Telegram voor nieuwe updates en handel ze af
        offset = last_update_id
        while True:
            updates = self.get_updates(offset)
            if 'result' in updates:
                for update in updates['result']:
                    offset = update['update_id'] + 1
                    self.handle_update(update, on_start, on_stop, on_order_approve, on_order_reject)
            time.sleep(2)
    def __init__(self, token, chat_id=None):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.chat_id = chat_id

    def send_message(self, text, buttons=None):
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text}
        if buttons:
            payload["reply_markup"] = {
                "inline_keyboard": [[{"text": b["text"], "callback_data": b["callback_data"]} for b in buttons]]
            }
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
        except Exception as e:
            with open("logs/telegram_service.log", "a") as log:
                log.write(f"ERROR get_updates: {e}\n")
            return {"error": str(e)}

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
