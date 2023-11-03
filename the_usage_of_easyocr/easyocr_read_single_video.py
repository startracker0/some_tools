import cv2
import easyocr
import os
import pandas as pd
from tqdm import tqdm
import re
import numpy as np
import math
import argparse

from PIL import Image, ImageEnhance

def pic_pre_process(image):
    shape = image.shape
    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                if image[i, j, k] < 200:
                    image[i, j, :] = 0
                if image[i, j, 0] > 200 and image[i, j, 1] > 200 and image[i, j, 2] > 200:
                    image[i, j, :] = 255
    return image


parser = argparse.ArgumentParser(description='Process video frames and perform text recognition.')

# 添加输入视频文件路径参数
parser.add_argument('-i', '--input', required=True, help='Input video file path')

# 添加输出文件夹路径参数
parser.add_argument('-o', '--output', required=True, help='Output folder path for saving Excel files')

# 解析命令行参数
args = parser.parse_args()

# 获取输入视频文件路径和输出文件夹路径
input_video_path = args.input
parent_directory =os.path.basename(os.path.dirname(input_video_path))
output_folder = args.output
input_video_filename = os.path.basename(input_video_path)
print(input_video_path)
print(input_video_filename)
print(parent_directory)
# 检查输出文件夹是否存在，如果不存在则创建
os.makedirs(output_folder, exist_ok=True)
# script_dir = os.path.abspath(os.path.dirname(__file__))



    
#input_video_filename = 'DJI_20230913163909_0001_0002_0003_0004_R_U.mp4'
#script_dir = os.path.dirname(__file__)
#video_path = os.path.join(script_dir, input_video_filename)

# 使用正则表达式提取目标字符串中的数字部分
height = re.search(r'(\d+)m', input_video_path).group(1)

# 将提取到的数字转换为整数
extracted_number = int(height)

# 输出提取到的数字
print("Extracted Number:", extracted_number)



# 感兴趣区域的坐标和尺寸 (x, y, width, height)
roi_x, roi_y, roi_width, roi_height = 512, 583, 27, 19
roi_X, roi_Y, roi_WD, roi_HT = 1226,289,20,20
# 定义像素值跳变的阈值
threshold = 50
# 打开视频文件
cap = cv2.VideoCapture(input_video_path)

# 检查视频是否成功打开
if not cap.isOpened():
    print("Error: 无法打开视频文件.")
    exit()

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print("Total frames in the video:", total_frames)

