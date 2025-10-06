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
import logging
import requests
from src.config.kraken_config import KRAKEN_API_KEY, KRAKEN_API_SECRET
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler("kraken_service.log"),
        logging.StreamHandler()
    ]
)

class KrakenService:
    def get_open_orders(self) -> dict:
        """
        Haalt openstaande orders op uit Kraken account.
        Returns:
            dict: Open orders per order_id.
        """
        import krakenex
        import logging
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
        """
        Initialiseert KrakenService met API credentials uit environment variables.
        Raises:
            ValueError: als credentials niet gevonden zijn of leeg zijn.
        """
        if not KRAKEN_API_KEY or not KRAKEN_API_SECRET or KRAKEN_API_KEY.strip() == "" or KRAKEN_API_SECRET.strip() == "":
            raise ValueError("Kraken API credentials niet gevonden of leeg in environment.")
        self.api_key = KRAKEN_API_KEY
        self.api_secret = KRAKEN_API_SECRET

    def get_ohlc(self, pair: str, interval: int = 1, limit: int = 100):
        """
        Haalt OHLC data op voor een pair en interval via Kraken API.
        Returns:
            pd.DataFrame: OHLC data
        """
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

    def get_min_order_size(self, pair: str) -> float:
        """
        Haalt de minimale ordergrootte op voor een pair via Kraken API.
        Returns:
            float: Minimale ordergrootte
        """
        import requests
        import logging
        url = 'https://api.kraken.com/0/public/AssetPairs'
        try:
            response = requests.get(url, params={'pair': pair})
            response.raise_for_status()
            data = response.json()
            # Zoek naar min order size (ordermin)
            result = data.get('result', {})
            key = pair if pair in result else (list(result.keys())[0] if result else None)
            if key and 'ordermin' in result[key]:
                min_order = float(result[key]['ordermin'])
                logging.info(f"Minimale ordergrootte voor {pair}: {min_order}")
                return min_order
        except Exception as e:
            logging.error(f"Fout bij ophalen min order size: {e}")
        return 0.0

    def get_balances(self, correct_for_open_orders=True) -> dict:
        """
        Haalt alle beschikbare balances op uit Kraken account.
        Returns:
            dict: Balances per asset.
        """
        import krakenex
        import logging
        k = krakenex.API()
        k.key = self.api_key
        k.secret = self.api_secret
        try:
            response = k.query_private('Balance')
            logging.info(f"Balances: {response}")
            raw_balances = response.get('result', {})
            # Asset mapping: normaliseer keys voor USD, USDC, ZUSD, XUSD, USDT, EUR, ZEUR, XEUR (case-insensitive)
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
                # Corrigeer balances voor reserved funds
                for order_id, order in open_orders.items():
                    descr = order.get('descr', {})
                    vol = float(order.get('vol', 0))
                    pair = descr.get('pair')
                    type_ = descr.get('type')
                    # Reserveer funds van base asset bij buy, quote asset bij sell
                    if pair and vol:
                        # Kraken asset mapping: base/quote
                        # Voor buy: reserveer quote, voor sell: reserveer base
                        # We halen funds af van balances
                        if type_ == 'buy':
                            quote = pair[-4:] if len(pair) > 4 else pair
                            # Map quote naar gestandaardiseerde key
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

    def get_asset_pairs(self) -> dict:
        """
        Haalt alle asset pairs op uit Kraken API.
        Returns:
            dict: Asset pairs info
        """
        import requests
        import logging
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
        import logging
        url = 'https://api.kraken.com/0/public/Ticker'
        try:
            response = requests.get(url, params={'pair': pair})
            response.raise_for_status()
            data = response.json()
            logging.info(f"Ticker data opgehaald voor {pair}: {data}")
            # Extract price info (voorbeeld: 'c' = last trade)
            price = None
            # Kraken API gebruikt soms andere pair keys, zoals 'XXBTZUSD' voor 'XBTUSD'
            if 'result' in data:
                # Neem eerste key uit result als pair niet direct gevonden wordt
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
        import logging
        import krakenex
        k = krakenex.API()
        k.key = self.api_key
        k.secret = self.api_secret
        # Zorg dat volume altijd >= min_order_size
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
        # Stoploss en take profit zijn advanced orders, Kraken vereist extra parameters
        # Voorbeeld: 'close[ordertype]': 'stop-loss', 'close[price]': stoploss
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

    def dynamic_trade(self, analyse_fn, max_order_pct=0.1):
        """
        Dynamische tradingfunctie:
        - Haalt actuele balances op
        - Bepaalt per pair of er voldoende saldo is
        - Analyseert pairs via analyse_fn
        - Plaatst orders met SL/TP
        Args:
            analyse_fn: functie die per pair een orderadvies geeft (dict met 'type', 'sl', 'tp')
            max_order_pct: maximaal percentage van asset om te traden
        Returns:
            dict: Resultaten van geplaatste orders
        """
        import logging
        balances = self.get_balances(correct_for_open_orders=True)
        asset_pairs = self.get_asset_pairs()
        results = {}
        # Dynamisch: bepaal alle quote assets die in je balances voorkomen
        tradable_quotes = set(balances.keys())
        for pair, info in asset_pairs.items():
            base = info.get('base')
            quote = info.get('quote')
            # Alleen pairs waarvan de quote asset voorkomt in je balances
            if quote not in tradable_quotes:
                continue
            min_order_size = float(info.get('ordermin', 0.0))
            advies = analyse_fn(pair, float(balances.get(base, 0)))
            if not advies or advies.get('type') not in ['buy', 'sell']:
                continue
            # Voor 'buy' orders: gebruik quote asset saldo
            # Voor 'sell' orders: gebruik base asset saldo
            if advies['type'] == 'buy':
                asset_balance = float(balances.get(quote, 0))
            else:
                asset_balance = float(balances.get(base, 0))
            order_size = asset_balance * max_order_pct
            if order_size < min_order_size:
                order_size = min_order_size
            if asset_balance < min_order_size:
                logging.info(f"Niet genoeg saldo voor {pair}: {asset_balance} < min {min_order_size}")
                continue
            ticker = self.get_ticker(pair)
            price = ticker['price'] if ticker and 'price' in ticker else None
            # Bepaal aantal decimalen voor prijs
            if pair in ["XXBTZUSD", "XBTUSD", "BTC/USD"]:
                price_decimals = 1
            else:
                price_decimals = int(info.get('pair_decimals', 1)) if 'pair_decimals' in info else 1
            if price is not None:
                price = round(price, price_decimals)
            logging.info(f"Analyse advies voor {pair}: {advies}, prijs: {price}, balance: {asset_balance}, order_size: {order_size}")
            if price:
                result = self.place_order(
                    pair,
                    advies['type'],
                    order_size,
                    price=price,
                    stoploss=advies.get('sl'),
                    take_profit=advies.get('tp'),
                    min_order_size=min_order_size
                )
                results[pair] = result
        return results

    def get_account_info(self) -> dict:
        """
        Haalt accountinformatie op van Kraken.
        Returns:
            dict: Accountinformatie.
        """
        pass

    def cancel_all_open_orders(self) -> dict:
        """
        Annuleert alle openstaande orders in het Kraken account.
        Returns:
            dict: Resultaten van cancel requests per order_id.
        """
        import krakenex
        import logging
        k = krakenex.API()
        k.key = self.api_key
        k.secret = self.api_secret
        open_orders = self.get_open_orders()
        results = {}
        for order_id in open_orders.keys():
            try:
                response = k.query_private('CancelOrder', {'txid': order_id})
                logging.info(f"Cancel order {order_id}: {response}")
                results[order_id] = response
            except Exception as e:
                logging.error(f"Fout bij annuleren order {order_id}: {e}")
                results[order_id] = {'error': str(e)}
        return results