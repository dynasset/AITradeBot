import logging
import requests
from ai_tradebot.config.kraken_config import KRAKEN_API_KEY, KRAKEN_API_SECRET
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler("kraken_service.log"),
        logging.StreamHandler()
    ]
)

class KrakenService:
    def get_asset_pairs(self) -> dict:
        """
        Haalt alle asset pairs op uit Kraken API.
        Returns:
            dict: Asset pairs info
        """
        url = 'https://api.kraken.com/0/public/AssetPairs'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            logging.info(f"AssetPairs: {list(data.get('result', {}).keys())}")
            return data.get('result', {})
        except Exception as e:
            logging.error(f"Fout bij ophalen asset pairs: {e}")
            return {}

    def get_ticker(self, pair: str) -> dict:
        """
        Haalt ticker informatie op voor een trading pair.
        Args:
            pair (str): Trading pair, bijvoorbeeld 'XBTUSD'.
        Returns:
            dict: Ticker data van Kraken API.
        """
        url = 'https://api.kraken.com/0/public/Ticker'
        try:
            response = requests.get(url, params={'pair': pair})
            response.raise_for_status()
            data = response.json()
            logging.info(f"Ticker data opgehaald voor {pair}: {data}")
            price = None
            if 'result' in data:
                result_keys = list(data['result'].keys())
                key = pair if pair in data['result'] else (result_keys[0] if result_keys else None)
                if key and 'c' in data['result'][key]:
                    price = float(data['result'][key]['c'][0])
            return {'price': price, 'raw': data}
        except Exception as e:
            logging.error(f"Fout bij ophalen ticker data: {e}")
            return None

    def place_order(self, pair: str, order_type: str, volume: float, price: float = None, stoploss: float = None, take_profit: float = None, min_order_size: float = None) -> dict:
        """
        Plaatst een order op Kraken via krakenex.
        Args:
            pair (str): Trading pair.
            order_type (str): 'buy' of 'sell'.
            volume (float): Hoeveelheid.
            price (float, optional): Prijs voor limit order.
            stoploss (float, optional): Stoploss prijs.
            take_profit (float, optional): Take profit prijs.
            min_order_size (float, optional): Minimale ordergrootte voor deze pair.
        Returns:
            dict: Resultaat van orderplaatsing.
        """
        import krakenex
        k = krakenex.API()
        k.key = self.api_key
        k.secret = self.api_secret
        if min_order_size is not None and volume < min_order_size:
            logging.info(f"Ordervolume ({volume}) lager dan minimum ({min_order_size}), aanpassen naar minimum.")
            volume = min_order_size
        order_data = {
            'pair': pair,
            'type': order_type,
            'ordertype': 'limit' if price else 'market',
            'volume': volume,
        }
        if price:
            order_data['price'] = price
        if stoploss:
            order_data['close[ordertype]'] = 'stop-loss'
            order_data['close[price]'] = stoploss
        if take_profit:
            order_data['close[ordertype]'] = 'take-profit'
            order_data['close[price]'] = take_profit
        try:
            logging.info(f"Order plaatsen: {order_type} {volume} {pair} @ {price} SL: {stoploss} TP: {take_profit}")
            response = k.query_private('AddOrder', order_data)
            logging.info(f"Order response: {response}")
            return response
        except Exception as e:
            logging.error(f"Fout bij orderplaatsing: {e}")
            return {'error': str(e)}
    def get_balances(self, correct_for_open_orders=True) -> dict:
        """
        Haalt alle beschikbare balances op uit Kraken account.
        Returns:
            dict: Balances per asset.
        """
        import krakenex
        k = krakenex.API()
        k.key = self.api_key
        k.secret = self.api_secret
        try:
            response = k.query_private('Balance')
            logging.info(f"Balances: {response}")
            raw_balances = response.get('result', {})
            asset_map = {
                'USD': ['USD', 'ZUSD', 'USDC', 'XUSD', 'USDT'],
                'EUR': ['EUR', 'ZEUR', 'XEUR'],
            }
            balances = {}
            mapped_assets = {}
            for key, value in raw_balances.items():
                key_upper = key.upper()
                mapped = False
                for std, aliases in asset_map.items():
                    if key_upper in [alias.upper() for alias in aliases]:
                        balances[std] = value
                        mapped_assets[key] = std
                        mapped = True
                        break
                if not mapped:
                    balances[key] = value
            logging.info(f"Asset mapping toegepast: {mapped_assets}")
            logging.info(f"Gecorrigeerde balances: {balances}")
            if correct_for_open_orders:
                open_orders = self.get_open_orders()
                for order_id, order in open_orders.items():
                    descr = order.get('descr', {})
                    vol = float(order.get('vol', 0))
                    pair = descr.get('pair')
                    type_ = descr.get('type')
                    if pair and vol:
                        if type_ == 'buy':
                            quote = pair[-4:] if len(pair) > 4 else pair
                            for std, aliases in asset_map.items():
                                if quote in aliases and std in balances:
                                    balances[std] = str(max(0, float(balances[std]) - vol))
                                    break
                            else:
                                if quote in balances:
                                    balances[quote] = str(max(0, float(balances[quote]) - vol))
                        elif type_ == 'sell':
                            base = pair[:-4] if len(pair) > 4 else pair
                            for std, aliases in asset_map.items():
                                if base in aliases and std in balances:
                                    balances[std] = str(max(0, float(balances[std]) - vol))
                                    break
                            else:
                                if base in balances:
                                    balances[base] = str(max(0, float(balances[base]) - vol))
            logging.info(f"Balances na correctie open orders: {balances}")
            return balances
        except Exception as e:
            logging.error(f"Fout bij ophalen balances: {e}")
            return {}
    def get_open_orders(self) -> dict:
        import krakenex
        k = krakenex.API()
        k.key = self.api_key
        k.secret = self.api_secret
        try:
            response = k.query_private('OpenOrders')
            logging.info(f"Open orders: {response}")
            return response.get('result', {}).get('open', {})
        except Exception as e:
            logging.error(f"Fout bij ophalen open orders: {e}")
            return {}
    def __init__(self):
        if not KRAKEN_API_KEY or not KRAKEN_API_SECRET or KRAKEN_API_KEY.strip() == "" or KRAKEN_API_SECRET.strip() == "":
            raise ValueError("Kraken API credentials niet gevonden of leeg in environment.")
        self.api_key = KRAKEN_API_KEY
        self.api_secret = KRAKEN_API_SECRET

    def get_ohlc(self, pair: str, interval: int = 1, limit: int = 100):
        import pandas as pd
        url = "https://api.kraken.com/0/public/OHLC"
        params = {"pair": pair, "interval": interval}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            result = data.get("result", {})
            ohlc = None
            for k in result:
                if k != "last":
                    ohlc = result[k]
                    break
            if not ohlc:
                return None
            df = pd.DataFrame(ohlc, columns=[
                "time", "open", "high", "low", "close", "vwap", "volume", "count"
            ])
            try:
                df = df.apply(pd.to_numeric)
            except Exception as e:
                logging.warning(f"Kon sommige kolommen niet converteren naar numeriek: {e}")
            return df.tail(limit)
        except Exception as e:
            logging.error(f"Fout bij ophalen OHLC data voor {pair} ({interval}m): {e}")
            return None
