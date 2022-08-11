import urllib.request
import re
import ssl

class Product(object):
    def __init__(self,img_url, price, title):
        self.img_url = img_url
        self.price = price
        self.title = title
        self.local_img_url = ''

    def set_local_img(self, local_img_url):
        self.local_img_url = local_img_url

class Taobao_prd_search(object):
    def __init__(self, key_words, base_url, ext_url, timeout, data_encode):
        self.key_words = key_words
        self.base_url = base_url
        self.ext_url = ext_url
        self.timeout = timeout
        self.data_encode = data_encode
        

    def build_opener(self):
        ssl._create_default_https_context = ssl._create_unverified_context
        headers = ("User-Agent","Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0")
        opener = urllib.request.build_opener();
        opener.addheaders = [headers]
        urllib.request.install_opener(opener)

    def build_url(self):
        kw = urllib.request.quote(self.key_words)
        self.url = self.base_url+ "?q=" + kw + self.ext_url
        print(self.url)

    def build_page_url(self, page):
        if(page != 0):
            self.url = self.url + "&s=" + str(page)
            print(self.url)

    def parse_data(self):
        prd_pattern = '<div class="product  " data-id=".*?".*?<div class="productImg-wrap">.*?<img  data-ks-lazyload=  "(.*?)" />.*?</div>.*?<p class="productPrice">.*?<em title=".*?"><b>&yen;</b>(.*?)</em>.*?</p>.*?<p class="productTitle">.*?<a href=".*?>(.*?)</a>.*?</p>.*?</div>'
        self.prd_data = re.compile(prd_pattern, re.S).findall(self.decode_data)

    def retrieve_data(self):
        try:
            self.data = urllib.request.urlopen(self.url, timeout=self.timeout).read()
        except Exception as err:
            print("retrieve data error")
            print(err)

    def decode_org_data(self):
        self.decode_data = self.data.decode(self.data_encode, "ignore")

    def print_data(self):
        print("--------product data-------")
        for s in self.prd_data:
            print(s[0])
            print(s[1])
            print(s[2])
            print("----------------------")

    def save_org_to_file(self, page):
        txt_file = open(self.save_file_path.replace(".txt", ("_" + str(page) + ".txt")), "wb")
        txt_file.write(self.data)
        txt_file.close()

    def save_prd_list(self):
        self.data_list = []
        for s in self.prd_data:
            p = Product(s[0], s[1], s[2])
            self.data_list.append(p)
            print(s[0])
            print(s[1])
            print(s[2])
            print("---------------------------------------")

    def retrieve_prod_img(self, folder_path, page_n):
        try:
            i=0
            for s in self.data_list:
                i_url = "https:" + s.img_url
                fn = folder_path + "\\" + str(page_n) + "_" + str(i) + ".jpg"
                urllib.request.urlretrieve(i_url,fn)
                s.set_local_img(fn)
                i+=1
        except Exception as err:
            print("retrieve img error")
            print(err)
            
    def save_to_file(self, page):
        txt_file =open(self.data_file.replace(".txt", ("_" + str(page) + ".txt")), "w", encoding="utf-8")
        for p in self.data_list:
            txt_file.write(p.img_url)
            txt_file.write("\r\n")
            txt_file.write(p.local_img_url)
            txt_file.write("\r\n")
            txt_file.write(p.price)
            txt_file.write("\r\n")
            txt_file.write(p.title)
            txt_file.write("\r\n------------------------------\r\n")
        txt_file.close()

    def save_to_html(self, folder_path, page_n):
        fp = folder_path + "\\products_" + str(page_n) + ".html"
        html_file = open(fp, "w", encoding="gbk")
        html_file.write("<html>")
        html_file.write("<table with='100%' border='1'>")

        for p in self.data_list:
            html_file.write("<tr><td><img src='" + p.local_img_url + "'</img></td>")
            html_file.write("<td>" + p.title + "<br><font color='red'>" + p.price + "</font></td></tr>")
        html_file.write("</table>")
        html_file.write("</html>")
        html_file.close()
            
        
    def process(self, save_file_path, data_file, page_no):
        self.save_file_path = save_file_path
        self.data_file = data_file
        
        print("build url")
        self.build_url()
        
        print("build opener")
        self.build_opener()

        for p in range(-1, page_no):
            print("processing page " + str(p))
            if(p == -1):
                page = 0
                print("retrieve data")
                self.retrieve_data()
            else:
                page = p * 60 + 59
                self.build_page_url(page)
                print("retrieve data")
                self.retrieve_data()
                
            print("save org data to file")
            self.save_org_to_file(page)

            print("decode data")
            self.decode_org_data()

            print("parse data")
            self.parse_data()

            print("save prd list")
            self.save_prd_list()

            print("retrieve img url")
            self.retrieve_prod_img("D:\\python\\learning\\test\\DL\\img", page)
            
            print("save data to file")
            self.save_to_file(page)

            print("save product to html file")
            self.save_to_html("D:\\python\\learning\\test\\DL",p)
        
        
base_url = "https://list.tmall.com/search_product.htm"
ext_url = "&imgfile=&commend=all&ssid=s5-e&search_type=tmall&sourceId=tb.index&spm=a21bo.2017.201856-taobao-item.1&ie=utf8&initiative_id=tbindexz_20170306"
key_words = "路由器 DLINK"
file_path = "D:\\python\\learning\\test\\DL\\" + key_words +".txt"
data_file = "D:\\python\\learning\\test\\DL\\" + key_words +"_prd.txt"
tb_sch = Taobao_prd_search(key_words,"https://list.tmall.com/search_product.htm", ext_url, 30, "gbk")
tb_sch.process(file_path, data_file, 5)


