import os
import json
import cv2
import numpy as np
image_folder = './jpg_files'
json_folder = './json_files'
output_folder = './jpg_with_json'
os.makedirs(output_folder, exist_ok=True)

for json_filename in os.listdir(json_folder):
    if json_filename.endswith('.json'):
        json_path = os.path.join(json_folder, json_filename)
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        image_filename = data.get('imagePath', '')
        jpg_path = os.path.join(image_folder, image_filename)
        if os.path.exists(jpg_path):
            image = cv2.imread(jpg_path)
            for shape in data['shapes']:
                points = shape['points']
                # 提取矩形左上角和右下角坐标
                x1, y1 = min(points[0][0], points[1][0]), min(points[0][1], points[1][1])
                x2, y2 = max(points[0][0], points[1][0]), max(points[0][1], points[1][1])
                color = (0, 255, 0)
                thickness = 2
                # 绘制矩形框
                image = cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), color, thickness)
                
                label = shape['label']
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                font_thickness = 1
                text_x = int(x1)
                text_y = int(y1) - 5
                cv2.putText(image, label, (text_x, text_y), font, font_scale, color, font_thickness)
            
            output_path = os.path.join(output_folder, image_filename)
            cv2.imwrite(output_path, image)
            print(f'Saved annotated image with bounding boxes to {output_path}')
        else:
            print(f'Image corresponding to {json_filename} not found in {image_folder}')
