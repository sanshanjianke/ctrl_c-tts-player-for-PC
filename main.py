# -*- coding: utf-8 -*-
import os
import time
import threading
import random
import asyncio

import pygame
import pyperclip
import edge_tts

play_queue=[]

# 获取并保存音频文件
async def get_song(text,output):
    tts = edge_tts.Communicate(text=text,voice="zh-CN-YunyangNeural",rate="+50%") # rate是语速，这里我加快了0.5倍
    await tts.save(output)

class ThreadingPrc(threading.Thread):
    def run(self):
        global play_queue
        pygame.mixer.init()
        while True:
            time.sleep(0.05)
            if not play_queue:  # 如果播放队列是空的就继续循环
                continue
            if os.path.exists(os.getcwd() + "\\" + str(play_queue[0]) + "audio.mp3"): # 如果播放队列里有，文件也下载好了就继续
                while True:
                    time.sleep(0.05)
                    if not pygame.mixer.music.get_busy(): # 如果正在播放，就先等他播放完
                        try:
                            pygame.mixer.music.load(os.getcwd() + "\\" + str(play_queue[0]) + "audio.mp3") # 如果获取失败也是重新
                        except BaseException:
                            continue
                        else:
                            pygame.mixer.music.play() # 播放音乐
                            play_queue.pop(0) # 播了之后，移出队列
                            break




def run_init_speaker():
    global play_queue
    set_text = pyperclip.paste()
    set_text = set_text.replace("\r", "") # 删除换行符和制表符，不然读智障pdf文件的时候，总会每一行末尾停顿一下。
    set_text = set_text.replace("\n", "")
    set_text = set_text.replace("\t", "")
    set_text_u = []
    # 将其切片成每份300个字的数组，或者按照句号分割
    if set_text.find("。") != -1:
        while set_text.find("。") != -1:
            set_text_u.append(set_text[0:set_text.find("。") + 1])
            set_text = set_text[set_text.find("。") + 1:len(set_text)]
        set_text_u.append(set_text[0:len(set_text)])
    elif len(set_text) > 300:
        while len(set_text) != 0:
            set_text_u.append(set_text[0:300])
            set_text = set_text[300:len(set_text)]
    else:
        set_text_u.append(set_text)

    # 把每一句话分别生成一份音频文件
    for set_next in set_text_u:
        pr = random.randint(10000000, 99999999)
        # 随机数字id，足够大，所以大概率不会发生冲突。
        if set_next != '':
            while True:
                try:
                    asyncio.run(get_song(set_next,os.getcwd() + "\\" + str(pr) + "audio.mp3"))
                except BaseException:
                    continue
                else:
                    play_queue.append(pr) # 把文件id塞进待播放的列表中
                    break
        else:
            break

# 启动一个线程监听播放队列，如果播放队列存在音频文件的话，就按顺序播放
new_thread = ThreadingPrc()
new_thread.start()

# 从剪切板循环判断，是否存在更改的现象，如果存在就调用speaker的功能
paste_string = pyperclip.paste()
while True:
    time.sleep(0.05)
    if paste_string != pyperclip.paste():
        run_init_speaker()
        paste_string = pyperclip.paste()
