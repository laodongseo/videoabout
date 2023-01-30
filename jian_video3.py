# coding:utf8
"""
一：
 1）获取原视频的尺寸、帧数、时长
 2）根据尺寸、帧数、时长随机生成几个背景图
 3）背景图组合成背景视频
二：
 1）剪切中间的画面视频
 2）调整画面视频的亮度
 3）获取画面视频的尺寸、帧数、时长
 4）根据尺寸、帧数、时长随机生成几个词云图
 5）词云图组合成词云视频
 6）词语视频添加一层空镜头
三：
 1）词云视频和画面视频画中画组合->视频1
 2）背景视频和视频1画中画组合->视频2
四：
 视频2添加干扰音频

"""
from PIL import Image
from  moviepy.editor import *
import cv2,shutil,os
from PIL import Image, ImageDraw, ImageFont
import random,time,re
from moviepy.config import change_settings
import pandas as pd
import threading,queue
import numpy as np
import wordcloud
import moviepy.editor as mpe
import traceback 
import time

# 前后拼接多个音频
def concatenate_audio_moviepy(audio_paths, output_path):
	clips = [AudioFileClip(c) for c in audio_paths]
	final_clip = concatenate_audioclips(clips)
	final_clip.write_audiofile(output_path)



change_settings({"IMAGEMAGICK_BINARY": r"D:/install/ImageMagick-7.1.0-Q16-HDRI/magick.exe"})
audio_file = './audio/34-Rain-10min.mp3'
# 选择文字字体和大小,加载字体才能支持中文
setFont = ImageFont.truetype(font='C:/windows/fonts/STZHONGS.TTF', size=75)

# 截取某个时间范围内的视频
def cut_time(video_path,video_cut_path, start_time='',end_time=''):
	video_base = VideoFileClip(video_path)
	if not isinstance(start_time,int) or not isinstance(end_time,int):
		return video_base ,video_path
	video_base = video_base.subclip(start_time,end_time)
	video_base.write_videofile(video_cut_path)
	return video_base ,video_cut_path


# 生成多个背景图片帧,每个图片写时间戳
def gen_rand_bgimgs(save_path,img_size,img_num,location=(0,0),setFont=setFont,fontColor='#FF1B23'):
	bg_imgs = []
	for i in range(img_num):
		num1,num2,num3 = random.randint(1,255),random.randint(1,255),random.randint(1,255)
		# 生成大小为400x400RGBA是四通道图像，RGB表示R，G，B三通道，A表示Alpha的色彩空間
		image = Image.new(mode='RGB', size=img_size, color=(num1, num2, num3))
		# ImageDraw.Draw 新建绘画图像
		draw = ImageDraw.Draw(im=image)
		text = f'{time.time()}'
		draw.text(location, text,font=setFont,fill=fontColor, direction=None)
		os.mkdir(save_path) if not os.path.exists(save_path) else 1
		file_img = os.path.join(save_path,f'{i}.png')
		image.save(file_img)
		bg_imgs.append(file_img)
	return bg_imgs


# 生成多个随机词云图片;和crop裁剪视频尺寸一致
def gen_rand_ciyunimgs(save_path,img_size,img_num):
	ciyun_imgs = []
	for i in range(img_num):
		values = random.randint(1,255) ,random.randint(1,255) ,random.randint(1,255)
		img  = Image.new(mode = "RGB", size = img_size, color = values )
		mask = np.array(img) # 图片转换为数组
		texts = random.sample('zyxwvutsrqponmlkjihgfedcba!@#$%^&*()',10)
		text = ' '.join(texts) + str(time.time())
		width,height = img_size
		wc = wordcloud.WordCloud(font_path=r"C:\Windows\Fonts\simsunb.ttf",width = width,height = height,
			mask=mask,background_color='white',max_words=1000,stopwords=['的'])
		wc.generate(text) # 加载词云文本
		os.mkdir(save_path) if not os.path.exists(save_path) else 1
		outimg = os.path.join(save_path,f'{i}.png')
		wc.to_file(outimg)
		ciyun_imgs.append(outimg)
	return ciyun_imgs


