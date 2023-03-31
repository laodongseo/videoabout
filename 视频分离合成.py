"""
视频分离为图片
图片再合成视频
"""

import os
import cv2
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip


def split_video_to_images(video_file, output_dir):
	# 加载视频文件
	cap = cv2.VideoCapture(video_file)
	# 获取视频帧率和总帧数
	fps = cap.get(cv2.CAP_PROP_FPS)
	total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	duration = total_frames / fps
	# 逐帧读取视频，并将每一帧保存为图片
	for i in range(total_frames):
		ret, frame = cap.read()
		if not ret:
			break
		# 生成图片文件名
		filename = "{:0>6d}.jpg".format(i)
		filepath = os.path.join(output_dir, filename)
		# 保存图片
		cv2.imwrite(filepath, frame)
	# 关闭视频文件
	cap.release()
	return fps, duration

def merge_images_to_video(images_dir, output_file, fps, duration):
	# 加载图片文件列表
	images = [os.path.join(images_dir, f) for f in os.listdir(images_dir) if f.endswith(".jpg")]
	# 对图片文件列表进行排序
	images.sort()
	# 生成视频剪辑对象
	clip = ImageSequenceClip(images, fps=fps)
	# 设置视频剪辑对象的时长
	clip = clip.set_duration(duration)
	# 保存视频剪辑对象为视频文件
	clip.write_videofile(output_file, fps=fps)

def main(video_file, output_file):
	# 定义图片保存目录
	images_dir = "images"
	# 分离视频成图片
	fps, duration = split_video_to_images(video_file, images_dir)
	# 将图片合成视频
	merge_images_to_video(images_dir, output_file, fps, duration)
	# 删除临时保存的图片
	for f in os.listdir(images_dir):
		os.remove(os.path.join(images_dir, f))
	os.rmdir(images_dir)

if __name__ == "__main__":
	video_file = "WeChat_20230328160053.mp4"
	output_file = "output.mp4"
	main(video_file, output_file)
