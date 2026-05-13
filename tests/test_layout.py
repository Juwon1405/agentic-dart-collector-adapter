"""Tests for layout.classify_artifact() — the dispatcher."""
import pytest

from dart_collector_adapter.layout import classify_artifact, EVIDENCE_LAYOUT


def test_prefetch_classified_as_prefetch():
    assert classify_artifact("uploads/auto/C:/Windows/Prefetch/SVCHOST.EXE-123.pf") == "prefetch"


def test_amcache_classified_as_amcache():
    assert classify_artifact("uploads/auto/C:/Windows/AppCompat/Programs/Amcache.hve") == "amcache"


def test_security_hive_classified_as_registry():
    assert classify_artifact("uploads/auto/C:/Windows/System32/config/SECURITY") == "registry"


def test_sam_hive_classified_as_registry():
    assert classify_artifact("uploads/auto/C:/Windows/System32/config/SAM") == "registry"


def test_evtx_classified_as_eventlog():
    assert classify_artifact("uploads/auto/C:/Windows/System32/winevt/Logs/Security.evtx") == "eventlog"


def test_chrome_history_classified_as_browser():
    assert classify_artifact("uploads/auto/C:/Users/x/AppData/Local/Google/Chrome/User Data/Default/History") == "browser"


def test_firefox_places_sqlite_classified_as_browser():
    assert classify_artifact("uploads/auto/C:/Users/x/AppData/Roaming/Mozilla/Firefox/Profiles/abc/places.sqlite") == "browser"


def test_lnk_classified_as_lnk():
    assert classify_artifact("uploads/auto/C:/Users/x/Recent/foo.lnk") == "lnk"


def test_jumplist_classified_as_jumplist():
    assert classify_artifact(
        "uploads/auto/C:/Users/x/AppData/Roaming/Microsoft/Windows/Recent/AutomaticDestinations/abc.automaticDestinations-ms"
    ) == "jumplist"


def test_iis_log_classified_as_weblog():
    assert classify_artifact("uploads/auto/inetpub/logs/LogFiles/W3SVC1/u_ex240509.log") == "weblog"


def test_nginx_log_classified_as_weblog():
    assert classify_artifact("uploads/auto/var/log/nginx/access_2024.log") == "weblog"


def test_linux_auth_classified_as_auth():
    assert classify_artifact("uploads/auto/var/log/auth.log") == "auth"


def test_memory_dump_classified_as_memory():
    assert classify_artifact("uploads/memory.dmp") == "memory"
    assert classify_artifact("uploads/memory_dump.raw") == "memory"


def test_unknown_falls_back_to_other():
    assert classify_artifact("uploads/random/unknown.bin") == "other"


def test_every_category_has_a_layout_dir():
    for category in {c for c, _ in [(classify_artifact(name), None) for name in [
        "x.pf", "Amcache.hve", "SECURITY", "Security.evtx", "x.lnk", "x.dmp",
        "u_ex.log", "auth.log", "random.bin"
    ]]}:
        assert category in EVIDENCE_LAYOUT
