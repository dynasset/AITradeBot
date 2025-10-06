def test_dashboard_import():
    try:
        import Dashboard.app
    except Exception as e:
        assert False, f"Import van Dashboard.app faalt: {e}"
