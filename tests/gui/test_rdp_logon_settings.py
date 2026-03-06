import pytest

from src.gui.pages.rdp_logon_settings_page import RdpLogonSettingsPage

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


@pytest.mark.smoke
def test_computer_field_accepts_valid_hostname(mstsc_page: RdpLogonSettingsPage):
    hostname = "myserver.local"
    mstsc_page.clear_computer()
    mstsc_page.set_computer(hostname)

    assert mstsc_page.get_computer() == hostname, (
        f"Expected {hostname!r}, got {mstsc_page.get_computer()!r}"
    )


def test_computer_field_accepts_ip_address(mstsc_page: RdpLogonSettingsPage):
    ip = "192.168.1.100"
    mstsc_page.clear_computer()
    mstsc_page.set_computer(ip)

    assert mstsc_page.get_computer() == ip


def test_computer_field_accepts_hostname_with_custom_port(mstsc_page: RdpLogonSettingsPage):
    value = "myserver.local:3389"
    mstsc_page.clear_computer()
    mstsc_page.set_computer(value)

    assert mstsc_page.get_computer() == value, (
        f"Expected {value!r}, got {mstsc_page.get_computer()!r}"
    )


def test_computer_field_can_be_cleared(mstsc_page: RdpLogonSettingsPage):
    mstsc_page.set_computer("somevalue")
    mstsc_page.clear_computer()

    result = mstsc_page.get_computer()
    assert result == "", f"Expected empty Computer field, got {result!r}"


def test_username_field_accepts_domain_username(mstsc_page: RdpLogonSettingsPage):
    username = "CORP\testuser"
    mstsc_page.set_username(username)

    assert mstsc_page.get_username() == username, (
        f"Expected {username!r}, got {mstsc_page.get_username()!r}"
    )


def test_username_field_accepts_upn_format(mstsc_page: RdpLogonSettingsPage):
    upn = "testuser@company.com"
    mstsc_page.set_username(upn)

    assert mstsc_page.get_username() == upn


def test_always_ask_credentials_checkbox_present_and_enabled(mstsc_page: RdpLogonSettingsPage):
    assert mstsc_page.is_always_ask_credentials_enabled(), (
        "'Always ask for credentials' checkbox must be enabled on the General tab"
    )


def test_always_ask_credentials_checkbox_can_be_checked(mstsc_page: RdpLogonSettingsPage):
    mstsc_page.set_always_ask_credentials(False)
    mstsc_page.set_always_ask_credentials(True)

    assert mstsc_page.is_always_ask_credentials_checked(), (
        "Checkbox must be checked after set_always_ask_credentials(True)."
    )


def test_always_ask_credentials_checkbox_can_be_unchecked(mstsc_page: RdpLogonSettingsPage):
    mstsc_page.set_always_ask_credentials(True)
    mstsc_page.set_always_ask_credentials(False)

    assert not mstsc_page.is_always_ask_credentials_checked()


def test_always_ask_credentials_checkbox_toggle_idempotency(mstsc_page: RdpLogonSettingsPage):
    initial = mstsc_page.is_always_ask_credentials_checked()

    mstsc_page.click_always_ask_credentials()
    assert mstsc_page.is_always_ask_credentials_checked() != initial, "First click must change state."

    mstsc_page.click_always_ask_credentials()
    assert mstsc_page.is_always_ask_credentials_checked() == initial, "Second click must restore state."

    mstsc_page.click_always_ask_credentials()
    assert mstsc_page.is_always_ask_credentials_checked() != initial, "Third click must change state again."


def test_settings_persist_after_tab_switch(mstsc_page: RdpLogonSettingsPage):
    computer = "persistserver"
    username = "persistuser"

    mstsc_page.set_computer(computer)
    mstsc_page.set_username(username)

    mstsc_page.select_display_tab()
    mstsc_page.select_general_tab()

    assert mstsc_page.get_computer() == computer, (
        f"Computer field lost value after tab switch. Got {mstsc_page.get_computer()!r}"
    )
    assert mstsc_page.get_username() == username, (
        f"Username field lost value after tab switch. Got {mstsc_page.get_username()!r}"
    )