# 给视频覆盖1个图片
def add_cover_img(cover_img,video_path,video_out_path):
	video = VideoFileClip(video_path)
	# 图片logo
	img_obj = Image.open(cover_img)
	logo = (ImageClip(cover_img).set_duration(video.duration) # 水印持续时间
			.resize(height=img_obj.height,width=img_obj.width) # 水印宽高，会等比缩放
			.margin(right=0, top=0,opacity=0)  # 水印边距和透明度
			.set_pos(("center", "bottom")))  # 水印的位置

	final = CompositeVideoClip([video, logo])
	# mp4文件默认用libx264编码， 比特率单位bps
	final.write_videofile(video_out_path, codec="libx264", bitrate="10000000")


# 图片合成视频
def imgs_to_video(my_imgs,output_video_path, time_long,each_image_duration = 4):
	"""
	time_long:生成的视频时长
	each_image_duration:每个图片站展现时间
	"""
	cv2_imgs=[]
	[cv2_imgs.append(cv2.imread(i)) for i in my_imgs]
	height, width, layers = cv2_imgs[0].shape
	size = (width,height)
	out = cv2.VideoWriter(output_video_path,cv2.VideoWriter_fourcc(*'mp4v'), 1.0, size) #DIVX avi
	 # 所需图片数
	img_num = int(time_long / each_image_duration) + 1
	img_num = img_num if img_num < len(my_imgs) else len(my_imgs)
	img_objs = random.sample(cv2_imgs,img_num)
	for img_obj in img_objs:
		image=cv2.resize(img_obj,size)
		for _ in range(each_image_duration):
			out.write(image)
	out.release()
	# 裁剪目标时长
	VideoFileClip(output_video_path).subclip(0,int(time_long)).write_videofile(output_video_path) #不int8.31会变成9



# 视频区域裁剪
def video_crop(position1, position2, video_source ,video_crop_path):
	# 剔除上下黑边选取影响范围
	video =  VideoFileClip(video_source)
	video_need = (video.fx(vfx.crop,position1[0],position1[1],position2[0],position2[1]))
	# video_heibai_light = video_need.fx(vfx.colorx, random.uniform(0.90000,1.11111)) # 调亮
	# video_need = video_need.fx(vfx.blackwhite) # 黑白处理
	# video_need_heibai = video_heibai_light.fx(vfx.invert_colors) # 反色处理
	video_need.write_videofile(video_crop_path)
	return video_crop_path


# 改变视频每一帧的亮度
def handle_frame(image_frame,add_value):
	image_frame_result = image_frame * add_value
	# 如果颜色值超过255，直接设置为255
	image_frame_result[image_frame_result > 255] = 255
	return image_frame_result


def increase_video_brightness(inputvideo_path ,outvideo_path):
	video = VideoFileClip(inputvideo_path)
	add_value = random.uniform(1.0500001,1.090000001)
	result = video.fl_image(handle_frame,add_value)
	result.write_videofile(outvideo_path)


# 叠加两段视频(画中画)
def composite_videos(video_down, video_up ,outputvideo):
	bg_video_clip = VideoFileClip(video_down)
	video_crop_clip = VideoFileClip(video_up)
	width1, height1 = bg_video_clip.w, bg_video_clip.h
	width2, height2 = video_crop_clip.w, video_crop_clip.h

	# 视频缩放
	video_up_set = video_crop_clip.resize((width1, width1 / width2 * height2))
	# 叠加视频
	composite_video_clip = CompositeVideoClip([bg_video_clip, video_up_set.set_pos("center")])
	composite_video_clip.write_videofile(outputvideo)

	return composite_video_clip



