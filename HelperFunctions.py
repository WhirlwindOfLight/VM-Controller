from os import path

import pyudev


def EventStruct(event, value):
    return {
        "event": event,
        "value": value
    }


def getDevPath(name, vendorNo=None, prodNo=None):
    for device in pyudev.Context().list_devices(subsystem="input"):
        try:
            assert device.parent is not None
            # Note: We have to search the parent for vendor, product, and name
            # because the devname is in a child of a main object,
            # and we need to be the child
            if vendorNo is not None:
                if vendorNo != device.parent.attributes.asstring("id/vendor"):
                    continue
            if prodNo is not None:
                if prodNo != device.parent.attributes.asstring("id/product"):
                    continue
            if name != device.parent.attributes.asstring("name"):
                continue
            for attr in device.attributes.asstring("uevent").split("\n"):
                if "DEVNAME=" in attr and "event" in attr:
                    return path.join("/dev", attr.replace("DEVNAME=", ""))
        except KeyError:
            continue
        except AttributeError:
            continue
        except AssertionError:
            continue
