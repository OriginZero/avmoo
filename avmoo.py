import os
import re
import requests
import json
from time import time
from lxml import etree
from multiprocessing import Pool
from shutil import move as move_file

# 匹配
# Actresses(.|\n)+?</dd>


class JavTool:
    __slots__ = ('_videosuffix', '_regex', '_headers', '_payload',
                 '_search_url', 'work_path')

    def __init__(self, work_path):
        if os.path.isdir(work_path):
            self.work_path = work_path
        else:
            raise OSError('无法找到改路径或路径不合法.')

        self._videosuffix = ['.wmv', '.rmvb', '.mov', '.avi', '.mp4', '.mkv']
        self._regex = re.compile('([A-Za-z]{3,4})(-|_)(\d{3})')
        self._payload={
            'username': 'admin',
            'password': 'admin123'
        }
        self._headers = {
            'Host': 'www.libredmm.com',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
        }
        # self._search_url = 'https://javzoo.com/cn/search/{0}'
        self._search_url = 'https://www.libredmm.com/movies/{0}'

    def moveVideo(self, video_path, video_name, video_actor):
        new_dir = os.path.join(video_path, video_actor)
        try:
            os.mkdir(new_dir)
            move_file(os.path.join(video_path, video_name),
                      os.path.join(new_dir, video_name))
        except FileExistsError as e:
            move_file(os.path.join(video_path, video_name),
                      os.path.join(new_dir, video_name))
        print('{}\tMOVE\tOK'.format(video_name))

    def classIfy(self, video_name):

        # video_name = 'NNPJ-326'
        # 下载
        def downHtml(url):
            try:
                r = requests.get(url, headers=self._headers, data=self._payload)
                r.raise_for_status
                r.encoding = 'utf-8'
                return r.text
            except Exception as e:
                print(e)

        # 解析搜索页面
        def parserSearch(search_html):
            """
                search_html: 参数 搜索 页面HTML

                返回值 详细信息URL
                other 网络原因或没有找到结果
            """
            if not search_html:
                raise Exception('未返回数据')
            try:
                temp_HTML = etree.HTML(search_html)
                selector = temp_HTML.xpath('//a[@class="movie-box"]')
                return selector[0].attrib['href']
            except IndexError:
                print('未查询到视频信息...')

        # 解析信息页面
        def parserInfo(info_html):
            """
                info_html: 参数 详细信息 页面HTML

                返回值 出演人员
                double 代表多位
                null 代表无
            """
            try:
                names = etree.HTML(info_html).xpath('//div[@class="card actress"]//h6[@class="card-title"]//a/text()')
                if len(names) == 1:
                    return names[0]
                if len(names) > 1:
                    return 'double'
                return 'null'
            except Exception as e:
                print('parse info error {}'.format(e))
                return 'error'

        print('查找{}中...'.format(video_name))
        search_url = self._search_url.format(os.path.splitext(video_name)[0])
        """
        info_url = parserSearch(downHtml(search_url))
        # 多
        # video_actor = parserInfo(downHtml('https://javzoo.com/cn/movie/66gc'))
        # 单
        # video_actor = parserInfo(downHtml('https://javzoo.com/cn/movie/74rp'))
        # 无
        # video_actor = parserInfo(downHtml('https://javzoo.com/cn/movie/6yy5'))
        video_actor = parserInfo(downHtml(info_url))
        """
        # video_actor = parserJson(downHtml(search_url))
        video_actor = parserInfo(downHtml(search_url))
        self.moveVideo(self.work_path, video_name, video_actor)

    def findAllVideo(self, path, find_subfolder=False):
        """
            查找文件夹内所有视频文件

            path: 目标目录

            find_subfolder: 查找子文件夹，默认False不开启，功能未实现  可用闭包函数+递归实现

            return: 返回所有找到的视频文件的字典
        """

        all_video_list = []
        # 返回完整路径列表
        # temp_list = [os.path.join(path, _) for _ in os.listdir(path)]
        temp_list = os.listdir(path)

        for _ in temp_list:
            # 判断路径是否是视频文件
            if (os.path.splitext(_)[1]).lower() in self._videosuffix:
                all_video_list.append(_)

        return all_video_list

    def reVideoName(self, file_path, old_name):
        """
            file_path: 文件所在文件夹

            old_name: 原有文件名
        """
        process_name = old_name.replace('1080p', '').replace(
            '720p', '').replace('FOW-', '')
        if self._regex.search(process_name):
            temp = self._regex.search(old_name)
            if temp:
                file_name = temp.group(0).upper()
                file_extension = old_name.split('.')[-1]
                new_name = file_name+'.'+file_extension
                try:
                    os.rename(os.path.join(file_path, old_name),
                              os.path.join(file_path, new_name))
                    print('重命名后：{}\t\t原始文件名：{}'.format(new_name,old_name))
                except Exception as e:
                    print('{}\n失败, 具体原因：\t{}'.format(new_name, e))
        else:
            self.moveVideo(file_path, old_name, 'no')

    def run(self, classify=True):
        """
            work_path: 需要操作的目录

            classify:
                Flase只进行重命名
                True重命名后按出演人员排序
        """
        try:
            video_dict = self.findAllVideo(self.work_path)
            if not video_dict:
                raise FileNotFoundError
            for video_name in video_dict:
                self.reVideoName(self.work_path, video_name)
            if classify:
                # 文件名发生变化 重新获取
                video_dict = self.findAllVideo(self.work_path)

                with Pool(8) as p:
                    p.map(self.classIfy, video_dict)
                # for video_name in video_dict:
                #     self.classIfy(video_name)
        except FileNotFoundError:
            print('没有找到视频文件.')


if __name__ == "__main__":
    start = time()
    jav = JavTool(input('输入文件夹地址:\n'))
    jav.run(True)
    end = time()
    print('总耗时:%fs' % (end-start))
