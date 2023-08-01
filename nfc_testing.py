import nfc
from ndef import TextRecord
import pygame

reader = nfc.ContactlessFrontend('usb')
from nfc.clf import RemoteTarget

while True:
    pygame.time.delay(500)
    target = reader.sense(RemoteTarget('106A'), RemoteTarget('106B'), RemoteTarget('212F'))

    if target is not None:
        try:
            myTag = nfc.tag.activate(reader, target)
            print(myTag.identifier)
            print(myTag.ndef.capacity)

        except AttributeError:
            print("read failed :(")

# My work ID's identifier
# b'\x04I}\n\xcf\x15\x90'