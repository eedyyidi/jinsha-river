from mintpy.utils import isce_utils
import os
from mintpy.utils import utils as ut

# 初始SLC的路径
SLC_dir = '../../s1_a099/merged/SLC/'

# 获取所有日期
dates = []
for folder_name in os.listdir(SLC_dir):
    folder_path = os.path.join(SLC_dir, folder_name)
    if os.path.isdir(folder_path):
        # 检查文件夹是否为空
        if os.listdir(folder_path):
            try:
                date = folder_name.strip()[:8]  # 提取前8个字符作为日期（YYYYMMDD）
                dates.append(date)
            except IndexError:
                pass
dates = sorted(dates)
print(dates)

## slc_file---初始slc的文件位置
slc_file = []
for date in dates:
    file_path = os.path.join(SLC_dir, date, f'{date}.slc.full')
    slc_file.append(file_path)

## sub_slc_file---裁剪的要处理的slc的文件位置
sub_SLC_dir = './sub_SLC/'
sub_slc_file = []
for date in dates:
    file_path = os.path.join(sub_SLC_dir, date, f'{date}.slc.full')
    sub_slc_file.append(file_path)

############################################裁剪slc############################################使用并行处理
num_cores, _, Parallel, delayed = ut.check_parallel(len(sub_slc_file))
Parallel(n_jobs=num_cores)(delayed(isce_utils.crop_slc)(file, sub_file, x0=63000, y0=15000, x1=65700, y1=15900) for file, sub_file in zip(slc_file, sub_slc_file))
############################################裁剪slc############################################使用并行处理


## 生成干涉图的文件位置
interferograms_dir = './interferograms/'
all_pairs = []  ## 干涉时间，例如20210202_20220202
for i in range(len(dates)):
    for j in range(i + 1, len(dates)):
        pair = f"{dates[i]}_{dates[j]}"
        all_pairs.append(pair)

int_file = []   ## 干涉图，例如./s1_a026/interferograms/20141019_20230517/20141019_20230517.int
for all_pair in all_pairs:
    file_path = os.path.join(interferograms_dir, all_pair, f'{all_pair}.int')
    int_file.append(file_path)

slc_1s = []  ## 干涉时间1，例如20210202
slc_2s = []  ## 干涉时间2，例如20210202
for pair in all_pairs:
    date1, date2 = pair.split('_')
    slc_1s.append(date1)
    slc_2s.append(date2)

## sub_slc_file1，sub_slc_file2---用于干涉的两个slc的位置
sub_SLC_dir = './sub_SLC/'
sub_slc_file1 = [] ## slc1的位置，例如./s1_a026/sub_SLC/20141019/20141019.slc.full
for slc_1 in slc_1s:
    file_path = os.path.join(sub_SLC_dir, slc_1, f'{slc_1}.slc.full')
    sub_slc_file1.append(file_path)

sub_slc_file2 = [] ## slc2的位置，例如./s1_a026/sub_SLC/20141019/20141019.slc.full
for slc_2 in slc_2s:
    file_path = os.path.join(sub_SLC_dir, slc_2, f'{slc_2}.slc.full')
    sub_slc_file2.append(file_path)

## 生成干涉图
def generate_interferogram(int_name, sub_slc1, sub_slc2):
    isce_utils.form_ifgram(sub_slc1, sub_slc2, int_name, rg_look=9, az_look=3)

############################################生成干涉图############################################## 使用并行处理
num_cores, _, Parallel, delayed = ut.check_parallel(len(int_file))
Parallel(n_jobs=num_cores)(delayed(generate_interferogram)(int_name, sub_slc1, sub_slc2) for int_name, sub_slc1, sub_slc2 in zip(int_file, sub_slc_file1, sub_slc_file2))
############################################生成干涉图############################################使用并行处理


## 干涉图滤波
filt_file = []   ## 干涉图，例如./s1_a026/interferograms/20141019_20230517/20141019_20230517_filt.int
for all_pair in all_pairs:
    file_path = os.path.join(interferograms_dir, all_pair, f'{all_pair}_filt.int')
    filt_file.append(file_path)

## 干涉图滤波
def filter_interferogram(int_name, filt_name):
    isce_utils.filter_goldstein(int_name, filt_name, filt_strength=0.8)

############################################干涉图滤波############################################## 使用并行处理
num_cores, _, Parallel, delayed = ut.check_parallel(len(filt_file))
Parallel(n_jobs=num_cores)(delayed(filter_interferogram)(int_name, filt_name) for int_name, filt_name in zip(int_file, filt_file))
############################################干涉图滤波############################################ 使用并行处理

## 相干性计算
cor_file = [] ## 干涉图，例如./s1_a026/interferograms/20141019_20230517/20141019_20230517_filt.cor
for all_pair in all_pairs:
    file_path = os.path.join(interferograms_dir, all_pair, f'{all_pair}_filt.cor')
    cor_file.append(file_path)

## 相干性计算
def calculate_coherence(filt_name, cor_name):
    isce_utils.estimate_coherence(filt_name, cor_name)

############################################相干性计算############################################## 使用并行处理
num_cores, _, Parallel, delayed = ut.check_parallel(len(cor_file))
Parallel(n_jobs=num_cores)(delayed(calculate_coherence)(filt_name, cor_name) for filt_name, cor_name in zip(filt_file, cor_file))
############################################相干性计算############################################ 使用并行处理