# 生成图片标题
def logopic_text(text,logofile,img_size,location=(15,10),fontColor='#FF0000'):
	num1,num2,num3 = 255,255,0
	image = Image.new(mode='RGB', size=img_size, color=(num1, num2, num3))
	# ImageDraw.Draw 新建绘画图像
	draw = ImageDraw.Draw(im=image)
	draw.text(location, text,font=setFont,fill=fontColor, direction=None)
	image.save(logofile)
	return logofile


# 给视频加logo图片
def add_logo_img(logo_img,video_path,video_logo_path):
	video = VideoFileClip(video_path)
	# 图片logo
	img_obj = Image.open(logo_img)
	logo = (ImageClip(logo_img).set_duration(video.duration) # 水印持续时间
			.resize(height=img_obj.height) # 水印的高度，会等比缩放
			.margin(left = 2,right=1, top=1,opacity=1)  # 水印边距和透明度
			.set_pos(("center", "top")))  # 水印的位置
	final = CompositeVideoClip([video, logo])
	# mp4文件默认用libx264编码， 比特率单位bps
	final.write_videofile(video_logo_path, codec="libx264", bitrate="10000000")


# 添加多个随机文字水印
def add_shuiyin_text(logo_text,video_path,video_logo_path):
	video = VideoFileClip(video_path)
	times = video.duration
	n = int(times * 0.8)  # 一共出现n次
	times_list = [i * (times / n) for i in range(n + 1)]
	logos = []
	for i in range(n):
		logo = (TextClip((logo_text), fontsize=45, font='Simhei', color='red')
				.set_start(times_list[i]).set_end(times_list[i + 1])  # 水印持续时间
				.set_pos((random.randint(0, video.w), random.randint(0, video.h))))  # 水印的位置
		logos.append(logo)
	final = CompositeVideoClip([video, *logos])
	# mp4文件默认用libx264编码， 比特率单位bps
	final.write_videofile(video_logo_path, codec="libx264", bitrate="10000000")


# 视频添加背景音频
def add_bgaudio(input_video,audio_file,out_video):
	videoclip = VideoFileClip(input_video)
	audio_video = videoclip.audio # 原声
	audio_background = mpe.AudioFileClip(audio_file).volumex(random.uniform(0.01,0.018)) # 背景声
	# 视频音频和背景音频时长判断
	time_audio,time_bgaudio = audio_video.duration, audio_background.duration
	audio_background = audio_background.subclip(0,time_audio) if time_bgaudio > time_audio else audio_background
	# 音频混合
	mix_audio = mpe.CompositeAudioClip([audio_video, audio_background])
	final_clip = videoclip.set_audio(mix_audio)
	final_clip.write_videofile(out_video)



