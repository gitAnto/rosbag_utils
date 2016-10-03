#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rosbag
import rospy
import time
import sys
import os
import argparse
import threading
import random
from rosbag import Bag
from numpy import argmin, argmax


class EndOfBagException(Exception): pass

class InputBag():

    def __init__(self, filepath, rebase_time):
        self.filepath = filepath
        self.bag = Bag(self.filepath, 'r')
        self.message_count = self.bag.get_message_count()
        self.message_index = 0
        self.retrieve_message_offsets()
        self.retrieve_time_start()
        self.calculate_time_offset(rebase_time)

    def get_next_message(self):
        i = self.get_next_message_index()
        r = self.read_message_by_index(i)
        return self.rebase_message(r)

    def rebase_message(self, data):
        data_mod = data
        new_time = data.timestamp + self.time_offset
        data_mod = data_mod._replace(timestamp = new_time)
        try:
            data_mod.message.header = self.rebase_header(data_mod.message.header, new_time)
        except: pass
        try:
            for i in data_mod.message.transforms:
                i.header = self.rebase_header(i.header, new_time)
        except: pass
        return data_mod

    def rebase_header(self, header, new_time):
        header.stamp.secs  = header_time.secs
        header.stamp.nsecs = header_time.nsecs
        return header

    def read_message_by_index(self, index):
        position = self.message_offsets[index]
        r = self.bag._reader.seek_and_read_message_data_record(position, False)
        return r

    def retrieve_time_start(self):
        first_message = self.read_message_by_index(0)
        self.time_start = first_message.timestamp

    def calculate_time_offset(self, rebase_time):
        random_time = rospy.Duration().from_sec(random.uniform(0, 0.1))
        self.time_offset = rebase_time - self.time_start + random_time

    def get_next_message_index(self):
        if self.message_index < self.message_count:
            i = self.message_index
            self.message_index += 1
            return i
        else: raise EndOfBagException("No more messages.")

    def retrieve_message_offsets(self):
        self.message_offsets = []
        for entry in self.bag._get_entries():
            e = (entry.chunk_pos, entry.offset)
            self.message_offsets.append(e)
        assert( len(self.message_offsets) == self.message_count )

    def close(self):
        self.bag.close()


class BagMultiplex():

    def __init__(self, input_bags):
        self.bags = input_bags
        self.get_first_message_from_all()

    def get_first_message_from_all(self):
        self._timestamps = [None] * len(self.bags)
        self._messages = [None] * len(self.bags)
        for bag_number, bag in enumerate(self.bags):
            first_message = bag.get_next_message()
            self.store_message(bag_number, first_message)

    def pull_message(self):
        bag_number = argmin(self._timestamps)
        bag = self.bags[bag_number]
        message = self._messages[bag_number]
        try:
            new_message = bag.get_next_message()
            self.store_message(bag_number, new_message)
        except EndOfBagException:
            del(self.bags[bag_number])
            del(self._messages[bag_number])
            del(self._timestamps[bag_number])
        return message, bag_number

    def store_message(self, bag_number, message):
        self._timestamps[bag_number] = message.timestamp
        self._messages[bag_number] = message


class rosbag_multiplexer():

    def __init__(self):
        self.parse_command_line()
        self.open_input_bags()
        self.open_output_bag()
        self.multiplex()

    def __del__(self):
        self.close_input_bags()
        self.close_output_bag()

    def multiplex(self):
        m = BagMultiplex(self.input_bags)
        while len(self.input_bags) > 0:
            message, bag_number = m.pull_message()
            print bag_number, message.topic, message.timestamp
            self.output_bag.write(message.topic, message.message, message.timestamp)

    def open_input_bags(self):
        print "Opening Input Bags ..."
        print "[[ This could take some time, have a coffe! ]]"
        self.input_bags = []
        for current_filename in self.input_filenames:
            print "Opening '%s' ..." % current_filename
            current_base_time = self.base_time
            current_bag = InputBag(current_filename, self.base_time)
            print "Bag starts at: %s" % current_bag.time_start
            self.input_bags.append(current_bag)
        print "Done!"

    def close_input_bags(self):
        for i in self.input_bags: i.close()

    def open_output_bag(self):
        print "Initializing Output Bag '%s' ..." % self.output_filename
        self.output_bag = Bag(self.output_filename, 'w')

    def close_output_bag(self):
        self.output_bag.close()

    def parse_command_line(self):
        current_time = time.time()
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', action='append', default=[], type=str, help="Input bag. A minumum number of 2 input bags is required. Usage: '-i bag_1.bag -i bag_2.bag'.")
        parser.add_argument('-o', action='store', default=None, type=str, help="Output bag")
        parser.add_argument('-t', action='store', default=current_time, type=str, help="Common start time.")
        args = parser.parse_args()
        if len(args.i) < 2: raise Exception("A minimum number of 2 input bags is required.")
        if args.o is None: args.o = '%s.bag' % current_time
        self.input_filenames = args.i
        self.output_filename = args.o
        self.base_time = rospy.Time().from_sec(float(args.t))
        print "== BASE_TIME  %s" % self.base_time
        print "== OUTPUT_BAG %s" % self.output_filename
        print "== INPUT_BAGS"
        for i in self.input_filenames: print "  - %s" % i

if __name__ == "__main__":
    c = rosbag_multiplexer()
    # try:
    # except Exception as e:
    #     print e
