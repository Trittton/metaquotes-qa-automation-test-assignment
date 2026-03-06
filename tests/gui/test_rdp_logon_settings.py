import logging

import pytest

from src.gui.pages.rdp_logon_settings_page import RdpLogonSettingsPage

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.gui


@pytest.mark.smoke
def test_mstsc_launches_and_shows_main_window(mstsc_raw: RdpLogonSettingsPage):
    assert mstsc_raw.window_exists(), "mstsc.exe did not produce a visible window within the timeout."


def test_collapsed_dialog_shows_computer_field_only(mstsc_raw: RdpLogonSettingsPage):
    assert mstsc_raw.is_computer_field_visible(), "Computer field must be visible in collapsed state."
    assert not mstsc_raw.is_general_tab_visible(), "General tab must NOT be visible before Show Options."
    assert mstsc_raw.is_show_options_button_visible(), "'Show Options' button must be present."


@pytest.mark.smoke
def test_show_options_expands_dialog_to_show_tabs(mstsc_raw: RdpLogonSettingsPage):
    mstsc_raw.expand_options()

    assert mstsc_raw.is_general_tab_visible(), "General tab must be visible after Show Options."
    assert mstsc_raw.is_hide_options_button_visible(), "'Hide Options' must appear after expansion."
    assert not mstsc_raw.is_show_options_button_visible(), "'Show Options' must disappear after expansion."


@pytest.mark.smoke
def test_general_tab_is_selectable(mstsc_raw: RdpLogonSettingsPage):
    mstsc_raw.expand_options()
    mstsc_raw.select_general_tab()
    assert mstsc_raw.is_general_tab_visible()


@pytest.mark.smoke
def test_username_field_visible_and_enabled_on_general_tab(mstsc_page: RdpLogonSettingsPage):
    assert mstsc_page.is_username_field_visible(), "User name field must be visible."
    assert mstsc_page.is_username_field_enabled(), "User name field must be enabled."


@pytest.mark.smoke
def test_mstsc_window_can_be_closed(mstsc_raw: RdpLogonSettingsPage):
    assert mstsc_raw.window_exists()
    mstsc_raw.close()
    assert not mstsc_raw.window_exists(), "Window must not exist after close()."
