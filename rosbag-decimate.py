#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''rosbag-decimate
    
    This script reads the content of a rosbag file (.bag) and creates a new
    rosbag file decimating the content of some topics.
    
    Example:
        $ python rosbag-decimate.py -i input.bag -o output.bag \
            -r 10 -t '/odom' -t '/camera/rgb/raw' -x 3
        
        Will decimate topics '/odom' and '/camera/rgb/raw' from 'input.bag'
        limiting the publish rate to 10 Hz. The new bag will be 'output.bag'.
        The messages in the first 3 seconds will not be limited.
    
    Options:
        -i PATH  : path to the input rosbag (mandatory)
        -o PATH  : path to the output rosbag (mandatory)
        -r NUM   : maximum rate of the selected topics (default 10) [Hz]
        -x NUM   : don't limit messages in the first NUM seconds (default 5)
        -t TOPIC : topic that should be limited (multiple allowed)
    
'''

import rosbag
import time
import sys
import os
import argparse
import threading


class rosbag_decimate:

    def __init__(self):
        self.REFRESH_INTERVAL = 1
        
        self._parse_cl()
        self._show_info()
        self._decimate()


    def _parse_cl(self):
        """Parse command line arguments.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', action='store', type=str)
        parser.add_argument('-o', action='store', type=str)
        parser.add_argument('-r', action='store', type=float, default=10.0)
        parser.add_argument('-x', action='store', type=float, default=5.0)
        parser.add_argument('-t', action='append', type=str)
        results = parser.parse_args()
        
        self.__i       = -1
        self.__count   = 1
        self.__file_i  = results.i
        self.__file_o  = results.o
        self.__topics  = results.t
        self.__rate    = results.r
        self.__exclude = results.x


    def _show_info(self):
        """Shows the processing status in the terminal.
        """
        if (self.__i == -1):
            print 'Input            : ', self.__file_i
            print 'Output           : ', self.__file_o
            for tp in self.__topics: print 'Decimate topic   : ', tp
            print 'Maximum Rate     : ', self.__rate, 'Hz'
            print 'Do not limit for : ', self.__exclude, 'seconds'
            print "Loading bag file... (This could take a while. Time for a coffe?)"
            self.__i = 0
        elif (self.__i > 0):
            sys.stdout.write("%6.1f %% \r" % (self.__i*100.0/self.__count))
            sys.stdout.flush()
            
        if (self.__i < self.__count):
            threading.Timer(self.REFRESH_INTERVAL, self._show_info).start()
        else:
            print


    def _decimate(self):
        # open bags
        bag_i = rosbag.Bag(self.__file_i, 'r')
        bag_o = rosbag.Bag(self.__file_o, 'w')

        self.__count  = bag_i.get_message_count()
        self.__t_init = bag_i.get_start_time()
        self.__t_last = dict()
        for topic in self.__topics:
            self.__t_last[topic] = self.__t_init

        # loop every message in bag
        for topic, msg, t in bag_i.read_messages():
            
            # decimate topics that need decimation
            if topic in self.__topics:
                if (t.to_sec() - self.__t_last[topic]) >= self.__rate**(-1) \
                or (t.to_sec() - self.__t_init) < self.__exclude:
                    bag_o.write(topic, msg, t)
                    self.__t_last[topic] = t.to_sec()
            
            # directly save topics that don't need decimation
            else:
                bag_o.write(topic, msg, t)

            self.__i += 1
        
        self.__i = self.__count
        
        bag_i.close()
        bag_o.close()


if __name__ == "__main__":

    c = rosbag_decimate()

