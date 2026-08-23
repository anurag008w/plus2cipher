"""
services/sharing.py

Android: uses the system share sheet via plyer (spec section 55).
Linux: plyer has no share backend there, so we fall back to copying the
text to the clipboard rather than crashing or doing nothing (section 55
explicitly calls for a "reasonable fallback").

share_text() never raises -- it returns a small result object the UI uses
to pick the right snackbar message.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import clipboard as clipboard_service


@dataclass
class ShareResult:
    ok: bool
    used_fallback: bool
    message: str


def share_text(text: str, title: str = "+2 Cipher") -> ShareResult:
    if not text:
        return ShareResult(False, False, "Nothing to share")

    try:
        from plyer import share  # provided by plyer, bundled via buildozer on Android

        share.share(text=text, title=title)
        return ShareResult(True, False, "Shared")
    except NotImplementedError:
        pass
    except Exception:
        pass

    # Fallback path (desktop Linux, or any platform without a share backend).
    if clipboard_service.copy(text):
        return ShareResult(True, True, "Share unavailable — copied to clipboard instead")
    return ShareResult(False, False, "Unable to share or copy")
