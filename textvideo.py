# -*- coding: utf-8 -*-
# author: kuangdd
# date: 2020/6/20
"""
utils

视频编码参考：
CV_FOURCC('P','I','M','1') = MPEG-1 codec
CV_FOURCC('M','J','P','G') = motion-jpeg codec
CV_FOURCC('M', 'P', '4', '2') = MPEG-4.2 codec
CV_FOURCC('D', 'I', 'V', '3') = MPEG-4.3 codec
CV_FOURCC('D', 'I', 'V', 'X') = MPEG-4 codec
CV_FOURCC('U', '2', '6', '3') = H263 codec
CV_FOURCC('I', '2', '6', '3') = H263I codec
CV_FOURCC('F', 'L', 'V', '1') = FLV1 codec
"""
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(Path(__name__).stem)

import random
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.editor import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

from tqdm import tqdm
import os
import cv2
import pydub

_length = 720
_height = 1080
_size = (_length, _height)
_fps = 30

_image_ext = '.png'
_image_format = 'PNG'
_image_mode = 'RGB'


_colors_total = ['aqua', 'black', 'blue', 'fuchsia', 'gray', 'green', 'lime', 'maroon', 'navy', 'olive', 'purple', 'red', 'silver', 'teal', 'white', 'yellow']
_colors_oov = ['black', 'gray', 'navy', 'silver', 'white']
_colors = ['aqua', 'blue', 'fuchsia', 'green', 'lime', 'maroon', 'olive', 'purple', 'red', 'teal', 'yellow']



class TextVideoGenerator(object):
    def __init__(self):
        pass


def generate_image_pure_color(outpath, color='black'):
    """生成纯色背景图片"""
    image = Image.new(_image_mode, _size, color)
    ImageDraw.Draw(im=image)
    image.save(outpath, _image_format)
    image.close()


def generate_images_twinkle(text="中文", backgound_path='', font_path='', out_prefix='', location=(50, 500),
                        colors=('black', 'red', 'white'), font_size=50, n_frame=50):
    """把文字转为图片，闪烁文字"""
    if isinstance(backgound_path, (str, Path)):
        img_bg = cv2.imdecode(np.fromfile(str(backgound_path), dtype=np.uint8), -1)

    x, y = location
    for f in range(1, n_frame + 1):
        if isinstance(backgound_path, list):
            img_bg = cv2.imdecode(np.fromfile(str(backgound_path[f - 1]), dtype=np.uint8), -1)
        cv2img = cv2.cvtColor(img_bg, cv2.COLOR_BGR2RGB)  # cv2和PIL中颜色的hex码的储存顺序不同
        pilimg = Image.fromarray(cv2img)
        draw = ImageDraw.Draw(pilimg)

        loc = (x + random.randint(-3, +3), y + random.randint(-3, +3))
        font = ImageFont.truetype(font_path, font_size + random.randint(1, 2), encoding="utf-8")
        color = np.random.choice(colors)
        # 参数1：打印坐标，参数2：文本，参数3：字体颜色，参数4：字体
        draw.text(loc, text, color, font=font)

        cv2charimg = cv2.cvtColor(np.array(pilimg), cv2.COLOR_RGB2BGR)
        outpath = '{}_{:04d}.jpg'.format(out_prefix, f)
        cv2.imencode('.jpg', cv2charimg)[1].tofile(outpath)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def generate_images_zoom(text="中文", backgound_path='', font_path='', out_prefix='', location=(50, 500),
                        colors=('black', 'red', 'white'), font_size=50, n_frame=50):
    """把文字转为图片，文字缩放变大"""
    if isinstance(backgound_path, (str, Path)):
        img_bg = cv2.imdecode(np.fromfile(str(backgound_path), dtype=np.uint8), -1)

    x, y = location
    for num in range(1, n_frame + 1):
        if isinstance(backgound_path, list):
            img_bg = cv2.imdecode(np.fromfile(str(backgound_path[f - 1]), dtype=np.uint8), -1)
        cv2img = cv2.cvtColor(img_bg, cv2.COLOR_BGR2RGB)  # cv2和PIL中颜色的hex码的储存顺序不同
        pilimg = Image.fromarray(cv2img)
        draw = ImageDraw.Draw(pilimg)

        loc = (x, y)
        nz = 10
        fs = min(font_size, int(num *  font_size / nz))
        font = ImageFont.truetype(font_path, fs, encoding="utf-8")
        color = np.random.choice(colors)
        # 参数1：打印坐标，参数2：文本，参数3：字体颜色，参数4：字体
        draw.text(loc, text, color, font=font)

        cv2charimg = cv2.cvtColor(np.array(pilimg), cv2.COLOR_RGB2BGR)
        outpath = '{}_{:04d}.jpg'.format(out_prefix, num)
        cv2.imencode('.jpg', cv2charimg)[1].tofile(outpath)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def images_to_video(inpaths, outpath):
    """图片合成视频"""
    fps = _fps  # 28
    size = _size
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # 不同视频编码对应不同视频格式（例：'I','4','2','0' 对应avi格式）
    videowriter = cv2.VideoWriter(str(outpath), fourcc, fps, size)

    for fpath in inpaths:
        if os.path.exists(fpath):
            img = cv2.imread(str(fpath))
            cv2.waitKey(1)
            videowriter.write(img)
        else:
            print(fpath)
    videowriter.release()


