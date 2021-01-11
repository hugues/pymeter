#!/usr/bin/env python
# encoding: utf-8

import serial
import time
import sys

#         0x01
#        ______
#       |      |
#  0x10 |      | 0x02
#       | 0x20 |
#       |______|
#       |      |
#  0x40 |      |
#       |      | 0x04
#       |______|
#         0x08


DIGITS=[0x5f, 0x06, 0x6b, 0x2f, 0x36, 0x3d, 0x7d, 0x07, 0x7f, 0x3f]
#          0     1     2     3     4     5     6     7     8     9

def digit(byte):
    d = 0
    b = byte & 0x7f
    if b in DIGITS:
        d = DIGITS.index(b)
    return d

def debug(fmt, **kwargs):
    print(fmt, **kwargs)

#
# Awful trick for reading either serial console, or input file, or stdin
#
if len(sys.argv) > 1:
    try:
        multimeter = serial.Serial(sys.argv[1], 2400)
    except Exception:
        # fallback to simple binary file (this eases debug, or other input methods)
        multimeter = open(sys.argv[1], 'rb')
else:
    multimeter = open('/dev/stdin', 'rb')


END_OF_DATA=0x55
FRAME_LENGTH=22

try:
    while True:
        data = []
        now = time.time()
        while len(data) == 0 or data[-1] != END_OF_DATA:
            byte = multimeter.read(1)
            if len(byte) == 0:
                exit()
            data.append(byte[0])
            if len(data) > FRAME_LENGTH:
                # Error, drop the frame and continue
                debug('bad frame. drop data.')
                break

        if len(data) < FRAME_LENGTH:
            # Too short (likely first loop, data is truncated)
            # drop & continue with next
            debug('too short. drop data.')
            continue
        elif data[-1] != END_OF_DATA:
            continue

        # debug
        debug('# ', end='')
        for i in range(0, len(data)):
            debug('{:02x} '.format(data[i]), end='')
        debug('')

        value = 0
        mult = 1
        power = 0
        decimal = False

        debug('#  ', end='')

        if data[8] & 0x80:
            debug('-', end='')
            # negative value
            mult *= -1

        # Read bytes from 7th to 4th to decode value
        for d in [7,6,5,4]:
            if data[d] & 0x80 or decimal:
                # this is the decimal place
                if decimal is False:
                    debug('.', end='')
                decimal = True
                power -= 1
            debug('{}'.format(digit(data[d])), end='')
            value *= 10
            value += digit(data[d])

        unit = ''
        # Read and decode the multiplier (M, K, m, µ, n)
        if data[18] & 0x40:
            unit = 'n'
            power -= 12
        elif data[18] & 0x20 or data[17] & 0x01:
            unit = 'µ'
            power -= 9
        elif data[17] & 0x02:
            unit = 'm'
            power -= 3
        elif data[17] & 0x20:
            unit = 'k'
            power += 3
        elif data[17] & 0x10:
            unit = 'M'
            power += 6

        if data[18] & 0x80:
            unit += 'F'
        elif data[18] & 0x02:
            unit += '°F'
        elif data[18] & 0x01:
            unit += '°C'
        elif data[19] & 0x80:
            unit += 'Hz'
        elif data[19] & 0x40:
            unit += '%'
        elif data[19] & 0x08:
            unit += 'V'
        elif data[19] & 0x04:
            unit += 'A'

        debug(' {:s}'.format(unit))


        debug('#  value : {}'.format(value))
        debug('#  mult : {}'.format(mult))
        debug('#  power : {}'.format(power))
        value *= mult * 10 ** power

        print('{}'.format(value))

except KeyboardInterrupt:
    debug('-- EOT --')
