#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import argparse
import serial.serialposix as s

# os.system('sudo systemctl disable hciuart')

class vedirect:

    def __init__(self, serialport, timeout):
        self.serialport = '/dev/ttyAMA0'
        self.ser = s.Serial('/dev/ttyAMA0', 19200, timeout=timeout)
        self.header1 = '\r'
        self.header2 = '\n'
        self.hexmarker = ':'
        self.delimiter = '\t'
        self.key = ''
        self.value = ''
        self.bytes_sum = 0
        self.state = self.WAIT_HEADER
        self.dict = {}
        print('1')

    (HEX, WAIT_HEADER, IN_KEY, IN_VALUE, IN_CHECKSUM) = range(5)

    def input(self, byte):
        print('2')
        if byte == self.hexmarker and self.state != self.IN_CHECKSUM:
            self.state = self.HEX

        if self.state == self.WAIT_HEADER:
            self.bytes_sum += ord(byte)
            if byte == self.header1:
                self.state = self.WAIT_HEADER
            elif byte == self.header2:
                self.state = self.IN_KEY
            return None

        elif self.state == self.IN_KEY:
            self.bytes_sum += ord(byte)
            if byte == self.delimiter:
                if self.key == 'Checksum':
                    self.state = self.IN_CHECKSUM
                else:
                    self.state = self.IN_VALUE
            else:
                self.key += byte
            return None

        elif self.state == self.IN_VALUE:
            self.bytes_sum += ord(byte)
            if byte == self.header1:
                self.state = self.WAIT_HEADER
                self.dict[self.key] = self.value;
                self.key = '';
                self.value = '';
            else:
                self.value += byte
            return None

        elif self.state == self.IN_CHECKSUM:
            self.bytes_sum += ord(byte)
            self.key = ''
            self.value = ''
            self.state = self.WAIT_HEADER
            if (self.bytes_sum % 256 == 0):
                self.bytes_sum = 0
                return self.dict
            else:
                print('Malformed packet')
                self.bytes_sum = 0

        elif self.state == self.HEX:
            self.bytes_sum = 0
            if byte == self.header2:
                self.state = self.WAIT_HEADER

        else:
            raise AssertionError()


    def read_data(self):
        print('3')
        while True:
            byte = self.ser.read(1)
            packet = self.input(byte)


    def read_data_single(self):
        print('4')
        while True:
            byte = self.ser.read(1)
            packet = self.input(byte)
            if (packet != None):
                return packet


    def read_data_callback(self, callbackFunction):
        print('5')
        while True:
            print('hello')
            byte = self.ser.read(1)
            print(byte)
            print('im here')
            if byte:
                packet = self.input(byte)
                if (packet != None):
                    callbackFunction(packet)
            else:
                break


def print_data_callback(data):
    print('6')
    print(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process VE.Direct protocol')
    parser.add_argument('--port', help='Serial port')
    parser.add_argument('--timeout', help='Serial port read timeout', type=int, default='60')
    print('main')
    args = parser.parse_args()
    ve = vedirect(args.port, args.timeout)
    ve.read_data_callback(print_data_callback)
    #print(ve.read_data_single())
