#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import serial
import struct
from threading import Thread
import math
from random import randint


class crc8(object):
    """
    CRC8 is provided to detect or verify possible errors after data transmission or saving. It uses the principle of
    division and remainder to detect errors
    """
    crcTable = [0x00, 0x5E, 0xBC, 0xE2, 0x61, 0x3F, 0xDD, 0x83,
                0xC2, 0x9C, 0x7E, 0x20, 0xA3, 0xFD, 0x1F, 0x41,
                0x9D, 0xC3, 0x21, 0x7F, 0xFC, 0xA2, 0x40, 0x1E,
                0x5F, 0x01, 0xE3, 0xBD, 0x3E, 0x60, 0x82, 0xDC,
                0x23, 0x7D, 0x9F, 0xC1, 0x42, 0x1C, 0xFE, 0xA0,
                0xE1, 0xBF, 0x5D, 0x03, 0x80, 0xDE, 0x3C, 0x62,
                0xBE, 0xE0, 0x02, 0x5C, 0xDF, 0x81, 0x63, 0x3D,
                0x7C, 0x22, 0xC0, 0x9E, 0x1D, 0x43, 0xA1, 0xFF,
                0x46, 0x18, 0xFA, 0xA4, 0x27, 0x79, 0x9B, 0xC5,
                0x84, 0xDA, 0x38, 0x66, 0xE5, 0xBB, 0x59, 0x07,
                0xDB, 0x85, 0x67, 0x39, 0xBA, 0xE4, 0x06, 0x58,
                0x19, 0x47, 0xA5, 0xFB, 0x78, 0x26, 0xC4, 0x9A,
                0x65, 0x3B, 0xD9, 0x87, 0x04, 0x5A, 0xB8, 0xE6,
                0xA7, 0xF9, 0x1B, 0x45, 0xC6, 0x98, 0x7A, 0x24,
                0xF8, 0xA6, 0x44, 0x1A, 0x99, 0xC7, 0x25, 0x7B,
                0x3A, 0x64, 0x86, 0xD8, 0x5B, 0x05, 0xE7, 0xB9,
                0x8C, 0xD2, 0x30, 0x6E, 0xED, 0xB3, 0x51, 0x0F,
                0x4E, 0x10, 0xF2, 0xAC, 0x2F, 0x71, 0x93, 0xCD,
                0x11, 0x4F, 0xAD, 0xF3, 0x70, 0x2E, 0xCC, 0x92,
                0xD3, 0x8D, 0x6F, 0x31, 0xB2, 0xEC, 0x0E, 0x50,
                0xAF, 0xF1, 0x13, 0x4D, 0xCE, 0x90, 0x72, 0x2C,
                0x6D, 0x33, 0xD1, 0x8F, 0x0C, 0x52, 0xB0, 0xEE,
                0x32, 0x6C, 0x8E, 0xD0, 0x53, 0x0D, 0xEF, 0xB1,
                0xF0, 0xAE, 0x4C, 0x12, 0x91, 0xCF, 0x2D, 0x73,
                0xCA, 0x94, 0x76, 0x28, 0xAB, 0xF5, 0x17, 0x49,
                0x08, 0x56, 0xB4, 0xEA, 0x69, 0x37, 0xD5, 0x8B,
                0x57, 0x09, 0xEB, 0xB5, 0x36, 0x68, 0x8A, 0xD4,
                0x95, 0xCB, 0x29, 0x77, 0xF4, 0xAA, 0x48, 0x16,
                0xE9, 0xB7, 0x55, 0x0B, 0x88, 0xD6, 0x34, 0x6A,
                0x2B, 0x75, 0x97, 0xC9, 0x4A, 0x14, 0xF6, 0xA8,
                0x74, 0x2A, 0xC8, 0x96, 0x15, 0x4B, 0xA9, 0xF7,
                0xB6, 0xE8, 0x0A, 0x54, 0xD7, 0x89, 0x6B, 0x35]

    def crc8(self, data_bytes):
        """
        CRC8 received packet data integrity check using predefined cyclic redundancy check table
        :param data_bytes: bytes of received data
        :return: crc = amount of bytes in received data if there are no errors
        """
        crc = 0
        for byte in data_bytes:
            crc = self.crcTable[crc ^ byte]
        return crc


