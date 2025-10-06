import unittest
import os
from unittest import mock
from importlib import reload

class TestKrakenService(unittest.TestCase):
    def setUp(self):
        # Zorg dat we altijd starten met een schone import
        self.kraken_service_module = None

    def _import_service(self):
        # Verwijder modules uit sys.modules zodat reload werkt
        import sys
        sys.modules.pop('ai_tradebot.config.kraken_config', None)
        sys.modules.pop('ai_tradebot.kraken.kraken_service', None)
        # Herlaad config en service na mocken van environ
        from importlib import import_module
        import_module('ai_tradebot.config.kraken_config')
        global KrakenService
        KrakenService = import_module('ai_tradebot.kraken.kraken_service').KrakenService

    def test_init_success(self):
        with mock.patch.dict(os.environ, {"KRAKEN_API_KEY": "testkey", "KRAKEN_API_SECRET": "testsecret"}):
            self._import_service()
            service = KrakenService()
            self.assertEqual(service.api_key, 'testkey')
            self.assertEqual(service.api_secret, 'testsecret')

    def test_init_missing_credentials(self):
        with mock.patch.dict(os.environ, {"KRAKEN_API_KEY": "", "KRAKEN_API_SECRET": ""}):
            self._import_service()
            with self.assertRaises(ValueError):
                KrakenService()

    def test_get_ticker_signature(self):
        with mock.patch.dict(os.environ, {"KRAKEN_API_KEY": "testkey", "KRAKEN_API_SECRET": "testsecret"}):
            self._import_service()
            service = KrakenService()
            result = service.get_ticker('XBTUSD')
            self.assertIsInstance(result, dict)
            self.assertIn('price', result)

    def test_place_order_signature(self):
        with mock.patch.dict(os.environ, {"KRAKEN_API_KEY": "testkey", "KRAKEN_API_SECRET": "testsecret"}):
            self._import_service()
            service = KrakenService()
            result = service.place_order('XBTUSD', 'buy', 1.0, price=50000)
            self.assertIsInstance(result, dict)

    # test_get_account_info_signature verwijderd: bestaat niet in KrakenService

if __name__ == '__main__':
    unittest.main()
