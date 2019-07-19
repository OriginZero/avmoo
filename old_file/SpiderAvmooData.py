import os
import requests
from lxml import etree
from bs4 import BeautifulSoup

main_url = 'https://avmoo.net/cn/released/page/'


def DownHTML(url):
    try:
        r = requests.get(url)
        r.raise_for_status
        r.encoding = 'utf-8'
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

        html_temp = DownHTML(url)
        bs = BeautifulSoup(html_temp, 'html.parser')
        # 海报
        av_big_img = bs.find('a', {'class': {'bigImage'}}).attrs['href']
        # 视频时间
        av_movie_time = bs.find('div', {'class': {'row movie'}}).findAll('p')[
            2].contents[1]
        # 发行商
        av_manufacturer = bs.find(
            'div', {'class': {'row movie'}}).findAll('p')[4].text
        # 类别s
        type_lits = bs.find('div', {'class': {'row movie'}}).findAll(
            'span', {'class': {'genre'}})
        for type in type_lits:
            av_type_list.append(type.text)

        try:
            # 女优名
            av_performer = bs.find(
                'div', id='avatar-waterfall').find('span').text
            # 女优头像
            av_performer_avatar = bs.find(
                'div', id='avatar-waterfall').find('img').attrs['src']
        except Exception as e_performer_info:
            print(e_performer_info)
            print('出演人员未知...')
            av_performer = ''
            av_performer_avatar = ''

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
            # 封面
            av_poster = item.xpath(
                'a/div[@class="photo-frame"]/img/@src')[0]
            # av名称
            av_name = item.xpath('a/div[@class="photo-info"]/span')[0].text
            # 番号
            av_id = item.xpath(
                'a/div[@class="photo-info"]/span/date')[0].text
            # 发行时间
            av_release_time = item.xpath(
                'a/div[@class="photo-info"]/span/date')[1].text

            # 番号
            av_info['av_id'] = av_id
            # 视频名
            av_info['av_name'] = av_name
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
            av_info['type_lits'] = infos[5]
            # 视频预览图 list
            av_info['av_previews'] = infos[6]
            # 视频略缩图 list
            av_info['av_humbnails'] = infos[7]

            print(av_info)


def SpiderConlose():
    for i in range(1):
        url = main_url + str(i)
        HTMLAnalysis(DownHTML(url))


SpiderConlose()
