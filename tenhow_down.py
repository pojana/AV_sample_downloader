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


class mgs_img_down():
    def __init__(self) -> None:
        self.save_path = save_path
        self.name = ''
        self.title = ''
        self.session = ''
        self.cookie = {'adc': '1'}

    # def age_check(self):
    #    check_url = 'https://www.dmm.co.jp/mono/'
    #    self.session = requests.session()

    def get_url_list(self, url):

        self.save_path = save_path
        down_list = self.get_image_url(url=url)

        re.sub(r'[\\|/|:|?|.|!|*|"|<|>|\|]', '_', self.title)
        self.title = self.title.replace('*', '_')
        self.title = self.title.replace(chr(92), '_')
        self.title = self.title.replace('/', '_')
        print(self.title)

        # self.save_path += self.name + '\\' + self.title + '\\'
        self.save_path += self.title + '\\'
        pathlib.Path(self.save_path).mkdir(exist_ok=True, parents=True)

        self.download_frm_list(down_list, self.save_path)

    def download_frm_list(self, down_list, save_path):
        # [1.jpg, url]の二次元配列にする
        dlist = []
        for i, url in enumerate(down_list):
                
            filepath = self.save_path + '_' + url.replace('https://www.tenhow.net/images/', '') + '.jpg'
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
        name_temp = soup.find('ul', class_='Bread_crumb bold')
        name_temp = name_temp.find_all('li')
        self.name = name_temp[-2].get_text().strip()
        print(self.name)

        # urlのリストを取得
        base_url = 'https://www.mgstage.com'
        ul_temp = soup.find('div', class_='rank_list')

        ul_temp = [u.find('a') for u in ul_temp.find_all('h5')]
        url_list = [base_url + u.get('href') for u in ul_temp]
        # print(url_list)
        # print(len(url_list))
         
        # 次ページが存在するか調べる
        pages = soup.find_all('a', class_='page')
        
        # 次ページがなければココで終わる
        if pages == []:
            return url_list
        else:
            pass
        
        # ページごとに再帰的に呼び出し
        page = 'page'
        for p in pages:
            if p.text == '次へ':
                NextPage = url + '&page' + p.get('href').split(page)[-1]
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
        r.encoding = r.apparent_encoding
        soup = bs4.BeautifulSoup(r.text, 'lxml')
        sample_urls = []

        try:
            # タイトルを取得
            self.title = soup.find('h2', class_='um_title').get_text().strip()
            print(self.title)

            # サンプルのイメージ取得
            # package_temp = soup.find('div', class_='um_image_a um_popup')
            base_url = 'https://www.tenhow.net/'

            package_temp = soup.find_all('a', title='拡大表示')
            sample_urls = [base_url + i.get('href') for i in package_temp]
            print(sample_urls)

            print(len(sample_urls))

        except AttributeError:
            print('AttributeError:{}'.format(url))
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
    mgs = mgs_img_down()
    args = sys.argv

    if len(args) >= 2:
        if '.txt' in args[1]:
            print("get from txt")
            
            with open(args[1], mode='r', encoding='utf-8') as file:
                url_list = file.readlines()
                url_list = [li.rstrip() for li in url_list]

            for url in url_list:
                mgs.get_url_list(url)

        elif 'https' in args[1]:
            print('get one url')
            mgs.get_url_list(sys.argv[1])
        
        else:
            print('pls args url or txt_path')
            

if __name__ == '__main__':

    # url = 'https://www.mgstage.com/search/cSearch.php?actor[]=%E5%85%AB%E6%8E%9B%E3%81%86%E3%81%BF_0&type=top'
    # url = 'https://www.mgstage.com/search/cSearch.php?actor[]=%E9%88%B4%E6%9D%91%E3%81%82%E3%81%84%E3%82%8A_0&type=top'
    # url = 'https://www.mgstage.com/search/cSearch.php?actor[]=%E9%88%B4%E6%9D%91%E3%81%82%E3%81%84%E3%82%8A_0&actor[]=%E3%81%82%E3%82%84%E3%81%BF%E6%97%AC%E6%9E%9C_1&type=top&page=1&list_cnt=120'    
    # url = 'https://www.mgstage.com/search/cSearch.php?actor[]=%E6%B3%A2%E5%A4%9A%E9%87%8E%E7%B5%90%E8%A1%A3_0&type=top'
    
    # mgs.get_url_from_pages(url)

    # url = 'https://www.mgstage.com/product/product_detail/ABW-159/'
    # mgs.get_image_url(url)

    main()
