from utils.app_config import AppDataConfig
import services.spa_service as spa_service


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
