import os
import cv2
import re
import easyocr
import math
import pandas as pd
import openpyxl

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


def get_all_jpg_files(folder_path):
    jpg_files = []
    for foldername, subfolders, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.lower().endswith('.jpg'):
                file_path = os.path.join(foldername, filename)
                jpg_files.append(file_path)
    return jpg_files
# 创建一个新的Excel工作簿
workbook = openpyxl.Workbook()
sheet = workbook.active

folder_path = '/data3/X_Images/xuxiaoran/ocr/Images/images_1080P'
#folder_path =  '/data3/X_Images/xuxiaoran/ocr/Images/test'


jpg_files = get_all_jpg_files(folder_path)

data = []

count = 0
# 打印所有.jpg文件的路径
for jpg_file in jpg_files:
    print(jpg_file)
    input_image_path = jpg_file
    count = count + 1

    #a) 以下为获取文件名中相关信息
    #input_image_path = '/data3/X_Images/xuxiaoran/ocr/Images/images_1080P/3142_20230913163909_0003_Z_100m_infrared_2.0_rgb_3.3_sunny_frame_4200.jpg'
    input_image_filename = os.path.basename(input_image_path)
    #video_root_folder_path = '/data3/X_Images/xuxiaoran/ocr/video'
    video_root_folder_path = '/data3/X_Images/xuxiaoran/ocr/video'




    keyword_frame = re.search(r'(\d+).jpg', input_image_path).group(1)
    # 使用正则表达式提取'dark'关键字
    #date_pattern = r'_(\d{8})\d+_'  # 匹配8个数字的日期部分
    keyword_data = re.search(r'(\d{8})\d+_', input_image_filename).group(1)#8个时间信息

    # if keyword_weather == 'hazy':
    #     weather_info = 'beach_sunny'
    # else:
        
    keyword_hight = re.search(r'_(\d+)m_', input_image_filename).group(1)#100


    target_info = re.search(r'(\d{13,14})_', input_image_filename).group(1)   #14个时间信息
    print('shijianxinxi',target_info)
    keyword_index = re.search(r'_00(\d{2})_Z', input_image_filename).group(1)  #获取足够图片是在第几个视频
    print(keyword_index)
    key_the_first_num = re.search(r'^(\d+)_', input_image_filename).group(1)
    if 'hazy' in input_image_filename:
        input_image_filename = key_the_first_num + '_' + target_info + keyword_index + '_Z_' + f'{keyword_hight}m' + '_infrared_2.0_rgb_3.3_sunny' + f'_frame_{keyword_frame}.jpg'
    if 'fog' in input_image_filename:
        input_image_filename = key_the_first_num + '_' + target_info + keyword_index + '_Z_' + f'{keyword_hight}m' + '_infrared_2.0_rgb_3.3_fog' + f'_frame_{keyword_frame}.jpg'
    #print(input_image_filename)
    keyword_info =  re.search(r'_\d+m_(.*?)_frame_\d+\.jpg', input_image_filename).group(1)#infrared_2.0_rgb_3.3_sunny之类
    keyword_weather = re.search(r'_([a-zA-Z]+)_frame_', input_image_filename).group(1)#r'_([a-zA-Z]+)_frame_'
    if keyword_data == '20230907':
        weather_info = 'city_rain_180sunny'
    elif keyword_weather == 'rain' and keyword_data == '20230914':
        weather_info = 'beach_dark_rain'
    elif keyword_weather == 'fog':
        weather_info = 'beach_foggy'
    else:
        weather_info = 'beach_' + keyword_weather
    video_folder_path = os.path.join(video_root_folder_path, keyword_data + '_' + weather_info, f'{keyword_hight}m', keyword_info)#视频的父目录
    
    #print(type(keyword_frame))
    #pattern = r'.*{}.*\.MP4'.format(target_info)
    if int(keyword_frame) > 19999 or keyword_data == '20230907' or target_info == '20230922180327' or target_info == '20230913150639':#这些是没有测距信息的视频
        print("skip!")#!!!!!!!这里应该对加图，跳过ocr环节，之后记得加上
        data={'jpg_filename': input_image_filename, '角度': 'NONE', '测距(m)': 'NONE'}
        formatted_text = "jpg_filename: {},  角度: NONE, 测距(m): NONE".format(input_image_filename)
        print(formatted_text)
        sheet.append(list(data.values()))
        workbook.save('ALL_Laser_distance_measurement.xlsx')
        print("****************************************************************************")
    else:
        #print(video_folder_path)
        for filename in os.listdir(video_folder_path):
           # print(filename)
            # 使用正则表达式检查文件名是否匹配目标模式
            if re.match( r'.*{}.*\.MP4'.format(target_info), filename) and filename.endswith('_U.MP4'):  #_U.MP4
                video_path = os.path.join(video_folder_path, filename)
                print(video_path)
        video_filename = os.path.basename(video_path)      
        print(video_filename)
        sum_Z_frame = int(keyword_frame)
        #print("zheliygshi3720",sum_Z_frame)
        the_searched_Z_video_name = 'DJI_' + f'{target_info}' + f'_00{keyword_index}' + '_T.MP4'
        the_searched_Z_video_path = os.path.join(video_folder_path, the_searched_Z_video_name)
        cap0 = cv2.VideoCapture(the_searched_Z_video_path)#打开同名Z视频本身  这里该输入Z了
        print(the_searched_Z_video_path)
        total_Z_frames = 0#int(cap0.get(cv2.CAP_PROP_FRAME_COUNT))
        #print('zheliygshiyaozhaodeZspzongshenshu',total_Z_frames)
        num_connected = int((len(video_filename)-26)/5)
        #print(num_connected)
        split_name = video_filename.split("_")
        the_first_connected = int(split_name[2])
        the_final_connected = int(re.search(r'_00(\d{2})_R', video_filename).group(1))#100 
        print('first',the_first_connected)
        print('last conn',the_final_connected)
        print('zheli')
        if int(keyword_index) > the_first_connected:
            for i in range(the_first_connected,int(keyword_index)):
                print('第{i}个相关视频')
                if i < 10:
                    the_connected_video_filename = 'DJI_' + f'{target_info}' + '_' + f'000{i}' + '_T.MP4'
                else:
                    the_connected_video_filename = 'DJI_' + f'{target_info}'+ '_' + f'00{i}' + '_T.MP4'
                the_connected_video_path = os.path.join(video_folder_path, the_connected_video_filename)
                print(the_connected_video_path)
                cap1 = cv2.VideoCapture(the_connected_video_path) #打开各个相关Z视频
                print('第{}个相关视频的帧数为{}',i,int(cap1.get(cv2.CAP_PROP_FRAME_COUNT)))
                sum_Z_frame = sum_Z_frame + int(cap1.get(cv2.CAP_PROP_FRAME_COUNT)) #这里是同一个录屏文件下，keyword_index之前的视频帧加识别到的现有帧 14035
            print('SUM_Z',sum_Z_frame)
            for i in range(the_first_connected,the_final_connected + 1):
                if i < 10:
                    the_connected_video_filename = 'DJI_' + f'{target_info}' + '_' + f'000{i}' + '_T.MP4'
                else:
                    the_connected_video_filename = 'DJI_' + f'{target_info}'+ '_' + f'00{i}' + '_T.MP4'
                the_connected_video_path = os.path.join(video_folder_path, the_connected_video_filename)
                print(the_connected_video_path)
                cap1 = cv2.VideoCapture(the_connected_video_path) #打开各个相关Z视频
                total_Z_frames = total_Z_frames + int(cap1.get(cv2.CAP_PROP_FRAME_COUNT)) 
            print('TOTAL_Z',total_Z_frames)
        elif int(keyword_index) == the_first_connected:
            if int(keyword_index) < 10:
                the_connected_video_filename = 'DJI_' + f'{target_info}' + '_' + f'000{int(keyword_index)}' + '_T.MP4'
            else:
                the_connected_video_filename = 'DJI_' + f'{target_info}'+ '_' + f'00{int(keyword_index)}' + '_T.MP4'
            the_connected_video_path = os.path.join(video_folder_path, the_connected_video_filename)
            print(the_connected_video_path)
            cap1 = cv2.VideoCapture(the_connected_video_path) #打开各个相关Z视频
            sum_Z_frame = sum_Z_frame
            for i in range(the_first_connected,the_final_connected + 1):
                if i < 10:
                    the_connected_video_filename = 'DJI_' + f'{target_info}' + '_' + f'000{i}' + '_T.MP4'
                else:
                    the_connected_video_filename = 'DJI_' + f'{target_info}'+ '_' + f'00{i}' + '_T.MP4'
                the_connected_video_path = os.path.join(video_folder_path, the_connected_video_filename)
                print(the_connected_video_path)
                cap1 = cv2.VideoCapture(the_connected_video_path) #打开各个相关Z视频
                total_Z_frames = total_Z_frames + int(cap1.get(cv2.CAP_PROP_FRAME_COUNT)) 
            #total_Z_frames = total_Z_frames
            print('SUM_Z',sum_Z_frame)
            print('TOTAL_Z',total_Z_frames)
        
        cap = cv2.VideoCapture(video_path)#打开R视频
        if not cap.isOpened():
            print("Error: 无法打开视频文件.")
            exit()
        total_R_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        tran_sum_R_frame = int(sum_Z_frame * total_R_frames/total_Z_frames)#这里按理来说就是input_image在R视频中的帧数
        #tran_sum_R_frame = sum_Z_frame
        print(tran_sum_R_frame)
        # print('total_R',total_R_frames)
        # print('total_Z',total_Z_frames)
        # print('SUM_Z',sum_Z_frame)
        # print(tran_sum_R_frame)
    #b)以下为读取指定帧并识别
    # 感兴趣区域的坐标和尺寸 (x, y, width, height)

    # the_real_frame = keyword_frame * 
        #total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        #print("Total frames in the video:", total_R_frames)
        reader = easyocr.Reader(['ch_sim','en'],gpu = True)# 初始化EasyOCR对象
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, tran_sum_R_frame - 1)#设置帧号
        ret, frame = cap.read()
        if ret:
            saved_jpg_path = '/data3/X_Images/xuxiaoran/ocr/saved_jpg_sin'
            wanted = f'{count}_frame_{keyword_frame}.jpg'  # 保存的文件名
            cv2.imwrite(os.path.join(saved_jpg_path,wanted), frame)
            print(f'帧已保存为 {wanted}.')
            # saved_jpg_num = glob.glob(os.path.join(folder_path, "*.jpg"))
            # number_of_jpg_files = len(saved_jpg_num)
            # print(f'已处理{number_of_jpg_files}个数据库中的数据')
        else:
            print("error")
            
            
        #准备识别！！！！
        roi_x, roi_y, roi_width, roi_height = 512, 583, 27, 19
        roi_X, roi_Y, roi_WD, roi_HT = 1226,289,20,20
        roi_red = frame[roi_Y:roi_Y + roi_HT, roi_X:roi_X + roi_WD]
        red_pixels = roi_red[(roi_red[:, :, 2] > 100) & (roi_red[:, :, 1] < 100) & (roi_red[:, :, 0] < 100)]
        roi = frame[roi_y:roi_y + roi_height, roi_x:roi_x + roi_width]
        enhanced_roi = pic_pre_process(roi)
        results = reader.readtext(enhanced_roi)
        recognized_text = ""
        height = int(keyword_hight)
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
                recognized_text = 'error!'
                #     if previous_text != "NONE":
                #         last_not_none_text = previous_text
            print("recongized",recognized_text.strip())
            #  print("last not none",last_not_none_text.strip())
            if re.match(r'^-?\d+$', recognized_text.strip()):
                #if abs(int(recognized_text.strip()) - int(previous_text.strip())) >= 10:
                angle_radians = math.radians(int(recognized_text.strip()))
                height = float(height)
                angle = float(angle_radians)
                sin_value = math.sin(angle)
                distance = abs(height / sin_value) #abs!!
                print(distance)
            # elif re.match(r'^-?\d+$', recognized_text.strip()):
            #     recognized_text = recognized_text
            #     angle_radians = math.radians(int(recognized_text.strip()))
            #     height = float(height)
            #     angle = float(angle_radians)
            #     cos_value = math.cos(angle)
            #     distance = height / cos_value
            #     print(distance)
            # elif re.match(r'^-?\d+$', recognized_text.strip()) == 0:
            #     recognized_text = "NONE"
            #     distance = "NONE"
        else:
            recognized_text = "切换界面情况"
            distance = "切换界面情况"
        
        #data.append({'jpg_filename': input_image_filename, '角度': recognized_text.strip(), '测距(m)': distance})
        data = {'jpg_filename': input_image_filename, '角度': recognized_text.strip(), '测距(m)': distance}
        formatted_text = "jpg_filename: {},  角度: {}, 测距(m): {}".format(input_image_filename, recognized_text.strip(), distance)
        print(formatted_text)
        sheet.append(list(data.values()))
        workbook.save('ALL_sin_Laser_distance_measurement.xlsx')
        print("****************************************************************************")
