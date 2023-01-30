# coding:utf8
"""
视频处理函数库
"""
from PIL import Image
from  moviepy.editor import *
import cv2,shutil

#遮罩
def add_zm(fg_in_bg_avi):
    clip1 = VideoFileClip(fg_in_bg_avi)
    clip3 = VideoFileClip(zm_video_path, has_mask=True)
    video = CompositeVideoClip([clip1, clip3])
    name = zm_video_path.split('.', 1)[0] + ".mp4"
    video.write_videofile(name, audio=False)  # 先不加音频
    video.close()
    return name


# 分离视频和音频
def split_video_voice(video_path,audio_path,video_novoice_path):
	# 无声视频
	video = VideoFileClip(video_path)
	video_novoice = video.without_audio() 
	video.write_videofile(video_novoice_path)

	# 提取音频
	video.audio.write_audiofile(audio_path)


# 视频音频合并
def video_add_audio(video_path,audio_path,new_video):
	video = VideoFileClip(video_path)
	audio_clip = AudioFileClip(audio_path)
	video = video.set_audio(audio_clip)
	video.write_videofile(new_video)


# 视频沿x轴翻转
def array_video(video_path,new_video_path):
	video = VideoFileClip(video_path)
	video_clip2 = video.fx( vfx.mirror_x)
	final_clip = clips_array([[video],[video_clip2]])
	final_clip.write_videofile(new_video_path)


# 截取某个时间范围内的视频
def  cut_time(video_path,video_cut_path, start_time='',end_time=''):
	video_base =  VideoFileClip(video_path)
	if start_time == end_time == '':
		return video_base
	video_base = video_base.subclip(start_time,end_time)
	video_base.write_videofile(video_cut_path)
	return video_cut_path


# 获取某个时间点的图片帧
def get_frame_from_video(video_path, frame_time, img_path):
	# 秒转为时、分、秒
	m, s = divmod(frame_time, 60)
	h, m = divmod(m, 60)
	time_pre  = "%02d:%02d:%02d" % (h, m, s)
	os.system(f'ffmpeg -ss {time_pre} -i {video_path} -frames:v 1 {img_path}')
	return img_path


# 单图片生成背景视频(帧率|时长要和目标视频一一致)
def one_pic_to_video(image_path, output_video_path, fps, time):
	image_clip = ImageClip(image_path)
	img_width, img_height = image_clip.w, image_clip.h

	frame_num = (int)(fps * time) # 总共的帧数
	img_size = (int(img_width), int(img_height))
	fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
	video = cv2.VideoWriter(output_video_path, fourcc, fps, img_size)

	for index in range(frame_num):
		frame = cv2.imread(image_path)
		# 直接缩放到指定大小
		frame_suitable = cv2.resize(frame, (img_size[0], img_size[1]), interpolation=cv2.INTER_CUBIC)
		# 把图片写进视频
		video.write(frame_suitable)

	video.release()

	return output_video_path


# 视频区域裁剪
def video_crop(position1, position2, video_source ,video_crop_path):
	"""
	把图片帧拖进系统自带画图工具中截取的坐标点
	"""
	width,height = None,None # 宽度和高度
	x_center,y_center = None,None # X、Y轴中心点坐标

	# 剔除上下黑边选取影响范围
	video =  VideoFileClip(video_source)
	video_need = (video.fx(vfx.crop,position1[0],position1[1],position2[0],position2[1]))
	# video_need = video_need.resize((900, 900))
	video_need.write_videofile(video_crop_path)
	return video_crop_path


# 合成两段视频(画中画)
def composite_videos(video_down, video_up ,outputvideo):
	bg_video_clip = VideoFileClip(video_down)
	video_crop_clip = VideoFileClip(video_up)


	width1, height1 = bg_video_clip.w, bg_video_clip.h
	width2, height2 = video_crop_clip.w, video_crop_clip.h

	# 视频缩放
	video_up_set = video_crop_clip.resize((width1, width1 / width2 * height2))

	# 合成视频
	composite_video_clip = CompositeVideoClip([bg_video_clip, video_up_set.set_pos("center")])
	composite_video_clip.write_videofile(outputvideo)

	return composite_video_clip


# 给视频加logo图片
def add_logo_img(logo_img,video_path,video_logo_path):
	video = VideoFileClip(video_path)
	# 图片logo
	logo = (ImageClip(logo_img).set_duration(video.duration) # 水印持续时间
			.resize(height=80) # 水印的高度，会等比缩放
			.margin(right=8, top=8,opacity=1)  # 水印边距和透明度
			.set_pos(("center", "top")))  # 水印的位置
 
	final = CompositeVideoClip([video, logo])
	# mp4文件默认用libx264编码， 比特率单位bps
	final.write_videofile(video_logo_path, codec="libx264", bitrate="10000000")


# 添加多个随机文字水印
def add_logo_text(logo_text,video_path,video_logo_path):
	video = VideoFileClip(video_path)
	times = video.duration
	n = int(times * 0.8)  # 一共出现n次
	times_list = [i * (times / n) for i in range(n + 1)]
	logos = []
	for i in range(n):
		logo = (TextClip((logo_text), fontsize=10, font='Simhei', color='white')
				.set_start(times_list[i]).set_end(times_list[i + 1])  # 水印持续时间
				.set_pos((random.randint(0, video.w), random.randint(0, video.h))))  # 水印的位置
		logos.append(logo)
 
	final = CompositeVideoClip([video, *logos])
	# mp4文件默认用libx264编码， 比特率单位bps
	final.write_videofile(video_logo_path, codec="libx264", bitrate="10000000")



if __name__ == "__main__":

  video_path = r"D:\cms后台采纳.mkv"
  myvideo = cut_time(video_path,'1223.mp4')
  fps = int(myvideo.fps)
  time = myvideo.duration
  frames = int(fps * time)
  print(fps,time,frames)

  # 单个图片制作背景视频
  bg_img , bg_video = 'b.png','b.mp4'
  fps , time = fps ,time
  bg_video_path = one_pic_to_video(bg_img,bg_video,fps,time)

  # 获取视频中某个时间点的图片
  img_frame = '111.png'
  os.remove(img_frame) if os.path.exists(img_frame) else True
  get_frame_from_video(video_path ,25 ,img_frame)

  # 截取视频区域范围
  position1 = (0,200)
  position2 = (1437,873)
  video_crop_path = '111.mp4'
  video_crop(position1, position2, video_path ,video_crop_path)


  # 2个视频上下重合(画中画效果)
  composite_video_path = '22.mp4'
  composite_videos(bg_video_path ,video_crop_path ,composite_video_path)

  # 视频添加水印图片
  logo_img = 'logo.png'
  video_logoimg_path = 'aaa.mp4'
  add_logo_img(logo_img,composite_video_path,video_logoimg_path)

  # 视频添加文字水印
  video_logotext_path = '1.mp4'
  logo_text = '房子'
  add_logo_text(logo_text,video_logoimg_path,video_logotext_path)

