#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#
# INFO
#   legge il contenuto di una bag e ne crea una nuova decimando i messaggi
#   di alcuni topic.
#
# USO
#   rosbag-filter <input-file.bag>
#
# OUTPUT
#   il percorso del file di uscita e' "input-file_DEC.bag"
#
# CONFIGURAZIONE
# - topic_nod e' la lista dei topic da non decimare
# - topic_dec e' un dizionario che contiene come chiavi i topic da decimare, e 
#   come valori il tempo minimo (in secondi) fra la pubblicazione di un 
#   messaggio e il seguente nel dato topic
# - t_nodec e' il tempo (in secondi) che deve trascorrere dall'inizio della bag
#   prima di cominciare a decimare i topic in topic_dec
#
################################################################################

topics_nod = [
    '/odom',
    '/tf',
    '/camera/depth_registered/camera_info',
    '/camera/rgb/camera_info',
]

topics_dec = {
    '/camera/depth_registered/hw_registered/image_rect' : 0.2 ,
    '/camera/rgb/image_rect_color'                      : 0.2 ,
}
t_nodec = 5.0

################################################################################

import rosbag
import time
import sys
import os

import threading

# graphic info function
def show_info():
    print "\033c", "%0.1f %%" % (i*100.0/count)
    print 'I:', bag_i_path
    print 'O:', bag_o_path
    for x in topics_dec:
        print topic_dec_info[x], "%0.2f" % topic_dec_last[x], x
    if (i < count):
        threading.Timer(0.1, show_info).start()

# retrieve input file from args, calculate output file name
bag_i_path = sys.argv[1]
bag_o_path = os.path.splitext(bag_i_path)[0] + "_DEC.bag"

# open bags
bag_i = rosbag.Bag(bag_i_path, 'r')
bag_o = rosbag.Bag(bag_o_path, 'w')

# initialize internal variables
t_init = 0
topic_dec_last = dict()
topic_dec_info = dict();
for topic in topics_dec:
    topic_dec_info[topic] = ' '*40;
    topic_dec_last[topic] = 0;
i = 0
count = bag_i.get_message_count()

# start graphics async loop
show_info()

# loop every message in bag
for topic, msg, t in bag_i.read_messages(topics_nod + topics_dec.keys()):

    if t_init == 0:
        t_init = t.to_sec()

    # directly save topics that don't need decimation
    if not topic in topics_dec:
        bag_o.write(topic, msg, t)

	# decimate topics
    else:
        if (t.to_sec() - topic_dec_last[topic]) >= topics_dec[topic] or (t.to_sec() - t_init) < t_nodec:
            bag_o.write(topic, msg, t)
            topic_dec_last[topic] = t.to_sec()
            topic_dec_info[topic] = topic_dec_info[topic][1:]+u'▓'
        else:
            topic_dec_info[topic] = topic_dec_info[topic][1:]+u'░'

    i += 1

i = count

bag_i.close()
bag_o.close()

