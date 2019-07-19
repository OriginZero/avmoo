import os
from shutil import move as move_file
import requests
from lxml import etree


main_url = 'https://javzoo.com/cn/search/{0}'

path = r'E:\新建文件夹\temp'

video_extension_list = ['.wmv', '.rmvb', '.mov', '.avi', '.mp4', '.mkv']


def downloadHtml(url):
    """
        下载网页

        url: 下载链接

        return: 返回下载的html字符串数据

        下载错误将抛出异常
    """
    header = {
        'cache-control': 'no-cache',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
    }
    try:
        r = requests.get(url, headers=header)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text
    except Exception as e:
        print(e)


def findAllVideo(path, find_subfolder=False):
    """
        查找文件夹内所有视频文件

        path: 目标目录

        find_subfolder: 查找子文件夹，默认False不开启，功能未实现  可用闭包函数+递归实现

        return: 返回所有找到的视频文件的字典
    """

    video_info = {}
    # 视频集合
    all_video_list = set()
    # 子文件夹集合
    all_dir = set()
    # 返回完整路径列表
    # temp_list = [os.path.join(path, _) for _ in os.listdir(path)]
    temp_list = os.listdir(path)

    for _ in temp_list:
        # 判断路径是否是视频文件
        if (os.path.splitext(_)[1]).lower() in video_extension_list:
            all_video_list.add(_)
        # 判断是否为文件夹
        elif os.path.isdir(_):
            all_dir.add(_)
        # 忽略其他
        else:
            pass

    video_info['path'] = path
    video_info['video'] = all_video_list
    return video_info


def videoActor(video_name):
    def findVideo(video_name):
        """
            通过视频名返回avmoo视频详细url
        """
        pass

    def parserVideoInfo(url):
        """
            解析url，返回番号信息
        """
        pass


def operationalVideo(video_path, video_name, video_actor):
    new_dir = os.path.join(video_path, video_actor)
    try:
        os.mkdir(new_dir)
        move_file(os.path.join(video_path, video_name),
                  os.path.join(new_dir, video_name))
    except FileExistsError as e:
        move_file(os.path.join(video_path, video_name),
                  os.path.join(new_dir, video_name))
    print('\t{}\tOK...'.format(video_name))

    # if not os.path.exists(new_dir):
    #     os.mkdir(new_dir)
    #     # moveVideoFolder()
    #     move_file(os.path.join(video_path, video_name),
    #               os.path.join(new_dir, video_name))
    #     pass
    # elif os.path.exists(new_dir):
    #     move_file(os.path.join(video_path, video_name),
    #               os.path.join(new_dir, video_name))
    #     pass
    # else:
    #     print('{}--{}--{}'.format(video_path, video_name, video_actor))
    #     raise Exception


def main():
    video_info = findAllVideo(path)
    for _ in video_info['video']:
        video_name = os.path.splitext(_)[0]
        url_temp = main_url.format(video_name)
        temp = downloadHtml(url_temp)
        print('\t{}\toperating...'.format(video_name))
        a_selector = etree.HTML(temp).xpath('//a[@class="movie-box"]')
        info_url = a_selector[0].attrib['href']

        try:
            actor_name = etree.HTML(downloadHtml(info_url)).xpath(
                '//div[@id="avatar-waterfall"]/a/span')[0].text
            operationalVideo(video_info['path'], _, actor_name)
        except IndexError as e:
            operationalVideo(video_info['path'], _, 'other')

        # video_name = a_selector[0].xpath('div[@class="photo-info"]//date')[0].text

        # if len(a_selector) == 1:
        #     pass
        # else:
        #     pass

        # selector = etree.HTML(temp).xpath(
        #     '//div[@id="waterfall"]/div[@class="item"]/a')
        # for sub in selector:
        #     if video_name == sub.xpath('div[@class="photo-info"]/span/date')[0].text:
        #         url = sub.xpath('@href')[0]
        #         temp = downloadHtml(url)
        #         actor_name = etree.HTML(temp).xpath(
        #             '//div[@id="avatar-waterfall"]/a/span')[0].text
        #         operationalVideo(video_info['path'], video_name, actor_name)
        #     else:
        #         print(sub.xpath('@href')[0])


if __name__ == "__main__":
    main()
