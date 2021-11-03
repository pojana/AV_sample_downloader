from re import findall
import requests
import bs4
import pprint
import pathlib
import re
from concurrent.futures import ThreadPoolExecutor
import sys

save_path = ''

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"
}


class fanza_img_down():
    def __init__(self) -> None:
        self.save_path = save_path
        self.name = ''
        self.title = ''
        self.session = ''
        self.cookie = {'age_check_done': '1'}

    # def age_check(self):
    #    check_url = 'https://www.dmm.co.jp/mono/'
    #    self.session = requests.session()

    def get_url_list(self, url):

        url_list = self.get_url_from_pages(url)
        print(len(url_list))

        for url in url_list:
            self.save_path = save_path
            down_list = self.get_image_url(url=url)

            if down_list == []:
                print('not foud img url')
                continue

            re.sub(r'[\\|/|:|?|.|!|*|"|<|>|\|]', '_', self.title)
            replace_table = ['\\', '"', '*', "?", ":", "|", "<", ">", "/"]
            for rep in replace_table:
                self.title = self.title.replace(rep, '_')
                self.title = self.title.replace(rep, '_')
                self.title = self.title.replace(rep, '_')

            self.title = self.title.replace(chr(92), '_')
            self.title = self.title.replace(chr(92), '_')
            
            print(self.title)

            # self.save_path += self.name + '\\' + self.title + '\\'
            self.save_path += self.name + '\\'
            pathlib.Path(self.save_path).mkdir(exist_ok=True, parents=True)

            self.download_frm_list(down_list, self.save_path)

            self.save_path = save_path + self.name + '\\' + 'lib\\' + self.title + '\\'
            pathlib.Path(self.save_path).mkdir(exist_ok=True, parents=True)

            self.download_frm_list(down_list, self.save_path)
            
    def download_frm_list(self, down_list, save_path):
        # [1.jpg, url]の二次元配列にする
        dlist = []
        for i, url in enumerate(down_list):
                
            filepath = self.save_path + self.title + '_' + str(i) + '.jpg'
            add_list = [filepath, url]

            dlist.append(add_list)

        # print(dlist)
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(self.save_image, dlist)

    def save_image(self, data):
        img = requests.get(data[1], headers=headers, cookies=self.cookie)

        if img.status_code == 200:
            print('response: {}, filename: {}, \nurl: {}'.format(
                str(img.status_code), data[0], data[1]
            ))

            with open(data[0], 'wb') as file:
                file.write(img.content)

        else:
            print('!Failed! response: {}, filename: {}, \nurl: {}'.format(
                str(img.status_code), data[0], data[1]
            ))

    def get_url_from_pages(self, url):
        print(url)

        r = requests.get(url=url, headers=headers, cookies=self.cookie)
        soup = bs4.BeautifulSoup(r.text, 'lxml')
        
        # 名前を取得
        name_temp = soup.find_all('span', itemprop='name')
        self.name = name_temp[-1].get_text()
        # print(self.name)

        # urlのリストを取得
        ul_temp = soup.find('div', class_='d-item')
        url_list = [u.find('a').get('href') for u in ul_temp.find_all('p', class_='tmb')]
        
        # 次ページが存在するか調べる
        pages = soup.find('div', class_='list-boxcaptside list-boxpagenation')
        pages = [i for i in pages.find('ul').find_all('a')]
        
        # 次ページがなければココで終わる
        if pages == []:
            return url_list
        else:
            pass
        
        # ページごとに再帰的に呼び出し
        base_url = 'https://www.dmm.co.jp'
        for p in pages:
            if p.text == '次へ':
                NextPage = base_url + p.get('href')
                url_list.extend(self.get_url_from_pages(NextPage))
                break
            else:
                pass

        return url_list

    def get_image_url(self, url):
        # title ps, pl, jp
        # mide***-[1-9] -> mide***jp-[1-9]
        # rebd          -> rebd***jp
        # ABP, ABW      -> ab*****jp
        # ssis          -> jp
        # ipx -> jp

        # PRESTAGE -> cap_t1 -> cap_e

        r = requests.get(url=url, headers=headers, cookies=self.cookie)
        soup = bs4.BeautifulSoup(r.text, 'lxml')
        sample_urls = []

        # タイトルを取得
        try:
            self.title = soup.find('h1', class_='item fn').get_text()
            print(self.title)

            # ジャケットurl取得
            im_temp = soup.find('div', class_='tx10 pd-3 lh4')
            img_url = im_temp.find('a').get('href')

            # タイトルに製品番号追加
            self.title = im_temp.find('a').get('id').upper() + ' ' + self.title
        
            # サンプルのイメージ取得
            sample_temp = soup.find_all('a', attrs={'name': 'sample-image'})
            sample_urls = [i.find('img').get('src') for i in sample_temp]

            sample_urls = [i.replace('-', 'jp-') for i in sample_urls]

            sample_urls.insert(0, img_url)
            print(len(sample_urls))

        except AttributeError:
            print(url)
            self.err_log(url)
            return sample_urls

        return sample_urls

    def err_log(self, url):
        log_dir = './errlog\\'
        pathlib.Path(log_dir).mkdir(exist_ok=True)
        log_dir += self.name + '.log'

        with open(log_dir, 'a') as logfile:
            if not url:
                url = 'None'
            else:
                pass
            logfile.write(url + '\n')


def main():
    fanza = fanza_img_down()
    args = sys.argv

    if len(args) >= 2:
        if '.txt' in args[1]:
            print("get from txt")
            
            with open(args[1], mode='r', encoding='utf-8') as file:
                url_list = file.readlines()
                url_list = [li.rstrip() for li in url_list]

            for url in url_list:
                fanza.get_url_list(url)

        elif 'https' in args[1]:
            print('get one url')
            fanza.get_url_list(sys.argv[1])
        
        else:
            print('pls args url or txt_path')
            

if __name__ == '__main__':
    main()
    """
    # url = 'https://www.dmm.co.jp/mono/dvd/-/list/=/article=actress/id=1051912/'
    # url = 'https://www.dmm.co.jp/mono/dvd/-/list/=/article=actress/id=1037700/'
    # url = 'https://www.dmm.co.jp/mono/dvd/-/list/=/article=actress/id=1049255/'
    # url = 'https://www.dmm.co.jp/mono/dvd/-/list/=/article=actress/id=1034355/'
    # url = 'https://www.dmm.co.jp/mono/dvd/-/list/=/article=actress/id=1016835/'
    # url = 'https://www.dmm.co.jp/mono/dvd/-/list/=/article=actress/id=1072360/'

    if sys.argv[1]:
        fanza.get_url_list(sys.argv[1])
    else:
        print('please argv url')
    

    url = 'https://www.dmm.co.jp/mono/dvd/-/detail/=/cid=9mide754/?dmmref=aMonoDvd_List/'
    url = 'https://www.dmm.co.jp/mono/dvd/-/detail/=/cid=h_346rebd584tk/?dmmref=aMonoDvd_List/'
    url = 'https://www.dmm.co.jp/mono/dvd/-/detail/=/cid=118abw032/'
    # url = 'https://www.dmm.co.jp/mono/dvd/-/detail/=/cid=h_346rebdb570/?dmmref=aMonoDvd_List/'
    fanza.get_image_url(url)
    """
