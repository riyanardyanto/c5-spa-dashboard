from src.utils.app_config import AppDataConfig
import src.services.spa_service as spa_service
import pandas as pd
import asyncio


def test_get_url_period_loss_tree_uses_config_url(monkeypatch):
    # Prepare a config with a known base URL
    cfg = AppDataConfig(
        environment="test",
        username="u",
        password="p",
        link_up=("LU18",),
        url="http://example.test/db.aspx?",
    )

    # Patch base URL helper used inside spa_service
    monkeypatch.setattr(spa_service, "get_base_url", lambda: cfg.url)

    # Call the function under test
    result = spa_service.get_url_period_loss_tree("21", "2025-11-08", shift="")

    # Basic asserts: starts with base url and contains expected db_Line
    assert result.startswith(cfg.url)
    assert "db_Line=ID01-SE-CP-L021" in result
    assert "table=SPA_NormPeriodLossTree" in result


def test_process_async_with_local_html():
    html_path = "assets/spa1.html"
    with open(html_path, "r", encoding="utf-8") as fh:
        content = fh.read()

    processor = spa_service.SPADataProcessor(content, is_html=True)
    processed = asyncio.run(processor.process_async())

    assert isinstance(processed, dict)
    assert "data_losses" in processed
    assert "stops_reason" in processed
    assert isinstance(processed["data_losses"], pd.DataFrame)


def test_ssl_configurations_are_read():
    from src.utils.app_config import AppDataConfig

    cfg = AppDataConfig(
        environment="dev",
        username="u",
        password="p",
        link_up=("LU18",),
        url="http://example/",
        verify_ssl=False,
        ca_bundle=None,
    )

    from src.services.spa_service import SPADataFetcher

    fetcher = SPADataFetcher(url="http://example/", config=cfg)
    assert fetcher._verify_ssl is False
    assert fetcher._ca_bundle is None