def main():
	# t_id = threading.get_ident()
	while True:
		row_index,row = q.get()
		name_now = row_index
		video_path = row['path']
		start_time , end_time = row['starttime'] , row['endtime']
		is_tip = row['add_tip']
		# 需剪切时间则返回剪切视频路径
		myvideo ,video_path = cut_time(video_path, f'{name_now}cut.mp4' , start_time=start_time,end_time=end_time)
		fps = int(myvideo.fps)
		time_long = myvideo.duration
		frames_num = int(fps * time_long)
		video_size = myvideo.size
		print('fps:',fps, 'time:',time_long, 'frames:',frames_num)
		try:
			# 多个背景图片帧
			bg_img_path = f'{name_now}_bgimg'
			bg_imgs = gen_rand_bgimgs(bg_img_path,img_size=video_size,img_num=random.randint(20,40))
			# 合成背景视频
			bg_video_path = f'{name_now}_bgvideo.mp4'
			imgs_to_video(bg_imgs,bg_video_path, time_long)
			if is_tip == 1:
				add_cover_img(cover_img='../bottom.png',video_path=bg_video_path,video_out_path=bg_video_path)
			print('bg video success...')
			shutil.rmtree(bg_img_path) if os.path.exists(bg_img_path) else 1

			# 截取视频区域范围
			if video_size[0] < 720:
				position1 ,position2 = [(0, 300),(video_size[0], 800)]
			elif video_size[0] < 1080:
				position1 ,position2 =[(0, 350),(video_size[0], 1100)]
			else:
				position1 ,position2 = [(0, 500),(video_size[0], 1500)]
			video_crop_path = f'{name_now}part.mp4'
			os.remove(video_crop_path) if os.path.exists(video_crop_path) else 1
			video_crop(position1, position2, video_path, video_crop_path)
			print('video crop success...')

			# 改变每一帧的亮度
			video_crop_path_light = f'{name_now}part-light.mp4' #改亮度后的文件
			increase_video_brightness(video_crop_path,video_crop_path_light,add_value)
			print('video crop change light success...')

			# 生成多个词云图片
			ciyun_img_path = f'{name_now}_ciyunimg' # 图片存储路径
			video_crop_size = VideoFileClip(video_crop_path).size
			ciyun_imgs = gen_rand_ciyunimgs(ciyun_img_path,img_size=video_crop_size,img_num=random.randint(20,40))
			# 词云图片合成视频
			ciyun_video = f'{name_now}ciyunvideo.mp4'
			imgs_to_video(ciyun_imgs, ciyun_video, time_long)
			#词云视频再覆盖一层图片
			add_cover_img(cover_img=random.choice(ciyun_imgs),video_path=ciyun_video,video_out_path=ciyun_video)
			print('ciyun video  success...')
			shutil.rmtree(ciyun_img_path) if os.path.exists(ciyun_img_path) else 1

			# 添加1层词云视频画中画
			dict_cropvideo_mix = {'video_down':ciyun_video, 'video_up':video_crop_path_light,'outputvideo':video_crop_path}
			composite_videos(**dict_cropvideo_mix)

			# 再次添加画中画效果
			composite_video_path = f'{name_now}merge_video.mp4'
			dict_bgvideo_mmix = {'video_down':bg_video_path, 'video_up':video_crop_path,'outputvideo':composite_video_path}
			composite_videos(**dict_bgvideo_mmix)

			# 视频添加水印标题图片
			title = '\n'.join(row['图片标题1'].split(r'|'))
			logo_img = f'{name_now}logo.png'
			logosize = video_size[0] - 2,350
			logopic_text(title,logofile=logo_img,img_size=logosize)
			video_logoimg_path = f'{name_now}merge_video_logo.mp4'
			os.remove(video_logoimg_path) if os.path.exists(video_logoimg_path) else 1
			add_logo_img(logo_img, composite_video_path, video_logoimg_path)

			# 视频添加文字水印
			title = re.sub('[\/:*?"<>|\n]', '-', title)
			video_logotext_path = f'./{res_video_pathname}/{title}.mp4'
			print(video_logotext_path)
			os.remove(video_logotext_path) if os.path.exists(video_logotext_path) else 1
			shuiyin_text = '关注我,传承中医'
			add_shuiyin_text(shuiyin_text, video_logoimg_path, video_logotext_path)

			# 添加干扰音频
			video_logotext_audio = f'./{res_video_pathname}/{title}-audio.mp4'
			add_bgaudio(video_logotext_path,audio_file,video_logotext_audio)
			os.remove(video_logotext_path) if os.path.exists(video_logotext_path) else 1
		except Exception as e:
			traceback.print_exc()
		finally:
			q.task_done()


if __name__ == "__main__":
	s_start = time.time()
	config_excel = './config-中医文化.xlsx'
	res_video_pathname = 'newvideo'
	q = queue.Queue()
	for index,row in pd.read_excel(config_excel).iterrows():
		if row['是否选用'] == 1:
			q.put((index,row))

	for i in range(4):
		t = threading.Thread(target=main)
		t.setDaemon(True)
		t.start()
	q.join()
	s_end = time.time()
	print('spent:',(s_end - s_start) / 60 ,'min')
