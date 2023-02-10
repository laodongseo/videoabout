"""
# 分离SRT字幕
ffmpeg -i input_video.mp4 -c:s srt -an -vn -codec:s srt output_subtitles.srt

-i input_video.mp4：指定输入视频文件的路径
-c:s srt：指定字幕的格式为SRT
-an：禁止输出音频流
-vn：禁止输出视频流
-codec:s srt：指定字幕的编码格式为SRT
output_subtitles.srt：指定输出字幕文件的路径

# 添加SRT字幕到视频指定字体大小颜色和自动换行
ffmpeg -i input_video.mp4 -vf "ass=subtitles.srt:force_style='Fontsize=24,PrimaryColour=&Hffffff&,OutlineColour=&H000000&,BorderStyle=3,Alignment=2,WrapStyle=2'" -c:v copy -c:a copy -c:s copy output_video.mp4

-i input_video.mp4：指定输入视频文件的路径
-vf "ass=subtitles.srt:force_style='Fontsize=24,PrimaryColour=&Hffffff&,OutlineColour=&H000000&,BorderStyle=3,Alignment=2'"：指定字幕的格式为SRT，并设置字体的颜色、字体大小和显示位置
-c:v copy -c:a copy -c:s copy：指定保持视频、音频和字幕的编码格式不变
output_video.mp4：指定输出视频文件的路径
WrapStyle=2：指定自动换行显示字体

其中，Fontsize 指定字体大小，PrimaryColour 指定字体颜色，OutlineColour 指定字体轮廓颜色，BorderStyle 指定字体边框样式，Alignment 指定字体显示位置。您可以根据需要调整这些参数的值。

# 清除视频的字幕并且保留原声音
ffmpeg -i input_video.mp4 -map 0:v -map 0:a -c:v copy -c:a copy output_video.mp4

-i input_video.mp4：输入视频文件
-map 0:v：保留视频流（0 是输入视频文件的编号，v 表示视频流）
-map 0:a：保留音频流（0 是输入视频文件的编号，a 表示音频流）
-c:v copy：使用原有的视频编码器
-c:a copy：使用原有的音频编码器
output_video.mp4：输出视频文件

"""


			
# 你可以使用ffmpeg来替换视频SRT字幕中的关键词，只需要在终端输入以下命令即可实现，其中Name代表你要替换的关键词，value表示你要替换成的值。:
ffmpeg -i input.video -i input.srt -vf subtitles=input.srt:force_style='Name=value,Name=value' -c:v copy -c:a copy -c:s srt output.video

# 你可以用ffmpeg来为视频添加一层蒙版，只需要在终端输入以下命令即可，其中alpha_param表示蒙版的透明度，取值范围为0到1，数值越大蒙版越不透明。:
ffmpeg -i input.video -i input.png -filter_complex "overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:alpha=alpha_param" -c:v copy -c:a copy output.video

# 你可以使用moviepy来为视频添加一层蒙版，只需要在终端输入以下命令即可实现:
import moviepy.editor as mpe
video = mpe.VideoFileClip("input.video")
mask = mpe.VideoFileClip("input.png").set_opacity(alpha) # alpha为蒙版的透明度，取值范围为0到1
video = video.set_mask(mask)
video.write_videofile("output.video")

clip = clip.copy()
clip = clip.add_mask()
clip.mask.duration = clip.duration

# 你可以使用MoviePy来为视频添加一个图片覆盖，并使其从左侧平移到右侧。下面是Python代码实现的例子:
你可以使用MoviePy来为视频添加一个图片从左侧平移到右侧的效果。下面是Python代码实现的例子:
from moviepy.editor import *
video_clip = VideoFileClip("input.mp4")
image_clip = ImageClip('image.png')
video_with_image = CompositeVideoClip([video_clip, image_clip.set_pos((0, 0)).set_start(0).set_duration(video_clip.duration).set_end(video_clip.duration).set_pos(lambda t: (200*t, 0)).crossfadein(1)])
video_with_image.write_videofile("output.mp4")
"""

"""
# 可以使用OpenCV中的cv2.VideoCapture函数来提取视频的SRT字幕。下面是一段编写代码来实现这一功能的例子:
import cv2 
# 加载视频文件 
cap = cv2.VideoCapture('my_video.avi') 
# 初始化视频帧索引和时间戳 
frame_index = 0 
frame_time = 0 
# 初始化SMPTE时间码 
srt_timecode = '' 
# 打开字幕文件 
subtitle = open('subtitle.srt', 'w') 
# 读取视频帧 
while (cap.isOpened()): 
    ret, frame = cap.read() 
    # 检查帧是否存在 
    if not ret: 
       break 
    # 记录视频帧的索引和时间戳 
    frame_index += 1 
    frame_time = int(cap.get(cv2.CAP_PROP_POS_MSEC)) 
    # 将时间戳转换为SMPTE时间码 
    srt_timecode = str(datetime.timedelta(milliseconds=frame_time)) 
    # 写入字幕文件 
    subtitle.write(str(frame_index) + '\n') 
    subtitle.write(srt_timecode + ' --> ' + srt_timecode + '\n') 
    subtitle.write(str(frame) + '\n') 
