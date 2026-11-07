[app]

title = Black Launcher
package.name = blacklauncher
package.domain = org.codex

source.dir = .
source.include_exts = py,png,jpg,kv
version = 1.0

requirements = python3,kivy,pyjnius
orientation = portrait
fullscreen = 1

android.permissions = android.permission.QUERY_ALL_PACKAGES
android.api = 35
android.minapi = 23
android.ndk = 27c
android.accept_sdk_license = True
android.home_app = True

[buildozer]

log_level = 2
warn_on_root = 1
