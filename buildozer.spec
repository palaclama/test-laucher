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
android.permissions = QUERY_ALL_PACKAGES
android.api = 35
android.minapi = 23
android.ndk = 27c
android.accept_sdk_license = True
android.manifest.intent_filters = android.intent.action.MAIN
android.manifest.intent_filters = android.intent.category.LAUNCHER
android.manifest.intent_filters = android.intent.category.HOME
android.manifest.intent_filters = android.intent.category.DEFAULT

[buildozer]
log_level = 2
warn_on_root = 1
