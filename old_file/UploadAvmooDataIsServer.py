import os
import requests
import time
from random import randint
from lxml import etree
from bs4 import BeautifulSoup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luluguan.settings')
import django

django.setup()

from mainweb.models import AVid, AVtype, AVmanufacturer, AVperformer

main_url = 'https://avmoo.net/cn/released/page/'

# con_db = pymysql.Connect(host='111.231.204.86', port=3306,
#                          user='zero', passwd='zerozero', db='luluguan', charset='UTF8')
# db_mysql = con_db.cursor()


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
    'Referer': 'https://avmoo.net/cn',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
}


def AddDjangoDatabase(av_info):

    if av_info:
        if isinstance(av_info, dict):
            try:
                av_manufacturer_temp = AVmanufacturer.objects.get_or_create(
                    av_manufacturer=av_info['av_manufacturer'])[0]
                print('*向数据库添加:\n 番号:%s \n 视频:%s \n 发行商:%s \n' %
                      (av_info['av_id'], av_info['av_video_name'], av_manufacturer_temp))

                temp = AVid.objects.get_or_create(
                    av_id=av_info['av_id'], av_video_name=av_info['av_video_name'], av_release_time=av_info['av_release_time'], av_poster=av_info['av_poster'], av_big_img=av_info['av_big_img'], av_movie_time=av_info['av_movie_time'], av_manufacturer=av_manufacturer_temp)[0]

                # --------------------------------------------------

                print('*向数据库添加视频女优:')
                performer_list = []
                for i in zip(av_info['av_performer'], av_info['av_performer_avatar']):
                    print(i[0])
                    performer_list.append(AVperformer.objects.get_or_create(
                        av_name=i[0], av_performer_avatar=i[1])[0])
                temp.av_performer.set(performer_list)

                # --------------------------------------------------

                print('*向数据库添加视频类别:')
                type_temp_list = []
                for i in av_info['type_list']:
                    print(i)
                    type_temp_list.append(
                        AVtype.objects.get_or_create(type_name=i)[0])
                temp.av_type.set(type_temp_list)

                print('*数据库创建正常')
            except Exception as e:
                print('----------添加----------')
                print(e)
                print('----------错误----------')


def DownHTML(url):
    try:
        time.sleep(randint(0, 2))
        r = requests.get(url, headers=headers)
        r.raise_for_status
        r.encoding = 'utf-8'
        print(r.status_code)
        return r.text
    except Exception as e:
        print("错误信息如下：")
        print(e)


def HTMLAnalysis(html_text):
    # 解析详细信息
    def GetMoveInfo(url):
        av_maininfo_list = []
        av_type_list = []
        av_previews_list = []
        av_humbnails_list = []
        av_performer = []
        av_performer_avatar = []

        html_temp = DownHTML(url)
        bs = BeautifulSoup(html_temp, 'html.parser')
        # 海报
        av_big_img = bs.find('a', {'class': {'bigImage'}}).attrs['href']
        # 视频时间
        av_movie_time = bs.find('div', {'class': {'row movie'}}).findAll('p')[
            2].contents[1]
        # 发行商
        av_manufacturer = bs.find('div', {'class': {'row movie'}}).findAll('div')[1].findAll(
            'p', class_='header')[1].next_sibling.next_sibling.find_all('a')[0].text
        # 类别s
        type_list = bs.find('div', {'class': {'row movie'}}).findAll(
            'span', {'class': {'genre'}})
        for type in type_list:
            av_type_list.append(type.text)

        try:
            # # 女优名
            # av_performer = bs.find(
            #     'div', id='avatar-waterfall').find('span').text
            # # 女优头像
            # av_performer_avatar = bs.find(
            #     'div', id='avatar-waterfall').find('img').attrs['src']

            # 女优名
            av_performer_info = bs.find(
                'div', id='avatar-waterfall').findAll('a', class_='avatar-box')
            # 女优头像
            for i in av_performer_info:
                av_performer.append(i.find('span').text)
                av_performer_avatar.append(i.find('img').attrs['src'])

        except Exception as e_performer_info:
            print(e_performer_info)
            print('出演人员未知...')

        try:
            # 预览图
            av_previews = bs.find(
                'div', id='sample-waterfall').findAll('a', class_='sample-box')
            # 略缩图
            av_humbnails = bs.find(
                'div', id='sample-waterfall').findAll('img')
            for previews, humbnails in zip(av_previews, av_humbnails):
                av_previews_list.append(previews.attrs['href'])
                av_humbnails_list.append(humbnails.attrs['src'])
        except Exception as e_img_info:
            print(e_img_info)
            print('预览图暂无...')
        av_maininfo_list.append(av_big_img)
        av_maininfo_list.append(av_movie_time)
        av_maininfo_list.append(av_manufacturer)
        av_maininfo_list.append(av_performer)
        av_maininfo_list.append(av_performer_avatar)
        av_maininfo_list.append(av_type_list)
        av_maininfo_list.append(av_previews_list)
        av_maininfo_list.append(av_humbnails_list)
        return av_maininfo_list

    # 解析简单信息
    if html_text:
        items = etree.HTML(html_text).xpath(
            '//div[@id="waterfall"]/div[@class="item"]')
        for item in items:
            av_info = {}
            # 详情url
            url = item.xpath('a/@href')[0]
            # https://avmoo.net/cn/movie/6txc
            # url = 'https://avmoo.net/cn/movie/6txc'
            print(url)
            # 封面
            av_poster = item.xpath(
                'a/div[@class="photo-frame"]/img/@src')[0]
            # av名称
            av_name = item.xpath('a/div[@class="photo-info"]/span')[0].text
            # 番号
            av_id = item.xpath(
                'a/div[@classC="photo-info"]/span/date')[0].text
            # 发行时间
            av_release_time = item.xpath(
                'a/div[@class="photo-info"]/span/date')[1].text

            # 番号
            av_info['av_id'] = av_id
            # 视频名
            av_info['av_video_name'] = av_name
            # 发行时间
            av_info['av_release_time'] = av_release_time
            # 视频封面
            av_info['av_poster'] = av_poster
            infos = GetMoveInfo(url)
            # 视频海报
            av_info['av_big_img'] = infos[0]
            # 视频长度
            av_info['av_movie_time'] = infos[1]
            # 发行商
            av_info['av_manufacturer'] = infos[2]
            # 女优名
            av_info['av_performer'] = infos[3]
            # 女优头像
            av_info['av_performer_avatar'] = infos[4]
            # 视频类型 list
            av_info['type_list'] = infos[5]
            # 视频预览图 list
            av_info['av_previews'] = infos[6]
            # 视频略缩图 list
            av_info['av_humbnails'] = infos[7]

            # print(av_info)
            # UploadServer(av_info)
            AddDjangoDatabase(av_info)


def SpiderConlose():
    for i in range(1, 5):
        url = main_url + str(i)
        print(url)
        HTMLAnalysis(DownHTML(url))


def main():
    SpiderConlose()


if __name__ == '__main__':
    main()
