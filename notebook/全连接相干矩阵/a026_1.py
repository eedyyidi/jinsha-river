from mintpy.utils import isce_utils
import os

##初始SLC的路径
SLC_dir = '../../s1_a026/merged/SLC/'

##所有时间dates
dates = []         
for folder_name in os.listdir(SLC_dir):
    folder_path = os.path.join(SLC_dir, folder_name)
    if os.path.isdir(folder_path):
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

############################################裁剪slc############################################
for i, file_name in enumerate(slc_file):
    sub_slc_file[i] = isce_utils.crop_slc(file_name, sub_slc_file[i], x0=16983, y0=6660, x1=19683, y1=7560)
############################################裁剪slc############################################


## int_file---生成干涉图的文件位置
interferograms_dir = './interferograms/'
all_pairs = []  ##干涉时间，例如20210202_20220202
for i in range(len(dates)):
    for j in range(i + 1, len(dates)):
        pair = f"{dates[i]}_{dates[j]}"
        all_pairs.append(pair)

int_file = []   ##干涉图，例如./s1_a026/interferograms/20141019_20230517/20141019_20230517.int
for all_pair in all_pairs:
    file_path = os.path.join(interferograms_dir, all_pair, f'{all_pair}.int')
    int_file.append(file_path)

slc_1s = []  ##干涉时间1，例如20210202
slc_2s = []  ##干涉时间2，例如20210202
for pair in all_pairs:
    date1, date2 = pair.split('_')
    slc_1s.append(date1)
    slc_2s.append(date2)

## sub_slc_file1，sub_slc_file2---用于干涉的两个slc的位置
sub_SLC_dir = './sub_SLC/'
sub_slc_file1 = [] ##slc1的位置，例如./s1_a026/sub_SLC/20141019/20141019.slc.full
for slc_1 in slc_1s:
    file_path = os.path.join(sub_SLC_dir, slc_1, f'{slc_1}.slc.full')
    sub_slc_file1.append(file_path)

sub_slc_file2 = [] ##slc2的位置，例如./s1_a026/sub_SLC/20141019/20141019.slc.full
for slc_2 in slc_2s:
    file_path = os.path.join(sub_SLC_dir, slc_2, f'{slc_2}.slc.full')
    sub_slc_file2.append(file_path)

############################################生成干涉图############################################
for i, int_name in enumerate(int_file):
    sub_int_file = isce_utils.form_ifgram(sub_slc_file1[i], sub_slc_file2[i], int_name, rg_look=9, az_look=3)
############################################生成干涉图############################################

## filt_file--滤波后的干涉图
filt_file = []   ##干涉图，例如./s1_a026/interferograms/20141019_20230517/20141019_20230517_filt.int
for all_pair in all_pairs:
    file_path = os.path.join(interferograms_dir, all_pair, f'{all_pair}_filt.int')
    filt_file.append(file_path)

############################################干涉图滤波############################################
for i, int_name in enumerate(int_file):
    filt_milt_int_file = isce_utils.filter_goldstein(int_name, filt_file[i], filt_strength=0.8)
############################################干涉图滤波############################################

## cor_file--相干性计算
cor_file = [] ##干涉图，例如./s1_a026/interferograms/20141019_20230517/20141019_20230517_filt.cor
for all_pair in all_pairs:
    file_path = os.path.join(interferograms_dir, all_pair, f'{all_pair}_filt.cor')
    cor_file.append(file_path)
    
############################################相干性计算############################################
for i, file_name in enumerate(filt_file):
    cor_filt_milt_int_file = isce_utils.estimate_coherence(file_name, cor_file[i])
############################################相干性计算############################################







