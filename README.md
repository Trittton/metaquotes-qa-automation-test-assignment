# MetaQuotes QA Automation — Test Assignment

[Assignment brief](https://www.metaquotes.net/ru/company/vacancies/tests/senior-automation-qa-engineer)

Two tasks: REST API tests for `POST /pet/{petId}` on the Petstore Swagger v2 demo, and Windows GUI tests for the mstsc.exe Logon Settings section (General tab).

## Setup and running

Requirements: Python 3.11+, Windows (for GUI tests), internet access to reach the Petstore server.

```bash
pip install -r requirements.txt
```

```bash
pytest                          # everything
pytest -m smoke -v              # happy-path subset, fastest
pytest tests/api/ -m api -v     # API only
pytest tests/gui/ -m gui -v     # GUI only — Windows required
pytest -m negative -v           # known-bad-input cases
```

HTML report: `pytest --html=reports/report.html --self-contained-html`

GUI tests are auto-skipped on non-Windows.

## What's covered and what isn't

**API — `POST /pet/{petId}`**

I tested the two writable fields individually and together, all three valid status enum values, and a handful of negative paths — alphabetic ID, zero/negative IDs, a nonexistent ID, a 10 000-char name, five special characters (unicode, XSS payload, SQL fragment, emoji, null bytes), and wrong content type. Response schema is validated against the spec's `ApiResponse` shape.

I didn't test concurrent updates or rate limiting — the demo server is shared state and I can't control what else hits it, so those would be unreliable noise. Authentication isn't tested because the Petstore has none.

Three of the ID/status tests are marked `xfail` because the server deviates from its own spec (accepts petId=0, negative IDs, and an invalid status value). The tests still run and document the actual behaviour; they'll flip to normal passing tests if the server is ever fixed.

**GUI — mstsc.exe, General tab**

Covered: collapsed vs expanded state, the two text fields (Computer, Username) with realistic input formats (hostname, IP, `host:port`, domain username, UPN), the "Always ask for credentials" checkbox (check, uncheck, three-click toggle sequence), persistence across a Display tab round-trip, and open/close lifecycle.

The `Save As...` and `Open...` buttons exist in the page object but aren't tested — saving `.rdp` files creates disk artefacts with cleanup requirements that felt out of scope for a Logon Settings check.

## Markers

```
smoke      — minimal happy-path subset; run these first for quick sanity
negative   — invalid/edge input; tests assert on actual server behaviour
api        — all Petstore tests
gui        — all mstsc tests
```

## Design notes

**Why UIA backend and not win32.** mstsc.exe is a modern WPF application; the win32 backend misses most of its controls. UIA exposes them cleanly by `auto_id` and control type.

**Two fixture levels for GUI.** `mstsc_raw` is just a launched process; `mstsc_page` is raw + expanded + General tab selected. Tests that verify the collapsed state use `mstsc_raw` directly so the expand step doesn't interfere.

**Function-scoped GUI fixtures.** Fresh mstsc.exe per test. Slower, but shared process state between GUI tests causes subtle ordering bugs that are painful to diagnose.

**Client returns raw responses.** `PetstoreApiClient` makes no assertions. When a test fails, the message always comes from the test itself, not from somewhere inside a helper.

**`auto_id` fallback in locator methods.** mstsc exposes different `auto_id` values in collapsed vs expanded state, and the values vary between Windows builds. The `_get_computer_field()` method tries the expanded-state ID first, falls back to the collapsed-state one, and uses positional index as a last resort. Not elegant, but it's a real quirk of the app rather than a design preference.

## First-time GUI setup (new machine)

If controls aren't found, the `auto_id` values on your machine may differ from the ones hardcoded in the page object. Open mstsc.exe, then run:

```python
from pywinauto import Desktop
w = Desktop(backend="uia").window(title="Remote Desktop Connection")
w.wait("visible", timeout=10)
w.print_control_identifiers()
```

Copy the relevant values into the `_get_*()` methods in `src/gui/pages/rdp_logon_settings_page.py`.

## What I'd add with more time

- A mock for the Petstore endpoint — the shared demo server makes some tests occasionally flaky because other clients can modify pet data between the update call and the GET verification
- A test for hiding options (collapsing back from the expanded state)
- Separate HTML report paths per suite so running API and GUI jobs independently doesn't overwrite each other's results
- A minimal CI config — at least running the API tests on push since they don't need Windows
