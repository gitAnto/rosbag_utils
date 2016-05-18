#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''rosbag_odom_unslasher
    
    This script reads the content of a rosbag file (.bag) and creates a new
    rosbag file removing the trailing slashes in frame_id and child_frame_id
    contained in odometry topics.
    (Useful because new tf2 **do not accept** frame_ids with trailing slashes.)
    
    Example:
        $ python rosbag_odom_unslasher.py -i input.bag -o output.bag \\
            -t '/robot_odometry' -f 'odom' -c 'base_link'
        
        Will replace all frame_ids '/odom' with 'odom' and all child_frame_ids
        '/base_link' with 'base_link' in topic '/robot_odometry'
    
    Options:
        -i PATH  : path to the input rosbag (mandatory)
        -o PATH  : path to the output rosbag (mandatory)
        -t TOPIC : odometry topic
        -f FRAME : frame_id (without slash)
        -c FRAME : child_frame_id (without slash)
    
    Author:
        Antonio Coratelli <antoniocoratelli@gmail.com>
    
    License:
        (BSD License)

        Redistribution and use in source and binary forms, with or without
        modification, are permitted provided that the following conditions
        are met:

        * Redistributions of source code must retain the above copyright
          notice, this list of conditions and the following disclaimer.
        * Redistributions in binary form must reproduce the above
          copyright notice, this list of conditions and the following
          disclaimer in the documentation and/or other materials provided
          the distribution.
        * The name of the author may not be used to endorse or promote
          products derived from this software without specific prior written
          permission.

        THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
        "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
        LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
        FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
        COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
        INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
        BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
        LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
        CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
        LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
        ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
        POSSIBILITY OF SUCH DAMAGE.
        
'''

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
        parser.add_argument('-t', action='store', type=str, default='/odom')
        parser.add_argument('-f', action='store', type=str, default='odom')
        parser.add_argument('-c', action='store', type=str, default='base_link')
        parser.add_argument('-h', action='store_true', default=False)
        
        results = parser.parse_args()
        
        if (results.h) == True:
            print __doc__
            sys.exit(0)
        
        self.__i       = -1
        self.__count   =  1
        self.__file_i         = results.i
        self.__file_o         = results.o
        self.__topic          = results.t
        self.__frame_id       = results.f
        self.__child_frame_id = results.c


    def _show_info(self):
        """Shows the processing status in the terminal.
        """
        if (self.__i == -1):
            print 'Input            : ', self.__file_i
            print 'Output           : ', self.__file_o
            print 'Topic            : ', self.__topic
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
            
            if topic == self.__topic:
                
                if (msg.header.frame_id == '/'+self.__frame_id):
                    msg.header.frame_id =      self.__frame_id
                
                if (msg.child_frame_id == '/'+self.__child_frame_id):
                    msg.child_frame_id =      self.__child_frame_id
                
            bag_o.write(topic, msg, t)
            
            self.__i += 1
        
        self.__i = self.__count
        
        bag_i.close()
        bag_o.close()


if __name__ == "__main__":

    c = rosbag_odom_unslasher()

