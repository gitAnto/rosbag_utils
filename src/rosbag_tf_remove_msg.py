#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rosbag
import time
import sys
import os
import argparse
import threading


class rosbag_odom_unslasher:

    def __init__(self):
        self.REFRESH_INTERVAL = 1

        self._parse_cl()
        self._show_info()
        self._parse_bag()


    def _parse_cl(self):
        """Parse command line arguments.
        """
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('-i', action='store', type=str)
        parser.add_argument('-o', action='store', type=str)
        parser.add_argument('-f', action='store', type=str)
        parser.add_argument('-c', action='store', type=str)

        results = parser.parse_args()

        self.__i       = -1
        self.__count   =  1
        self.__file_i         = results.i
        self.__file_o         = results.o
        self.__frame_id       = results.f
        self.__child_frame_id = results.c


    def _show_info(self):
        """Shows the processing status in the terminal.
        """
        if (self.__i == -1):
            print 'Input            : ', self.__file_i
            print 'Output           : ', self.__file_o
            print 'Frame ID         : ', self.__frame_id
            print 'Child Frame ID   : ', self.__child_frame_id
            print "Loading bag file... (This could take a while. Time for a coffe?)"
            self.__i = 0

        elif (self.__i > 0):
            sys.stdout.write("%6.1f %% \r" % (self.__i*100.0/self.__count))
            sys.stdout.flush()

        if (self.__i < self.__count):
            threading.Timer(self.REFRESH_INTERVAL, self._show_info).start()
        else:
            print


    def _parse_bag(self):
        # open bags
        bag_i = rosbag.Bag(self.__file_i, 'r')
        bag_o = rosbag.Bag(self.__file_o, 'w')

        self.__count  = bag_i.get_message_count()

        # loop every message in bag
        for topic, msg, t in bag_i.read_messages():
            if topic == '/tf':
                new_transforms = []
                for i in msg.transforms:
                    if  i.header.frame_id == self.__frame_id \
                    and i.child_frame_id  == self.__child_frame_id:
                        pass
                    else:
                        new_transforms.append(i)
                msg.transforms = new_transforms
            bag_o.write(topic, msg, t)

            self.__i += 1

        self.__i = self.__count

        bag_i.close()
        bag_o.close()


if __name__ == "__main__":

    c = rosbag_odom_unslasher()