# 初始化EasyOCR对象
reader = easyocr.Reader(['ch_sim','en'],gpu = True)# ,
single_video_frame = 10254
# 初始化一个空的DataFrame来存储数据
data = []
k = 0 #状态
previous_text = ""
last_not_none_text=""
distance = ""
#print('changdu',len(input_video_filename))
#num_datasets = (total_frames - 1) // single_video_frame
num_datasets = (len(input_video_filename)-26)/5
print(num_datasets)
# 分割数据为四个不同的数据集
datasets = [[] for _ in range(int(num_datasets) + 1)]  # 创建包含空列表的列表
#print(len(datasets))
# width, height = 100, 100
# # 创建全黑图像
# black_background = np.zeros((height, width), dtype=np.uint8)
# x, y = 50, 50
for _ in tqdm(range(total_frames)):
    # 读取一帧
    ret, frame = cap.read()

    # 如果视频读取结束，退出循环
    if not ret:
        break
    frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
    roi_red = frame[roi_Y:roi_Y + roi_HT, roi_X:roi_X + roi_WD]
    red_pixels = roi_red[(roi_red[:, :, 2] > 100) & (roi_red[:, :, 1] < 100) & (roi_red[:, :, 0] < 100)]
    #print(red_pixels)
    # 裁剪感兴趣的区域

    roi = frame[roi_y:roi_y + roi_height, roi_x:roi_x + roi_width]
    # cv2.rectangle(roi, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (0, 255, 0), 2) 
    # cv2.imshow('ROI', roi)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
    enhanced_roi = pic_pre_process(roi)
    #enhanced_roi_gray = cv2.cvtColor(enhanced_roi, cv2.COLOR_BGR2GRAY)
    # print(y+enhanced_roi_gray.shape[0])
    # black_background[y:y+enhanced_roi_gray.shape[0],x:x+enhanced_roi_gray.shape[1]] = enhanced_roi_gray
    # interest = cv2.pyrDown(cv2.pyrDown(interest)) # picture too large for stack overflow
    # bg = cv2.medianBlur(interest, 51) # suitably large kernel to cover all text
    # roi = 255 - cv2.absdiff(bg, interest)
    #denoised_image = cv2.medianBlur(enhanced_roi, 5)

    # if frame_number == 1:
    #     #image = cv2.imread(binary_roi)
    #     #output_directory = '/data3/X_Images/data_angle/test'
    #     output_path = '/data3/X_Images/data_angle/black_background.jpg'
    #     cv2.imwrite(output_path, black_background)
    #     print("yes!")
    results = reader.readtext(roi)
    recognized_text = ""
    

    for (bbox, text, prob) in results:
        numbers = re.findall(r'-?\d+', text)
        print("识别出来的text",text)
    # 将提取到的数字添加负号并拼接到recognized_text中
        for number in numbers:
            # 在数字前添加负号
            formatted_number = '-' + number if number[0] != '-' else number
            recognized_text += formatted_number + " "
    if red_pixels.size == 0:
        print("#####发现不合理情况") # 如果不是红色，不合理
        k = 1
    else:
        k = 0
        
    
    if k == 0:
        if recognized_text.strip() == "":
            recognized_text = previous_text
            print("你没看错,就是none")
            # else:
            #     if previous_text != "NONE":
            #         last_not_none_text = previous_text
        print("recongized",recognized_text.strip())
        print("previous",previous_text.strip())
        #  print("last not none",last_not_none_text.strip())
        if re.match(r'^-?\d+$', recognized_text.strip()) and re.match(r'^-?\d+$', previous_text.strip()):
            #if abs(int(recognized_text.strip()) - int(previous_text.strip())) >= 10:
            if abs(int(recognized_text.strip())) >= 90 or abs(int(recognized_text.strip()) - int(previous_text.strip())) >= 30:
                #print("111111111111111111111111111111111111111111")
                print("!!!!!!!!!!!!!!!!!!")
                recognized_text = previous_text
                    #last_not_none_text = recognized_text
                # previous_text = recognized_text
                print("recognized corrected",recognized_text.strip())
                angle_radians = math.radians(int(recognized_text.strip()))
                height = float(height)
                angle = float(angle_radians)
                cos_value = math.cos(angle)
                distance = height / cos_value
                print(distance)
            else:
                recognized_text = recognized_text
                    #last_not_none_text = recognized_text
                    #previous_text = recognized_text
                angle_radians = math.radians(int(recognized_text.strip()))
                height = float(height)
                angle = float(angle_radians)
                cos_value = math.cos(angle)
                distance = height / cos_value
                print(distance)
        elif re.match(r'^-?\d+$', recognized_text.strip()):
            recognized_text = recognized_text
            angle_radians = math.radians(int(recognized_text.strip()))
            height = float(height)
            angle = float(angle_radians)
            cos_value = math.cos(angle)
            distance = height / cos_value
            print(distance)
        elif re.match(r'^-?\d+$', recognized_text.strip()) == 0:
            recognized_text = "NONE"
            distance = "NONE"
    else:
        recognized_text = "NONE"
        distance = "NONE"
            
 # 将帧数和识别的数字添加到data列表中
    #data.append({'Frame Number': frame_number, '角度': recognized_text.strip(), '测距(m)': distance})
    dataset_index = (frame_number - 1) // single_video_frame   # 计算数据应该属于哪个数据集10254 
    print(dataset_index)
    if dataset_index <= num_datasets :
        frame_number = frame_number - dataset_index * single_video_frame
        datasets[dataset_index].append({'Frame Number': frame_number, '角度': recognized_text.strip(), '测距(m)': distance})
        
        formatted_text = "Frame Number: {},  角度: {}, 测距(m): {}".format(frame_number, recognized_text.strip(), distance)
        print(formatted_text)
        print("****************************************************************************")
        previous_text = recognized_text
    else:
        break

# 将data列表转换为DataFrame    'DJI_20230913163909_0001_0002_0003_0004_R_U.mp4'

for i, dataset in enumerate(datasets):
    #for i in range(dataset_index + 1):
     #   print(dataset_index)
        output_filename_prefix  = input_video_filename[:18] + input_video_filename[18+i*5:18+(i+1)*5] + '_R' + f'_{extracted_number}m' + f'_{parent_directory}'
        output_filename = os.path.join(output_folder, f'{output_filename_prefix}.xlsx')
        df = pd.DataFrame(dataset)
        df.to_excel(output_filename, index=False)
        print(f'Saved {output_filename}')
# 释放视频文件
cap.release()