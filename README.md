# rosbag_utils

ROS catkin package containing some utilities for manipulating rosbags.

Copyright (c) 2016, Antonio Coratelli.


## License

BSD 3-Clause. See `LICENSE` file.


## Scripts

### rosbag_decimate
```
    This script reads the content of a rosbag file (.bag) and creates a new
    rosbag file decimating the content of some topics.
    
    Example:
        $ ./rosbag_decimate.py -i input.bag -o output.bag \
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
