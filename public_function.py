# -*- coding: utf-8 -*-
import os


# IP地址校验
def validate_ip(ip_str):
    sep = ip_str.split('.')
    if len(sep) != 4:
        return False
    for i,x in enumerate(sep):
        try:
            int_x = int(x)
            if int_x < 0 or int_x > 255:
                return False
        except ValueError as e:
            return False
    return True

# 获取指定列每行单元格的值
def getColValues(read,column):
    rows = read.max_row
    columndata=[]
    for i in range(1,rows+1):
        cellvalue = read.cell(row=i,column=column).value
        columndata.append(cellvalue)
    return columndata

# 函数-将文件按照生成时间排序
def sort_file_by_time(file_path):
    files = os.listdir(file_path)
    if not files:
        return
    else:
        files = sorted(files, key=lambda x: os.path.getmtime(
            os.path.join(file_path, x)))  # 格式解释:对files进行排序.x是files的元素,:后面的是排序的依据.  x只是文件名,所以要带上join.
        files.reverse()
        return files