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
三：
 1）词云视频和画面视频叠加->视频1
 2）背景视频和视频1叠加->视频2
四：
 视频2添加干扰音频

# if video_size[0] < 720:
# 	position1 ,position2 = [(0, 300),(video_size[0], 800)]
# elif video_size[0] < 1080:
# 	position1 ,position2 =[(0, 350),(video_size[0], 1100)]
# else:
# 	position1 ,position2 = [(0, 500),(video_size[0], 1500)]

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
bgaudio_files = ['./audio/爱江山更爱美人.mp3','./audio/电流杂声_耳聆网.wav',]
# 选择文字字体和大小,加载字体才能支持中文
setFont = ImageFont.truetype(font='C:/windows/fonts/STZHONGS.TTF', size=45)

# 截取某个时间范围内的视频
def cut_time(video_path,video_cut_path, start_time='',end_time=''):
	video_base = VideoFileClip(video_path)
	if not isinstance(start_time,int) or not isinstance(end_time,int):
		return video_base ,video_path
	video_base = video_base.subclip(start_time,end_time)
	video_base.write_videofile(video_cut_path)
	return video_base ,video_cut_path


# 生成多个背景图片帧,每个图片写时间戳
def gen_rand_bgimgs(save_path,img_size,img_num,location=(0,0),setFont=setFont):
	bg_imgs = []
	for i in range(img_num):
		num1,num2,num3 = random.randint(1,255),random.randint(1,255),random.randint(1,255)
		# 生成大小为400x400RGBA是四通道图像，RGB表示R，G，B三通道，A表示Alpha的色彩空間
		image = Image.new(mode='RGB', size=img_size, color=(num1, num2, num3))
		# ImageDraw.Draw 新建绘画图像
		draw = ImageDraw.Draw(im=image)
		text = f'{time.time()}'
		fontColor = "%06x" % random.randint(0, 0xFFFFFF)
		draw.text(location, text,font=setFont,fill=f'#{fontColor}', direction=None)
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
		color = "%06x" % random.randint(0, 0xFFFFFF)
		wc = wordcloud.WordCloud(font_path=r"C:\Windows\Fonts\simsunb.ttf",width = width,height = height,
			mask=mask,background_color=f'#{color}',max_words=1000,stopwords=['的'])
		wc.generate(text) # 加载词云文本
		os.mkdir(save_path) if not os.path.exists(save_path) else 1
		outimg = os.path.join(save_path,f'{i}.png')
		wc.to_file(outimg)
		ciyun_imgs.append(outimg)
	return ciyun_imgs


# 给视频覆盖1个图片
def add_cover_img(cover_img,video_path,video_out_path,opacity=1):
	video = VideoFileClip(video_path)
	# 图片logo
	img_obj = Image.open(cover_img)
	logo = ImageClip(cover_img).set_duration(video.duration).resize(height=img_obj.height,width=img_obj.width).margin(right=0, top=0,opacity=0).set_pos(("center", "bottom")).set_opacity(opacity)  # 水印的位置/透明度

	final = CompositeVideoClip([video, logo])
	# mp4文件默认用libx264编码， 比特率单位bps
	final.write_videofile(video_out_path, codec="libx264", bitrate="10000000")


# 图片合成视频
def imgs_to_video(my_imgs,output_video_path, time_long,each_image_duration = 3):
	"""
	time_long:生成的视频时长
	each_image_duration:每个图片站展现时间
	"""
	cv2_imgs=[]
	[cv2_imgs.append(cv2.imread(i)) for i in my_imgs]
	height, width, layers = cv2_imgs[0].shape
	size = (width,height)
	# 图片生成的视频
	outvideo = cv2.VideoWriter(output_video_path,cv2.VideoWriter_fourcc(*'mp4v'), 1.0, size) #DIVX avi
	# 所需图片数
	img_num = int(time_long / each_image_duration) + 1
	img_num_last = img_num if img_num < len(my_imgs) else len(my_imgs)
	print('img_num_last：',img_num_last)
	img_objs = random.sample(cv2_imgs,img_num_last)
	print('img_objs：',len(img_objs),type(img_objs))
	for img_obj in img_objs:
		image=cv2.resize(img_obj,size)
		for _ in range(each_image_duration):
			outvideo.write(image)
	# 判断图片生成的视频时长
	time_cost = each_image_duration * len(img_objs)
	print('time_cost：',time_cost,'time_long：',time_long)
	if time_cost < time_long:
		time_add = int(time_long - time_cost) + 1
		image = random.choice(cv2_imgs)
		for _ in range(time_add):
			outvideo.write(image)

	outvideo.release()
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

