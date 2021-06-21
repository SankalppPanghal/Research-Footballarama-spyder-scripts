# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 09:54:55 2021

AUTOMATE - FFMPEG COMMAND

@author: panghals
"""

import subprocess
import os

def find_start_no(loc):
    files = sorted([int(x.split('.')[0].split('_')[1]) for x in os.listdir(loc) if 'png' in x])
    return (files[0], len(files))


#main_loc = "D:\\Sequence Data Feb\\Seq 5 shelly 020"
main_loc = "D:\\Sequence Data Feb\\seq 1 daly boh vs dundalk"
#size = "1080"
for no in range(10,11):

    loc = main_loc + "\\{}".format("8k_yolo_detect_downsample_1080_frames")
    start_no, total = find_start_no(loc)

    command = "ffmpeg -start_number {} -i \"{}\\frame_%d.png\" -r 25 -c:v libx264 -b:v 4096k -pix_fmt yuv420p \"{}\"".format(start_no, loc, main_loc +"\\{}.mp4".format("8k_detect3"))
    print(command)

    p1 = subprocess.run(command, shell = True, capture_output=True, text = True)
    print(p1.returncode)
    print(p1.stdout)

