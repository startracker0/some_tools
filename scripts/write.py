import pandas as pd

# 读取xlsx文件
df = pd.read_excel('distance_measurement.xlsx')

# 遍历每一行，生成txt文件
for index, row in df.iterrows():
    txt_filename = str(row['jpg_filename']).replace('.jpg','.txt')  # 第一列作为txt文件名
    txt_content =str(row['测距(m)'])  # 第二列和第三列作为txt文件的内容
    
    # 写入txt文件
    with open(txt_filename, 'w') as txt_file:
        txt_file.write(txt_content)

print("Txt files created successfully.")
