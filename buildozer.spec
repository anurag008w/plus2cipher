[app]

title = +2 Cipher
package.name = plus2cipher
package.domain = com.example

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,ttf
source.exclude_dirs = tests,tests_manual,.github,.git,.venv,venv,bin,__pycache__
source.exclude_patterns = assets/icons/app_icon_source.png,assets/icons/icon_master.png,*.pyc,*.pyo,*.spec.bak

version = 1.0.0

requirements = python3,kivy==2.3.1,kivymd==1.2.0,plyer==2.1.0

# +2 Cipher is a text-shift utility, not a game -- support both
# orientations since the responsive layout system handles both cleanly.
orientation = all
fullscreen = 0

icon.filename = %(source.dir)s/assets/icons/icon_512.png
presplash.filename = %(source.dir)s/assets/icons/icon_512.png
presplash.color = #070A13

# No network, no accounts, no analytics (spec section 53) -- so no
# permissions beyond what the OS grants by default. Clipboard and the
# system share sheet do not require a manifest permission on Android.
android.permissions =

android.api = 34
android.minapi = 23
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True
android.logcat_filters = *:S python:D

p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
