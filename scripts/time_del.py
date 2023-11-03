import cv2
import os
from tqdm import tqdm

# 设置输入文件夹列表和输出文件夹
input_folders = ['20230909_beach_sunny',
                 '20230910_beach_dark',
                 '20230913_beach_dark','20230913_beach_rain','20230913_beach_sunny',
                 '20230914_beach_dark','20230914_beach_dark_rain',
                 '20230915_beach_dark','20230915_beach_sunny',
                 '20230918_beach_dark','20230918_beach_sunny',
                 '20230919_beach_dark','20230919_beach_sunny',
                 '20230920_beach_dark','20230920_beach_sunny',
                 '20230921_beach_dark','20230921_beach_sunny','20230921_beach_rain',
                 '20230922_beach_dark','20230922_beach_sunny','20230922_beach_rain','20230922_beach_foggy']  # 输入文件夹路径列表29
output_folder = ''  # 输出文件夹路径

# 递归遍历文件夹中的视频文件
for input_folder in input_folders:
    for folder in os.listdir(input_folder):
        folder_path = os.path.join(input_folder, folder)
        for folder1 in os.listdir(folder_path):
            folder_path = os.path.join(folder_path, folder1)
            if os.path.isdir(folder_path):
                print(folder_path)
                files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.endswith('_R.mp4')]
                
                # 使用tqdm显示进度条
                with tqdm(total=len(files), desc=f"处理文件夹 {folder_path} 中的视频") as pbar:
                    for file in files:
                        compressed_video_path =  os.path.join(folder_path, file)
                        parent_directory = os.path.dirname(compressed_video_path)
                        input_video_filename = os.path.basename(compressed_video_path)
                        print(input_video_filename)
                        # 输出视频路径
                        output_video_path =os.path.join(output_folder,  input_folder, folder, folder1)
                        num_datasets = int((len(input_video_filename)-18-2-4)/5)
                        print(num_datasets)
                        raw_frame_path = [[] for _ in range(int(num_datasets) + 1)]
                        target_frame_count = 0
                        for i in range(num_datasets):
                            raw_frame_path[i] = os.path.join(parent_directory , input_video_filename[:18] + input_video_filename[18+i*5:18+(i+1)*5] + '_Z.mp4')
                            print(raw_frame_path[i])
                            cap1 = cv2.VideoCapture(raw_frame_path[i])
                            target_frame_count = target_frame_count + int(cap1.get(cv2.CAP_PROP_FRAME_COUNT)) # 你可以根据需要修改这个值
                            print(target_frame_count)
                            cap1.release()
                        # 指定的总帧数


                        # 获取压缩后视频的总帧数
                        cap = cv2.VideoCapture(compressed_video_path)
                        if not cap.isOpened():
                            print("Error: 无法打开视频文件.")
                            exit()
                        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))#?
                        cap.release()

                        # 计算需要删减的帧数
                        frames_to_remove = total_frames - target_frame_count

                        # 获取随机删帧的帧号列表
                        frames_to_remove_indices = random.sample(range(total_frames), frames_to_remove)

                        # 打开压缩后的视频
                        cap = cv2.VideoCapture(compressed_video_path)

                        # 定义视频编解码器并创建VideoWriter对象
                        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 使用MP4V编码器
                        out = cv2.VideoWriter(output_video_path, fourcc, cap.get(cv2.CAP_PROP_FPS), (int(cap.get(3)), int(cap.get(4))))

                        # 逐帧处理视频
                        frame_number = 0
                        while True:
                            ret, frame = cap.read()

                            # 如果视频读取结束，退出循环
                            if not ret:
                                break

                            # 如果当前帧不在帧号列表中，则将该帧写入输出视频
                            if frame_number not in frames_to_remove_indices:
                                out.write(frame)

                            frame_number += 1

                        # 释放VideoCapture和VideoWriter对象
                        cap.release()
                        out.release()

                        print(f'视频已处理，输出路径为: {output_video_path}')