subtitle.close() 
cap.release()
"""


python 提取音频中的字幕转为SRT文件

	本文介绍如何使用python提取音频中的字幕并转换为SRT文件：

	1.安装SpeechRecognition库：

	要提取音频中的字幕，首先要安装SpeechRecognition库。它是Python的一个第三方库，用于识别音频中的文字。可以使用以下命令进行安装：

	pip install SpeechRecognition

	2.安装PyAudio库：

	为了使用SpeechRecognition库，还需要安装PyAudio库。PyAudio库用于捕捉音频输入，使SpeechRecognition库能够检测音频中的文字。可以使用以下命令进行安装：

	pip install PyAudio

	3.安装FFmpeg：

	如果要提取的音频文件不是WAV格式，那么还需要安装FFmpeg。FFmpeg可以将其他格式的音频文件转换为WAV格式，以便SpeechRecognition库能够识别。

	4.获取音频文件：

	首先，要在python程序中获取音频文件，可以使用以下命令获取：

	audio_file = open("filename.wav", "rb")

	5.使用SpeechRecognition库提取音频中的字幕：

	现在，可以使用以下代码提取音频中的字幕：

	import speech_recognition as sr

	r = sr.Recognizer()

	with sr.AudioFile(audio_file) as source:
	    audio = r.record(source)

	text = r.recognize_google(audio)

	6.将字幕转换为SRT格式：

	现在，可以使用以下代码将字幕转换为SRT格式：

	srt_file = open("filename.srt", "w")

	srt_file.write(text)

	srt_file.close()

	完成上述步骤后，即可提取音频中的字幕并将其转换为SRT文件。


python在视频中导入SRT字幕，请编写代码

	```
	# 导入需要的库
	import moviepy.editor as mp

	# 读取视频
	video = mp.VideoFileClip("my_video.mp4")

	# 读取srt字幕
	subs = mp.Subclip("my_subtitle.srt")

	# 将srt字幕添加到视频中
	video_with_subs = mp.CompositeVideoClip([video, subs.set_pos(('center', 'bottom'))])

	# 保存视频
	video_with_subs.write_videofile("my_video_with_subs.mp4")
	```

	```python
		import os
		from moviepy.editor import *

		# 导入视频
		video = VideoFileClip('video.mp4')

		# 导入字幕
		sub = os.path.join('subtitle.srt')

		# 设置字幕颜色、字体和字体大小
		subclip = TextClip(sub, color='white', font='Arial', fontsize=20)

		# 合并视频和字幕
		final = CompositeVideoClip([video, subclip])

		# 保存视频
		final.write_videofile('final.mp4')
		```

python提取视频中的SRT字幕，请编写代码

	```python
	from moviepy.editor import *

	video_path = "./video.mp4"

	video = VideoFileClip(video_path)

	# 将视频中的字幕提取为srt格式
	video.subclip().write_srt("./video.srt")
	``


用ffempeg提取视频的字幕

1.使用ffmpeg -i <video> 命令查看视频的流信息，以确定视频中是否包含字幕。

2.如果视频中包含字幕，使用ffmpeg -i <video> -map 0:s:0 <subtitle> 命令提取字幕，其中，s:0 代表字幕的索引，<subtitle> 代表提取的字幕文件。

	cmd = f' ffmpeg -i {infile} -map 0:s:0 {outfile}' 
	subprocess.call(cmd, shell=True)

3.如果视频中没有字幕，则可以使用ffmpeg -i <video> -vf subtitles=<subtitle> <output> 命令将字幕文件嵌入

ffmpeg -i input_video.mp4 -i output_subtitle.srt -map 0 -map 1 -c:v copy -c:a copy -c:s mov_text output_video_with_subtitle.mp4


"""