def merge_video_audio(video_path, audio_path, outpath):
    """视频和音频合并"""
    audioclip = AudioFileClip(str(audio_path))
    videoclip = VideoFileClip(str(video_path))
    videoclip2 = videoclip.set_audio(audioclip)
    video = CompositeVideoClip([videoclip2])
    video.write_videofile(str(outpath), codec='mpeg4', fps=_fps)


def synthesize_audio(text, outpath):
    """合成音频"""
    url = "http://10.32.72.44:9090/tts"
    result = requests.post(url=url, json=dict(text=text, timbre="1", pitch="1", speed="1", quality="-1"))
    result = result.content
    if not isinstance(result, dict):
        with open(outpath, 'wb') as f:
            f.write(result)


def combine_audio(inpaths, outpath):
    """合并音频"""
    out = pydub.AudioSegment.empty()
    for fpath in inpaths:
        aud = pydub.AudioSegment.from_file(fpath)
        out = out + aud
    out.export(outpath, format='mp3')


def video_to_images(inpath, out_prefix, n_frame=1000):
    mp4 = cv2.VideoCapture(str(inpath))  # 读取视频
    is_opened = mp4.isOpened()  # 判断是否打开
    fps = mp4.get(cv2.CAP_PROP_FPS)  # 获取视频的帧率
    widght = mp4.get(cv2.CAP_PROP_FRAME_WIDTH)  # 获取视频的宽度
    height = mp4.get(cv2.CAP_PROP_FRAME_HEIGHT)  # 获取视频的高度

    i = 0
    while is_opened:
        if i >= n_frame:
            break
        i += 1
        (flag, frame) = mp4.read()  # 读取图片
        outpath = '{}_{:04d}.jpg'.format(out_prefix, i)
        if flag == True:
            cv2.imwrite(outpath, frame, [cv2.IMWRITE_JPEG_QUALITY])  # 保存图片


def run_example():
    """样例"""
    rootdir = Path('../data')

    font_path = rootdir / 'font/HYZiYanGuoDongTiW.ttf'

    workdir = rootdir / 'example'
    workdir.mkdir(exist_ok=True, parents=True)

    background_path = workdir / 'background.png'
    generate_image_pure_color(outpath=background_path, color='black')
    # background_path = rootdir / 'duduswim.mp4'
    # background_dir = workdir / 'background'
    # background_dir.mkdir(exist_ok=True, parents=True)
    # out_prefix = str(background_dir) + '/background'
    # video_to_images(inpath=background_path, out_prefix=out_prefix, n_frame=20 * _fps)

    # <text=嘟嘟#pinyin=du3 du2#>
    texts = '大家好，我叫嘟嘟，我，是世界上，最聪明，最可爱，最调皮的，嘟嘟'.split('，')
    texts_ssml = '大家好，我叫<text=嘟嘟#pinyin=du3 du2#>，我，是世界上，最聪明，最可爱，最调皮的，<text=嘟嘟#pinyin=du3 du2#speed=0.8#>'.split('，')

    audio_dir = workdir / 'audio'
    audio_dir.mkdir(exist_ok=True, parents=True)

    for num, text in enumerate(texts_ssml, 1):
        outpath = audio_dir / 'example_{:04d}.mp3'.format(num)
        synthesize_audio(text, outpath=outpath)

    # background_lst = list(sorted(background_dir.glob('*.jpg')))
    cnt = 0
    image_dir = workdir / 'image'
    image_dir.mkdir(exist_ok=True, parents=True)
    for num, text in enumerate(tqdm(texts), 1):
        size_max = _length // (len(text) + 2)
        size_min = _length // (2 * len(text) + 2)
        font_size = random.randint(size_min, size_max)

        x_max = _length - font_size * len(text) - font_size
        x_min = font_size - 1
        x = random.randint(x_min, x_max)

        y_max = _height - font_size * 2#_height - font_size
        y_min = _height // 2#font_size
        y = random.randint(y_min, y_max)

        colors = np.random.choice(_colors, 1)

        out_prefix = str(image_dir) + '/example_{:04d}'.format(num)

        audio_path = audio_dir / 'example_{:04d}.mp3'.format(num)
        dur_s = pydub.AudioSegment.from_file(audio_path).duration_seconds

        n_frame = int(dur_s * _fps)
        # background_lst[cnt: cnt + n_frame]
        generate_images_zoom(text, backgound_path=background_path, font_path=str(font_path), out_prefix=out_prefix,
                            location=(x, y), colors=colors, font_size=font_size, n_frame=n_frame)
        cnt += n_frame

    inpaths = list(sorted(image_dir.glob('*.jpg')))
    video_path = workdir / 'example_silence.mp4'
    images_to_video(inpaths=inpaths, outpath=str(video_path))

    inpaths = list(sorted(audio_dir.glob('*.mp3')))
    audio_path = workdir / 'example.mp3'

    combine_audio(inpaths=inpaths, outpath=audio_path)

    outpath = workdir / 'example.mp4'
    merge_video_audio(video_path=video_path, audio_path=audio_path, outpath=outpath)


if __name__ == "__main__":
    print(__file__)
    run_example()
