# -*- coding: utf-8 -*-
"""ANT+ Stride Based Speed and Distance Monitor Device Profile

"""
# pylint: disable=not-context-manager,protected-access
##############################################################################
#
# Copyright (c) 2017, Matt Hughes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
##############################################################################

from __future__ import print_function

from threading import Lock
import struct

from plus import _EventHandler


class StrideCallback(object):
    """Receives stride events.
    """

    def device_found(self, device_number, transmission_type):
        """Called when a device is first detected.

        The callback receives the device number and transmission type.
        When instantiating the HeartRate class, these can be supplied
        in the device_id and transmission_type keyword parameters to
        pair with the specific device.
        """
        pass

    def stride_data(self, num_steps, distance_m):
        """Called when stride data is received.

        The number of steps and the distance travelled in meters since
        the device was found is provided.
        """


class Stride(object):
    """ANT+ Stride Based and Speed and Distance Monitor

    """

    def __init__(self, node, network, device_id=0, transmission_type=0, callback=None):
        """TODO

        """
        self._event_handler = _EventHandler(self, node)

        self.callback = callback

        self.lock = Lock()

        self._detected_device = None

        self._stride_count = None
        self._calories = None
        self._hw_revision = None
        self._manufacturer_id = None
        self._model_number = None
        self._sw_revision = None
        self._serial_number = None

        CHANNEL_FREQUENCY = 0x39
        CHANNEL_PERIOD = 8134
        DEVICE_TYPE = 0x7c
        SEARCH_TIMEOUT = 30
        self._event_handler.open_channel(network, CHANNEL_FREQUENCY, CHANNEL_PERIOD,
                                         transmission_type, DEVICE_TYPE,
                                         device_id, SEARCH_TIMEOUT)

    def _set_data(self, data):
        # ChannelMessage prepends the channel number to the message data
        # (Incorrectly IMO)
        data_size = 9
        payload_offset = 1

        if len(data) != data_size:
            return

        with self.lock:
            data_page_index = 0 + payload_offset
            device_page = data[data_page_index]

            if device_page == 0x01:
                stride_count_index = 6 + payload_offset
                self._stride_count = data[stride_count_index]

            elif device_page == 0x02:
                print("page 2, template")

            elif device_page == 0x03:
                calories_index = 6 + payload_offset
                self._calories = data[calories_index]

            elif device_page == 0x10:
                print("page 16, Distance & Strides Since Battery Reset")

            elif device_page == 0x16:
                print("page 22, capabilities")

            elif device_page == 0x50:
                self._hw_revision = data[3 + payload_offset]

                lsb = data[4 + payload_offset]
                msb = data[5 + payload_offset]
                self._manufacturer_id = 256 * msb + lsb

                lsb = data[6 + payload_offset]
                msb = data[7 + payload_offset]
                self._model_number = 256 * msb + lsb

            elif device_page == 0x51:
                self._sw_revision = data[3 + payload_offset]
                self._serial_number = struct.unpack('>L', data[4 + payload_offset:8 + payload_offset])[0]

    @property
    def detected_device(self):
        """A tuple representing the detected device.

        This is of the form (device_number, transmission_type). This should
        be accessed when pairing to identify the monitor that is connected.
        To specifically connect to that monitor in the future, provide the
        result to the Stride constructor:

        Stride(node, network, device_number, transmission_type)
        """
        return self._detected_device

    @property
    def stride_count(self):
        """Accumulated Strides.
        """
        strides = None
        with self.lock:
            strides = self._stride_count

        return strides

    @property
    def hardware_revision(self):
        """The hardware revision of the connected device.

        If the data page 80 has not been received yet, this will be None.
        """
        hw_rev = None
        with self.lock:
            hw_rev = self._hw_revision
        return hw_rev

    @property
    def manufacturer_id(self):
        """The manufacturer id of the connected device.

        If the data page 80 has not been received yet, this will be None.
        """
        manufacturer_id = None
        with self.lock:
            manufacturer_id = self._manufacturer_id

        return manufacturer_id

    @property
    def model_number(self):
        """The model number of the connected device.

        If the data page 80 has not been received yet, this will be None.
        """
        model_number = None
        with self.lock:
            model_number = self._model_number

        return model_number

    @property
    def software_revision(self):
        """The software revision of the connected device.

        If the data page 81 has not been received yet, this will be None.
        """
        sw_rev = None
        with self.lock:
            sw_rev = self._sw_revision

        return sw_rev

    @property
    def serial_number(self):
        """The serial number of the connected device.

        If the data page 81 has not been received yet, this will be None.
        """
        serial = None
        with self.lock:
            serial = self._serial_number

        return serial