# 设置图片从左平移到右侧
def move_to(inputvideo_path ,imgpath ,outvideo_path):
	video_clip = VideoFileClip(inputvideo_path)
	image_clip = ImageClip(imgpath)
	pos_value  = int(video_clip.size[0] / video_clip.duration)
	video_with_image = CompositeVideoClip([video_clip, 
		image_clip.set_pos((0, 0)).set_start(0).set_duration(video_clip.duration).set_end(video_clip.duration).set_pos(lambda t: (pos_value*t, 0)).crossfadein(1)])
	video_with_image.write_videofile(outvideo_path)


# 改变视频每一帧的亮度
def handle_frame(image_frame):
	image_frame_result = image_frame * add_value
	# 如果颜色值超过255，直接设置为255
	image_frame_result[image_frame_result > 255] = 255
	return image_frame_result


def increase_video_brightness(inputvideo_path ,outvideo_path):
	video = VideoFileClip(inputvideo_path)
	result = video.fl_image(handle_frame)
	result.write_videofile(outvideo_path)

def increase_video_brightness2(inputvideo_path ,outvideo_path):
	video = VideoFileClip(inputvideo_path)
	result = video.fx(vfx.colorx,random.uniform(1.02000001,1.090000002))
	result.write_videofile (outvideo_path)

# 黑白处理
def video_blackwhite(inputvideo_path ,outvideo_path):
	video = VideoFileClip(inputvideo_path)
	result = video.fx(vfx.blackwhite)
	result.write_videofile (outvideo_path)

# 镜像
def video_mirroring(inputvideo_path ,outvideo_path):
	video = VideoFileClip(inputvideo_path)
	result = video.fx(vfx.mirror_x)
	result.write_videofile (outvideo_path)

# 叠加两段视频(画中画)
def composite_videos(video_down, video_up ,outputvideo,value):
	bg_video_clip = VideoFileClip(video_down)
	video_crop_clip = VideoFileClip(video_up)

	width_down, height_down = bg_video_clip.w, bg_video_clip.h
	width_up, height_up = video_crop_clip.w, video_crop_clip.h

	# 视频缩放
	video_up_set = video_crop_clip.resize((width_down, width_down / width_up * height_up))

	# 叠加视频
	composite_video_clip = CompositeVideoClip([bg_video_clip, video_up_set.set_pos("center").set_opacity(value)])
	composite_video_clip.write_videofile(outputvideo)

	return composite_video_clip


# 生成标题图片
def logotext_pic(text,outfile,img_size,location=(10,5),max_num=10,fontColor='#000000'):
	num1,num2,num3 = 255,255,0
	image = Image.new(mode='RGB', size=img_size, color='#FF6347')
	# ImageDraw.Draw 新建绘画图像
	draw = ImageDraw.Draw(im=image)
	fontsize = int((img_size[0]-location[0])/max_num) # 字体大小
	setFont = ImageFont.truetype(font='C:/windows/fonts/STZHONGS.TTF', size=fontsize)
	draw.text(location, text,font=setFont,fill=fontColor, direction=None)
	image.save(outfile)
	return outfile


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
def add_shuiyin_text(account_name,video_path,video_logo_path):
	# texts = '♥,✤,✥,❋,✦,✪,✫,✬,✭,✮,✯,❂,✡,★,✱,✲,✳,✴,✵,✶,✷,✸,✹,✺,✼,❄,❅,❆,❇,❈,❉,❊,㊍,㊌,㊋,㊏,㊐,㊊,*,&,@,#,~,+'.split(',')
	texts = '*,♥,-,+,),(,$,#,@,|,——,!,【,】,%,=,1,2,3,4,5,6,7,8,9,0,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z'.split(',')
	video = VideoFileClip(video_path)
	video_time = video.duration
	w, h = video.w , video.h
	n = random.randint(40,50)
	logos = []
	# colors = ['#FF6347','#FF7F50','#CD5C5C','#F08080','#E9967A','#FA8072','#FFA07A','#FF4500','#FF8C00','#EEE8AA','#BDB76B','#F0E68C']
	for i in range(n):
		Color = "%06x" % random.randint(0, 0xFFFFFF)
		logo_text = random.choice(texts)
		logo_text = f'@{account_name}' if i == int(n/2) else logo_text
		logo = (TextClip((logo_text), fontsize=random.randint(20,25) if logo_text!=account_name else 30, font='Simhei', color=f'#{Color}').set_start(0).set_end(int(video_time))  # 水印持续时间
				.set_pos((random.randint(0, w), random.randint(0, int(h * 0.9))))).set_opacity(0.8)
		logos.append(logo)
	final = CompositeVideoClip([video, *logos])
	# mp4文件默认用libx264编码， 比特率单位bps
	final.write_videofile(video_logo_path, codec="libx264", bitrate="10000000")



