import pandas as pd
import math

# 读取Excel文件
df = pd.read_excel('ALL_Laser_distance_measurement.xlsx', header=None)

# 计算第三列数值除以第二列数字的tan，并将结果写入第四列
for i in range(df.shape[0]):
    
    if df.iloc[i, 1] == 'NONE':
        print('skip')
        value_to_assign = 'NONE'
    else:
        angle = float(df.iloc[i, 1])  # 将角度列转换为浮点数
        height = float(df.iloc[i, 2])
        if angle == -90 or angle == 0:
            print('skip')
        else:  
            value_to_assign =  abs(height/math.tan(math.radians(angle)))
           # df.at[i, 3] = value_to_assign
        print(i)
    df.at[i, 3] = value_to_assign
       

# 保存修改后的数据到新的Excel文件
df.to_excel('modified_data.xlsx', index=False, header=False,float_format='%s')
