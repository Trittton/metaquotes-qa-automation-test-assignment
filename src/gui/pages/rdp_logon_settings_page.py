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
