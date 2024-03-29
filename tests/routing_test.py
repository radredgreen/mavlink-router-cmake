#!/usr/bin/python3

# This file is part of the MAVLink Router project
#
# Copyright (C) 2017  Intel Corporation. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from threading import Thread
from time import sleep

import argparse
import functools
import subprocess
import sys
import time
from pymavlink import mavutil

SENDER_NUM_MESSAGES = 10


class MavlinkSender(Thread):
    '''MavlinkSender sends some ping messages to a system and collects the answers'''
    def __init__(self, name, port, sysId, compId, targetSysId, targetCompId):
        super().__init__()
        self.name = name
        self.sysId = sysId
        self.compId = compId
        self.targetSysId = targetSysId
        self.targetCompId = targetCompId
        self.mav = mavutil.mavlink_connection('udpout:127.0.0.1:' + str(port),
                                              source_system=self.sysId,
                                              source_component=self.compId)
        self.sender_thread = Thread(target=self.send_loop)
        self.received = []
        self.success = True

    def send_loop(self):
        for i in range(0, SENDER_NUM_MESSAGES):
            self.mav.mav.ping_send(int(time.time() * 1000), i,
                                   self.targetSysId, self.targetCompId)
            sleep(0.5)

    def run(self):
        self.sender_thread.start()

        while True:
            msg = self.mav.recv_match(blocking=True, timeout=5)
            if msg is not None:
                if msg.target_system == 0:
                    continue  # Just discard any broadcast ping we may receive

                if self.targetSysId != 0 and msg.get_srcSystem(
                ) != self.targetSysId:
                    print(
                        f"Received unexpected response from {msg.get_srcSystem()}/{msg.get_srcComponent()} - current target: {self.targetSysId}/{self.targetCompId}"
                    )
                    self.success = False

                # TODO maybe check if no message sent has seq bigger than any sent?
                self.received.append(msg)
            else:
                break

    def accept(self, func):
        return self.success and func(self.received)


class MavlinkReceiver(Thread):
    '''MavlinkReceiver collects incoming ping messages and returns a reply'''
    def __init__(self, name, port, sysId, compId):
        super().__init__()
        self.name = name
        self.sysId = sysId
        self.compId = compId
        self.mav = mavutil.mavlink_connection('udpin:127.0.0.1:' + str(port),
                                              source_system=self.sysId,
                                              source_component=self.compId)
        self.received = []
        self.success = True

    def run(self):
        while True:
            msg = self.mav.recv_match(blocking=True, timeout=5)
            if msg is not None:
                self.received.append(msg)
                if msg.target_system not in [0, self.sysId]:
                    print(
                        f"Received unexpected message from: {msg.get_srcSystem()}/{msg.get_srcComponent()}, meant to {msg.target_system}/{msg.target_component} - current receiver: {self.sysId}/{self.compId}"
                    )
                    self.success = False
                self.mav.mav.ping_send(int(time.time() * 1000), msg.seq,
                                       msg.get_srcSystem(),
                                       msg.get_srcComponent())
            else:
                break

    def accept(self, func):
        return self.success and func(self.received)


def expect_len(name, msgs, expected):
    if len(msgs) != expected:
        print(f"{name} expected {expected} messages, got {len(msgs)}")
        return False
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='MAVLink Router Message Routing System Test')
    parser.add_argument("-b",
                        "--binary",
                        default="./build/src/mavlink-routerd",
                        help="path to mavlink-routerd")
    args = parser.parse_args()

    # Setup mavlink-router
    with subprocess.Popen([
            args.binary, "-e", "127.0.0.1:10100", "-e", "127.0.0.1:10101",
            "127.0.0.1:10000", "-c", "/nonexistent"
    ],
                          stderr=sys.stdout.fileno(),
                          stdout=sys.stdout.fileno()) as proc:

        # Two senders: one send to all (target 0). The other sends to target 100/1
        sender0 = MavlinkSender("sender0", 10000, 1, 1, 0, 0)
        sender100 = MavlinkSender("sender100", 10000, 2, 1, 100, 1)

        # Two receivers
        receiver100 = MavlinkReceiver("receiver100", 10100, 100, 1)
        receiver101 = MavlinkReceiver("receiver101", 10101, 101, 1)

        sender100.start()
        # Wait a bit before starting broadcaster pinger
        time.sleep(0.2)
        sender0.start()

        receiver100.start()
        receiver101.start()

        sender0.join()
        sender100.join()

        receiver100.join()
        receiver101.join()

        proc.terminate()

        results = []

        # Sender0 should receive 20 replies - 10 from each receiver
        results.append(
            sender0.accept(lambda msgs: expect_len(sender0.name, msgs,
                                                   (SENDER_NUM_MESSAGES * 2))))

        # Sender100 OTOH, should receive only 9. It first message
        # should be delivered to no-one, as mavlink-router doesn't know
        # Receiver100 until it responds a message.
        results.append(
            sender100.accept(lambda msgs: expect_len(sender100.name, msgs, (
                SENDER_NUM_MESSAGES - 1))))

        # Receiver101 should only get messages sent to all - 10 from sender0
        results.append(
            receiver101.accept(lambda msgs: expect_len(receiver101.name, msgs,
                                                       SENDER_NUM_MESSAGES)))

        # Receiver100 should only get 19 messages, as it first specific
        # message should be lost, as mavlink-router doesn't know it
        # before it answers first broadcast ping
        results.append(
            receiver100.accept(
                lambda msgs: expect_len(receiver100.name, msgs, (
                    SENDER_NUM_MESSAGES + SENDER_NUM_MESSAGES - 1))))

        if functools.reduce((lambda p, q: p and q), results):
            print("Routing test OK")
            sys.exit(0)
        else:
            print(
                "Routing test FAILED. See previous output for more information"
            )
            sys.exit(1)