# 视频添加背景音频
def add_bgaudio(input_video,bgaudio_files,out_video):
	videoclip = VideoFileClip(input_video)
	mix_audio = videoclip.audio # 原声
	for bgaudio_file in bgaudio_files:
		audio_background = mpe.AudioFileClip(bgaudio_file).volumex(random.uniform(0.04,0.06)) # 背景声
		# 视频音频和背景音频时长判断
		time_audio,time_bgaudio = mix_audio.duration, audio_background.duration
		start_s = random.randint(1,3)
		audio_background = audio_background.subclip(start_s,time_audio+start_s) if time_bgaudio > time_audio else audio_background
		# 音频混合
		mix_audio = mpe.CompositeAudioClip([mix_audio, audio_background])
	final_clip = videoclip.set_audio(mix_audio)
	final_clip.write_videofile(out_video)
	# 生成封面图
	fname = os.path.splitext(out_video)[0]
	final_clip.save_frame(f"{fname}_frame.png", t = 1)



def main():
	global add_value
	t_id = threading.get_ident()
	add_value = random.uniform(1.05,1.09)
	while True:
		row_index,row = q.get()
		name_now = row_index
		video_path = row['path']
		start_time , end_time = row['starttime'] , row['endtime']
		is_tip = row['add_tip']
		account_name = row['账号归属']
		res_video_pathname = f'{video_pathname}/{account_name}' # 最终视频路径
		# shutil.rmtree(res_video_pathname) if os.path.exists(res_video_pathname) else 1
		os.mkdir(res_video_pathname) if not os.path.exists(res_video_pathname) else 1
		# 需剪切时间则返回剪切视频路径
		myvideo ,video_path = cut_time(video_path, f'{name_now}cut.mp4' , start_time=start_time,end_time=end_time)
		fps = int(myvideo.fps)
		time_long = myvideo.duration
		frames_num = int(fps * time_long)
		video_size = myvideo.size
		print('fps:',fps, 'time:',time_long, 'frames:',frames_num)
		try:
			# 多个背景图片帧
			bg_img_path = f'{temp_path}/{name_now}_bgimg'
			bg_imgs = gen_rand_bgimgs(bg_img_path,img_size=video_size,img_num=random.randint(20,40))
			# 合成背景视频
			bg_video_path = f'{temp_path}/{name_now}_bgvideo.mp4'
			imgs_to_video(bg_imgs,bg_video_path, time_long)
			if is_tip != 0:
				add_cover_img(cover_img='../bottom.png',video_path=bg_video_path,video_out_path=bg_video_path,opacity=1)
			print('bg video success...')
			shutil.rmtree(bg_img_path) if os.path.exists(bg_img_path) else 1
			# 截取视频区域范围
			h1 = int(video_size[1] * 0.265)
			h2 = int(video_size[1] * 0.8)
			position1 ,position2 =[(0, h1),(video_size[0], h2)]
			position1 ,position2 = [(0, 0),(video_size[0], ideo_size[1])] if '大学生' in row['图片标题1'] else position1 ,position2
			# 截取的视频
			video_crop_path = f'{temp_path}/{name_now}crop.mp4'
			# os.remove(video_crop_path) if os.path.exists(video_crop_path) else 1
			video_crop(position1, position2, video_path, video_crop_path)
			print('video crop success...')

			# 改变每一帧的亮度
			video_crop_path_light = f'{temp_path}/{name_now}crop-light.mp4' #改亮度后的文件
			increase_video_brightness2(video_crop_path,video_crop_path_light)
			print('video crop change light success...')

			# 生成多个词云图片
			ciyun_img_path = f'{temp_path}/{name_now}_ciyunimg' # 词云图片存储路径
			video_crop_size = VideoFileClip(video_crop_path).size
			ciyun_imgs = gen_rand_ciyunimgs(ciyun_img_path,img_size=video_crop_size,img_num=random.randint(20,40))
			# 词云图片合成视频
			ciyun_video = f'{temp_path}/{name_now}ciyunvideo.mp4'
			imgs_to_video(ciyun_imgs, ciyun_video, time_long)
			print('ciyun video  success...')

			# 原视频裁剪部分和词云视频画中画
			ciyun_crop_merge = f'{temp_path}/{name_now}ciyun_crop_merge.mp4'
			dict_cropvideo_mix = {'video_down':video_crop_path_light, 'video_up':ciyun_video,'outputvideo':ciyun_crop_merge,'value':random.uniform(0.15,0.20)}
			composite_videos(**dict_cropvideo_mix)

			# 词云画中画视频：黑白处理+镜像
			ciyun_crop_merge_blackwhite = f'{temp_path}/{name_now}ciyun_crop_merge_blackwhite.mp4'
			ciyun_crop_merge_blackwhite_mx = f'{temp_path}/{name_now}ciyun_crop_merge_blackwhite_mx.mp4'
			video_blackwhite(ciyun_crop_merge,ciyun_crop_merge_blackwhite)
			video_mirroring(ciyun_crop_merge_blackwhite,ciyun_crop_merge_blackwhite_mx)

			# 词云画中画视频添加各种符号
			ciyun_crop_merge_addletter = f'{temp_path}/{name_now}ciyunv_crop_mergeletter.mp4'
			add_shuiyin_text(account_name,ciyun_crop_merge, ciyun_crop_merge_addletter)

			#和黑白镜像视频画中画
			ciyun_crop_merge_addletter_mixblackwhite = f'{temp_path}/{name_now}ciyunv_crop_mergeletter_mixblackwhite.mp4'
			dict_bgvideo_mmix = {'video_down':ciyun_crop_merge_addletter, 'video_up':ciyun_crop_merge_blackwhite_mx,'outputvideo':ciyun_crop_merge_addletter_mixblackwhite,'value':random.uniform(0.1,0.2)}
			composite_videos(**dict_bgvideo_mmix)

			shutil.rmtree(ciyun_img_path) if os.path.exists(ciyun_img_path) else 1
			# os.remove(ciyun_video) if os.path.exists(ciyun_video) else 1

			# 和背景视频添加画中画
			composite_bgvideo_path = f'{temp_path}/{name_now}merge_bgvideo.mp4'
			dict_bgvideo_mmix = {'video_down':bg_video_path, 'video_up':ciyun_crop_merge_addletter_mixblackwhite,'outputvideo':composite_bgvideo_path,'value':1}
			composite_videos(**dict_bgvideo_mmix)

			# 视频添加水印标题图片
			title = '\n'.join(row['图片标题1'].split(r'|'))
			logo_img = f'{temp_path}/{name_now}logo.png'
			logosize = video_size[0] - 2, int(video_size[1] * 0.3)
			# 生成logo图片
			logotext_pic(title,outfile=logo_img,img_size=logosize)
			video_logoimg_path = f'{temp_path}/{name_now}merge_video_logo.mp4'
			# os.remove(video_logoimg_path) if os.path.exists(video_logoimg_path) else 1
			add_logo_img(logo_img, composite_bgvideo_path, video_logoimg_path)

			# 结果视频名称
			title = re.sub('[\/:*?"<>|\n]', '-', title)
			video_logotext_path = f'./{res_video_pathname}/{title}.mp4'
			print(video_logotext_path)
			# os.remove(video_logotext_path) if os.path.exists(video_logotext_path) else 1

			# 添加干扰音频
			video_logotext_audio = f'./{res_video_pathname}/{title}-audio.mp4'
			add_bgaudio(video_logoimg_path,bgaudio_files,video_logotext_audio)
		except Exception as e:
			traceback.print_exc()
			
		finally:
			q.task_done()


if __name__ == "__main__":
	s_start = time.time()
	config_excel = './config-中医文化.xlsx'
	video_pathname = 'newvideo'
	temp_path = 'tempvideo'
	shutil.rmtree(temp_path) if os.path.exists(temp_path) else True
	os.mkdir(temp_path) if not os.path.exists(temp_path) else True
	q = queue.Queue()
	for index,row in pd.read_excel(config_excel).iterrows():
		if row['是否选用'] == 1:
			q.put((index,row))

	for i in range(5):
		t = threading.Thread(target=main)
		t.setDaemon(True)
		t.start()
	q.join()
	s_end = time.time()
	print('spent:',(s_end - s_start) / 60 ,'min')
