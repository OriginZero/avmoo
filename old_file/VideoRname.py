# 正则表达式 \w{3,4}(-|_|)\d{3,4}
import os
import re

regex = re.compile('([A-Za-z]{3,4})(-|_)(\d{3,4})')


def ReFileName(file_path, old_name):
    temp = regex.search(old_name)
    if temp:
        file_name = temp.group(0).upper()
        file_extension = old_name.split('.')[-1]
        new_name = file_name+'.'+file_extension
        try:
            os.rename(os.path.join(file_path, old_name),
                      os.path.join(file_path, new_name))
            print('文件 {}\t重命名成 {}\t成功.'.format(old_name, new_name))
        except Exception as e:
            print('重命名成 \t{} 失败，具体原因：\t{}'.format(new_name, e))


# ReFileName(os.path.join(
#     abs_path, '[ThZu.Cc]rbd-917.mp4'), os.path.join(abs_path, 'rbd-917.mp4'))

def FindPathList(path, find_all=False):
    """
        path: 文件路径

        find_all: 检索子文件夹, 默认为False不进行检索

        return: 
    """
    dir_list = os.listdir(path)
    for _ in dir_list:
        temp_path = os.path.join(path, _)
        if os.path.isfile(temp_path):
            ReFileName(path, _)
        elif find_all == False:
            continue
        elif os.path.isdir(temp_path):
            print('\n\n开始检索子文件夹：\n{}\n{}'.format(_, temp_path))
            FindPathList(temp_path, True)
        else:
            print(_)


def main():
    path = input('输入重命名的路径：\n')
    if os.path.isdir(path):
        FindPathList(path, False)
    else:
        print('路径不合法...')


if __name__ == '__main__':
    while(True):
        main()
