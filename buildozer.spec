[app]

title = +2 Cipher
package.name = plus2cipher
package.domain = com.example

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,ttf
source.exclude_dirs = tests,tests_manual,.github,.git,.venv,venv,bin,__pycache__
source.exclude_patterns = assets/icons/app_icon_source.png,assets/icons/icon_master.png,*.pyc,*.pyo,*.spec.bak

version = 1.0.0

requirements = python3,kivy==2.3.1,plyer==2.1.0

# +2 Cipher is a text-shift utility, not a game -- support both main
# orientations since the responsive layout system handles both cleanly.
orientation = portrait,landscape
fullscreen = 0

icon.filename = %(source.dir)s/assets/icons/icon_512.png
presplash.filename = %(source.dir)s/assets/icons/icon_512.png
presplash.color = #070A13

# No network, no accounts, no analytics (spec section 53) -- so no
# permissions beyond what the OS grants by default. Clipboard and the
# system share sheet do not require a manifest permission on Android.
android.permissions =

android.api = 34
# Python 3.14 (what current python-for-android builds) uses preadv/pwritev
# in Python/remote_debugging.c, which Android's libc only declares from
# API 24 (Android 7.0) onward. Below that, the NDK sysroot headers don't
# expose them and the build fails with an implicit-declaration error.
# API 24 is a non-issue in practice (~0% of active devices are below it).
android.minapi = 24
android.ndk = 25b
android.build_tools = 34.0.0
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True
android.logcat_filters = *:S python:D

# Required for non-interactive CI builds -- without this, sdkmanager blocks
# on an interactive license prompt that GitHub Actions can never answer,
# and the build fails with "license is not accepted" even though nothing
# is actually broken.
android.accept_sdk_license = True

p4a.branch = master
# Pinned instead of floating on master's tip: your cached p4a checkout in
# CI never auto-updates (buildozer only re-pulls when platform_update is
# set, e.g. via `buildozer android update`), so it was stuck on an old
# master commit whose venv bootstrap ran `pip install -U pip` mid-build --
# that self-upgrade corrupts pip's own site-packages, causing
# "ImportError: cannot import name 'BuildDependencyInstallError'".
# Current master (7af1d13, 2026-08-09) already dropped that self-upgrade
# step and carries the 3.14 remote-debugging patch this app needs, so
# pin to it for a reproducible, working build.
p4a.commit = 7af1d1325ef460def993cc7871c43d04bc877a94

[buildozer]
log_level = 2
warn_on_root = 1
