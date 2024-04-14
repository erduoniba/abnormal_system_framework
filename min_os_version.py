import plistlib


def read_minimum_os_version(app_path):
    info_plist_path = app_path + "/" + "info.plist"
    try:
        with open(info_plist_path, 'rb') as f:
            data = plistlib.load(f)
        return data.get('MinimumOSVersion'), data.get('CFBundleShortVersionString'), data.get('CFBundleVersion')
    except (KeyError, FileNotFoundError):
        return None
