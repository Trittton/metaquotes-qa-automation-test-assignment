import pytest

from src.gui.pages.rdp_logon_settings_page import RdpLogonSettingsPage


@pytest.fixture()
def mstsc_raw() -> RdpLogonSettingsPage:
    page = RdpLogonSettingsPage()
    page.launch()
    yield page
    page.close()


@pytest.fixture()
def mstsc_page(mstsc_raw: RdpLogonSettingsPage) -> RdpLogonSettingsPage:
    mstsc_raw.expand_options()
    mstsc_raw.select_general_tab()
    yield mstsc_raw
