import requests
import time

class TelegramService:
    def __init__(self, token, chat_id=None):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.chat_id = chat_id

    def send_message(self, text):
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text}
        resp = requests.post(url, json=payload)
        return resp.json()

    def get_updates(self, offset=None):
        url = f"{self.base_url}/getUpdates"
        params = {"timeout": 30}
        if offset:
            params["offset"] = offset
        resp = requests.get(url, params=params)
        return resp.json()

    def await_approval(self, proposal_id, timeout=300):
        """
        Wacht op goedkeuring via Telegram reply. proposal_id is een unieke string in het bericht.
        """
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
