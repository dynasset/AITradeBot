import pytest
from ai_tradebot.main import start_bot, stop_bot, approve_order, reject_order, analyse_and_push_opportunity

def test_start_bot():
    assert callable(start_bot)

def test_stop_bot():
    assert callable(stop_bot)

def test_approve_order():
    assert callable(approve_order)

def test_reject_order():
    assert callable(reject_order)

def test_analyse_and_push_opportunity():
    assert callable(analyse_and_push_opportunity)
