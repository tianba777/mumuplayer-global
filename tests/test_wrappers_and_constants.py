import re

from mumu import Mumu as ExportedMumu
from mumu.api.driver.Driver import Driver
from mumu.api.driver.bridge import Bridge
from mumu.api.permission.Permission import Permission
from mumu.api.permission.root import Root
from mumu.constant import AndroidID, AndroidKey, IMEI, IMSI, MacAddress, PhoneNumber
from mumu.mumu import Mumu
from conftest import FakeUtils


def test_package_exports_mumu():
    assert ExportedMumu is Mumu


def test_wrapper_properties_return_expected_classes():
    utils = FakeUtils()
    assert isinstance(Driver(utils).bridge, Bridge)
    assert isinstance(Permission(utils).root, Root)


def test_random_constants_formats():
    mac = MacAddress.random()
    imei = IMEI.random()
    imsi = IMSI.random()
    android_id = AndroidID.random()
    phone = PhoneNumber.random()

    assert re.match(r"^([0-9a-f]{2}:){5}[0-9a-f]{2}$", mac)
    assert imei.isdigit() and len(imei) == 15
    assert imsi.isdigit() and len(imsi) == 15
    assert re.match(r"^[0-9a-f]{16}$", android_id)
    assert phone.isdigit() and len(phone) == 11


def test_android_key_constants_are_ints():
    assert isinstance(AndroidKey.KEYCODE_HOME, int)
    assert isinstance(AndroidKey.KEYCODE_BACK, int)
    assert AndroidKey.KEYCODE_HOME == 3
    assert AndroidKey.KEYCODE_BACK == 4
