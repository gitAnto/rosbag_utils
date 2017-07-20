# rosbag_utils

ROS catkin package containing some utilities for manipulating rosbags.

Copyright (c) 2016 
Antonio Coratelli
Antonio Petitti


## License

BSD 3-Clause. See `LICENSE` file.


## Scripts

### rosbag_multiplexer
```
    This script reads the content of an arbitrary number of rosbag files and
    creates a new bag that merges the contents of the input bags as these were
    playing together. Message timestamps are modified appropriately.

    Example:
        $ python rosbag_multiplexer.py -i bag_1.bag -i bag_2.bag -o multi.bag \
            -t 1000

        Will create a new bag 'multi.bag' with all the content from 'bag_1.bag'
        and 'bag_2.bag' starting at time 1000.
```

### rosbag_tf_remove_msg
```
    This script reads the content of a rosbag file (.bag) and creates a new
    rosbag file removing all messages in /tf topic that match chosen frame_id
    and child_frame_id.

    Example:
        $ python rosbag_tf_remove_msg.py -i input.bag -o output.bag \
            -f '/odom' -c '/base_link'

        Will create a new bag that DOESN'T broadcast a transform from '/odom'
        to '/base_link'.
```


### rosbag_decimate
```
    This script reads the content of a rosbag file (.bag) and creates a new
    rosbag file decimating the content of some topics.

    Example:
        $ python rosbag_decimate.py -i input.bag -o output.bag \
            -r 10 -t '/odom' -t '/camera/rgb/raw' -x 3

        Will decimate topics '/odom' and '/camera/rgb/raw' from 'input.bag'
        limiting the publish rate to 10 Hz. The new bag will be 'output.bag'.
        The messages in the first 3 seconds will not be limited.
```

### rosbag_odom_unslasher
```
    This script reads the content of a rosbag file (.bag) and creates a new
    rosbag file removing the trailing slashes in frame_id and child_frame_id
    contained in odometry topics.
    (Useful because new tf2 **doesn't accept** frame_ids with trailing slashes.)

    Example:
        $ python rosbag_odom_unslasher.py -i input.bag -o output.bag \
            -t '/robot_odometry' -f 'odom' -c 'base_link'

        Will replace all frame_ids '/odom' with 'odom' and all child_frame_ids
        '/base_link' with 'base_link' in topic '/robot_odometry'
```
