[app]
android.accept_sdk_license = True
title = الحاسبة الذكية
package.name = smartcalculator
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.permissions =
android.api = 35
android.minapi = 23
android.ndk = 27c
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