class us_nav(Thread):
    def __init__(self, serial_port="/dev/ttyUSB0", debug=False):
        Thread.__init__(self)
        self.debug = debug
        if not self.debug:
            # Initialize serial connection through RS-485 using given port and other parameters
            self.ser = serial.Serial()
            self.ser.port = serial_port
            self.ser.baudrate = 57600
            self.ser.parity = serial.PARITY_NONE
            self.ser.stopbits = serial.STOPBITS_ONE
            self.ser.bytesize = serial.EIGHTBITS

        self._run = True
        self.idx = 0
        self.size = 0
        self.buffer = bytearray(260)
        self.crc8 = crc8().crc8

        """
        __TELEMETRY_PACKET structure: uint8_t start B
                                      uint8_t size B
                                      uint8_t addr B
                                      uint8_t event B
                                      uint32_t orientations I
                                      int32_t pos[3] 3i
                                      int16_t vel[3] 3h
                                      uint16_t voltage H
                                      uint8_t beacons B
                                      uint8_t status B
                                      uint8_t posError B
                                      NUL byte x
        """
        self.__TELEMETRY_PACKET = '<BBBBI3i3hHBBBx'
        self.__SYS_STATUS_PACKET = '<HBBII'
        """
        __INFO_PACKET structure:uint16_t hwId H
                                uint16_t fwType H
                                uint16_t fwVersion H
                                uint8_t protoMinor B
                                uint8_t protoMajor B
                                uint32_t commit I
                                uint16_t commitCount H
        """
        self.__INFO_PACKET = '<HHHBBIH'
        """
        __RAW_ACCEL_PACKET structure: int16_t accel[3] 3h
        """
        self.__RAW_ACCEL_PACKET = '<3h'
        self.__STRENGTH_PACKET = '<hhhh'
        self.__EV_TELEMETRY = 0x02
        self.__EV_SYS_STATUS = 0x08
        self.__EV_INFO = 0x18
        self.__EV_RAW_ACCEL = 0x1D
        self.__EV_STRENGTH = 0x33
        self.__ANGLE_SCALE = 360 / 2 ** 11

        self.tel_received = False
        self.h_start = None
        self.h_size = None
        self.h_addr = None
        self.h_event = None
        self.roll = None
        self.pitch = None
        self.yaw = None
        self.x = None
        self.y = None
        self.z = None
        self.vX = None
        self.vY = None
        self.vZ = None
        self.voltage = None
        self.beacons = None
        self.status = None
        self.pos_error = None

        self.hwld = None
        self.fwType = None
        self.fwVersion = None
        self.protoMinor = None
        self.protoMajor = None
        self.commit = None
        self.commitCount = None

        self.rawAccel = None

        self.levels = None
        if not self.debug:
            try:
                self.ser.open()
            except Exception as e:
                print("error open serial port: " + str(e))
                self._run = False

    def run(self):
        if not self.debug:
            self.ser.flushInput()
            self.ser.flushOutput()
            while self._run:
                try:
                    data_len = self.ser.inWaiting()
                    if data_len > 0:
                        data = self.ser.read(data_len)
                        i = 0
                        while i < data_len:
                            if self.idx == 0:
                                if data[i] == 0xFE:
                                    self.idx += 1
                                i += 1
                            elif self.idx == 1:
                                self.buffer[self.idx] = data[i]
                                self.size = data[i] + 4
                                i += 1
                                self.idx += 1
                            elif self.idx < self.size:
                                block_len = min(self.size - self.idx, data_len - i)
                                self.buffer[self.idx: self.idx+block_len] = data[i: i+block_len]
                                self.idx += block_len
                                i += block_len
                            else:
                                if data[i] == self.crc8(self.buffer[1:self.size]):
                                    self.parse_packet(self.buffer[:self.size])
                                else:
                                    crc_packet = self.buffer[:self.size]
                                    print("crc error: id %d, size %d" % (crc_packet[3], self.size))
                                self.idx = 0
                                i += 1

                except Exception as e:
                    print("Error occurred:" + str(e))
        else:
            while self._run:
                self.parse_packet(None)
                time.sleep(0.1)

    def parse_packet(self, packet):
        if packet is None:
            self.x = randint(0, 105) * 100
            self.y = randint(0, 105) * 100
            self.z = randint(0, 40) * 100
            self.roll = randint(0, 900) / 10 - 45
            self.pitch = randint(0, 900) / 10 - 45
            self.yaw = randint(0, 900) / 10 - 45
            self.levels = [randint(2, 2500), randint(2, 2500), 300, 1000]
            self.beacons = 0b1010
            return
        if packet[3] == self.__EV_TELEMETRY:  # '<BBBBI3i3hHBBBx', no packet length check?
            # print(''.join('{:02x}'.format(x) for x in packet))
            self.tel_received = True
            self.h_start, self.h_size, self.h_addr, self.h_event, orientation, self.x, self.y, self.z, self.vX, \
                self.vY, self.vZ, self.voltage, self.beacons, self.status, \
                self.pos_error = struct.unpack_from(self.__TELEMETRY_PACKET, packet, 0)
            # print("addr {}: ".format(self.h_addr), len(packet))
            self.roll = round(((orientation & 0b11111111111) * math.pi / 1024), 3)  # * self.__ANGLE_SCALE #11 bit
            self.pitch = round(((orientation >> 11 & 0b1111111111) * math.pi / 1024), 3)  # * self.__ANGLE_SCALE #10 bit
            self.yaw = round(((orientation >> 21 & 0b11111111111) * math.pi / 102), 3)  # * self.__ANGLE_SCALE #11 bit
        elif packet[3] == self.__EV_SYS_STATUS and len(packet) == 16:
            ident, cfg_status, log_status, logger_capacity, log_size = \
                struct.unpack_from(self.__SYS_STATUS_PACKET, packet, 4)
            # print(ident, cfg_status, log_status, logger_capacity, log_size)
        elif packet[3] == self.__EV_INFO:  # '<HHH2BBBIH', no packet length check?
            self.hwld, self.fwType, self.fwVersion, self.protoMinor, self.protoMajor, self.commit, \
                self.commitCount = struct.unpack_from(self.__INFO_PACKET, packet, 4)
        elif packet[3] == self.__EV_RAW_ACCEL:  # '<3h', no packet length check?
            raw_a, raw_b, raw_c = struct.unpack_from(self.__RAW_ACCEL_PACKET, packet, 4)
            self.rawAccel = (raw_a, raw_b, raw_c)
        elif packet[3] == self.__EV_STRENGTH and len(packet) == 12:
            level1, level2, level3, level4 = struct.unpack_from(self.__STRENGTH_PACKET, packet, 4)
            self.levels = [level1, level2, level3, level4]
        else:
            # print('unknown packet... ' + str(hex(packet[3])))
            pass

    def telemetry_received(self):
        if self.tel_received and self.h_addr is not None:
            self.tel_received = False
            return True
        else:
            return None

    def get_telemetry(self):
        return self.h_start, self.h_size, self.h_addr, self.h_event, self.roll, self.pitch, self.yaw, \
            self.x/1000.0, self.y/1000.0, self.z/1000.0, self.vX, self.vY, self.vZ, self.voltage/1000.0, \
            self.beacons, self.status, self.pos_error

    def get_info(self):
        return self.hwld, self.fwType, self.fwVersion, self.protoMinor, self.protoMajor, self.commit, \
                self.commitCount

    def get_rawAccel(self):
        return self.rawAccel

    def get_addr(self):
        if self.h_addr is not None:
            return self.h_addr
        else:
            return None

    def get_angles(self):
        if self.roll is not None and  self.pitch is not None and self.yaw is not None:
            return [math.degrees(self.roll), math.degrees(self.pitch), math.degrees(self.yaw)]
        else:
            return None

    def get_position(self):
        if self.x is not None and  self.y is not None and self.z is not None and self.beacons is not None:
            return [self.x/1000.0, self.y/1000.0, self.z/1000.0], self.beacons
        else:
            return [0.0, 0.0, 0.0], 0

    def get_strength(self):
        if self.levels is not None:
            return self.levels
        else:
            return None

    def get_vel(self):
        return [self.vX, self.vY, self.vZ]

    def get_status(self):
        return self.status

    def stop(self):
        self._run = False
        if not self.debug:
            self.ser.close()
