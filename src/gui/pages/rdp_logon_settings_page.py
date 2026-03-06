# Page Object for mstsc.exe — General tab, Logon Settings section.
# Run print_controls() on a new machine to discover auto_id values.

import logging

from pywinauto.application import Application

logger = logging.getLogger(__name__)

MSTSC_TITLE = "Remote Desktop Connection"
MSTSC_EXE = "mstsc.exe"
WINDOW_WAIT_TIMEOUT = 15


class RdpLogonSettingsPage:

    def __init__(self):
        self._app = None
        self._window = None

    def launch(self) -> "RdpLogonSettingsPage":
        """Start mstsc.exe and wait for the dialog.

        Uses Application.start() so the window is bound to this process,
        avoiding ElementAmbiguousError when a prior instance is still closing.
        """
        logger.info("Launching %s", MSTSC_EXE)
        self._app = Application(backend="uia").start(MSTSC_EXE)
        self._window = self._app.window(title=MSTSC_TITLE, control_type="Window")
        self._window.wait("visible", timeout=WINDOW_WAIT_TIMEOUT)
        return self

    def close(self) -> None:
        if self._window and self._window.exists():
            try:
                cancel_btn = self._window.child_window(title="Cancel", control_type="Button")
                if cancel_btn.exists(timeout=1):
                    cancel_btn.click_input()
                    self._window.wait_not("visible", timeout=5)
                    return
            except Exception as e:
                logger.warning("Cancel button close failed: %s", e)
            try:
                self._window.close()
                self._window.wait_not("visible", timeout=5)
            except Exception as e:
                logger.debug("Window close: %s", e)

    def window_exists(self) -> bool:
        return self._window is not None and self._window.exists()

    def expand_options(self) -> "RdpLogonSettingsPage":
        """Click 'Show Options' to reveal the tabbed dialog. No-op if already expanded."""
        tab_control = self._window.child_window(auto_id="5015", control_type="Tab")
        if tab_control.exists(timeout=1):
            return self

        show_btn = self._window.child_window(title="Show Options ", control_type="Button")
        show_btn.wait("exists", timeout=5)
        self._window.set_focus()
        # invoke() is more reliable than click_input() for this toolbar button
        show_btn.invoke()

        tab_control.wait("exists", timeout=10)
        logger.info("Dialog expanded")
        return self

    def select_general_tab(self) -> "RdpLogonSettingsPage":
        tab_control = self._window.child_window(auto_id="5015", control_type="Tab")
        tab_control.wait("exists", timeout=8)
        tab_control.child_window(title="General", control_type="TabItem").select()
        return self

    def select_display_tab(self) -> "RdpLogonSettingsPage":
        tab_control = self._window.child_window(auto_id="5015", control_type="Tab")
        tab_control.wait("exists", timeout=8)
        tab_control.child_window(title="Display", control_type="TabItem").select()
        return self

    def is_general_tab_visible(self) -> bool:
        try:
            return self._window.child_window(auto_id="5015", control_type="Tab").exists(timeout=2)
        except Exception:
            return False

    def is_show_options_button_visible(self) -> bool:
        try:
            return self._window.child_window(
                title="Show Options ", control_type="Button"
            ).exists(timeout=1)
        except Exception:
            return False

    def is_hide_options_button_visible(self) -> bool:
        try:
            return self._window.child_window(
                title="Hide Options ", control_type="Button"
            ).exists(timeout=1)
        except Exception:
            return False

    def set_computer(self, hostname: str) -> None:
        self._get_computer_field().set_edit_text(hostname)
        logger.info("Set Computer = %r", hostname)

    def get_computer(self) -> str:
        return self._get_computer_field().get_value()

    def clear_computer(self) -> None:
        self._get_computer_field().set_edit_text("")

    def set_username(self, username: str) -> None:
        self._get_username_field().set_edit_text(username)
        logger.info("Set Username = %r", username)

    def get_username(self) -> str:
        return self._get_username_field().get_value()

    def clear_username(self) -> None:
        self._get_username_field().set_edit_text("")

    def is_username_field_visible(self) -> bool:
        try:
            return self._get_username_field().is_visible()
        except Exception:
            return False

    def is_username_field_enabled(self) -> bool:
        try:
            return self._get_username_field().is_enabled()
        except Exception:
            return False

    def set_always_ask_credentials(self, checked: bool) -> None:
        """Set checkbox to the desired state; only clicks if state differs."""
        checkbox = self._get_always_ask_checkbox()
        current = checkbox.get_toggle_state()  # 0 = unchecked, 1 = checked
        if (checked and current == 0) or (not checked and current == 1):
            checkbox.click_input()

    def is_always_ask_credentials_checked(self) -> bool:
        return self._get_always_ask_checkbox().get_toggle_state() == 1

    def is_always_ask_credentials_enabled(self) -> bool:
        try:
            return self._get_always_ask_checkbox().is_enabled()
        except Exception:
            return False

    def click_always_ask_credentials(self) -> None:
        """Toggle the checkbox once regardless of current state."""
        self._get_always_ask_checkbox().click_input()

    def click_save_as(self) -> None:
        self._window.child_window(title="Save As...", control_type="Button").click_input()

    def click_open(self) -> None:
        self._window.child_window(title="Open...", control_type="Button").click_input()

    def is_computer_field_visible(self) -> bool:
        try:
            return self._get_computer_field().is_visible()
        except Exception:
            return False

    def print_controls(self) -> None:
        """Dump UIA control tree — useful for finding auto_id values on a new machine."""
        if self._window:
            self._window.print_control_identifiers()

    def _get_computer_field(self):
        # TODO: discover correct auto_id via print_control_identifiers
        return self._window.child_window(auto_id="CenterEdit", control_type="Edit")

    def _get_username_field(self):
        return self._window.child_window(auto_id="UserNameEdit", control_type="Edit")

    def _get_always_ask_checkbox(self):
        return self._window.child_window(
            title="Always ask for credentials",
            control_type="CheckBox",
        )
