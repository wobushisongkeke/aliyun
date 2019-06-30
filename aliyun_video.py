import requests
import traceback
import re
import os

from aes import PrpCrypt
from binascii import b2a_hex, a2b_hex


class VideoCrawler:
    """
    a crawler to get video with m3u8
    """

    def __init__(self, path, ts_path, result_path):
        self.path = path
        self.ts_path = ts_path
        self.result_path = result_path
        self.keys = []
        self.ts_list = []
        self.headers = None
        self.m3u8 = None
        self.ts_url_list = None
        self.key_url_dealt = None
        self.iv_dealt = None

    def get(self, url):
        try:
            req = requests.get(url, self.headers)
            req.raise_for_status()
            req.encoding = req.apparent_encoding
            return req.text
        except:
            traceback.print_exc()

    def set_headers(self, cookie, referer, user_agent):
        self.headers = {"Cookie": cookie,
                        "Referer": referer,
                        "User-Agent": user_agent}

    def parse_m3u8(self, m3u8):
        self.m3u8 = m3u8
        self.ts_url_list = re.findall(r'http.*\.ts', self.m3u8)
        key_url_list = re.findall(r'EXT-X-KEY:METHOD=AES-128,URI="http.*"', self.m3u8)
        iv_list = re.findall(r'IV=0x.{32}', self.m3u8)

        self.key_url_dealt = []
        for key in key_url_list:
            key = key[30:-1]
            self.key_url_dealt.append(key)

        self.iv_dealt = []
        for iv in iv_list:
            iv = iv[5:]
            self.iv_dealt.append(iv)

    def save_ts_url(self, url):
        name = url.split("/")[-1]
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        try:
            req = requests.get(url)
            req.raise_for_status()
            file_path = self.path + os.path.sep + name
            print("download", file_path)
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(req.content)
            return req.content
        except:
            traceback.print_exc()

    def save_content(self, name, content, path):
        if type(content) == str:
            content = content.encode('utf-8')
        if not os.path.exists(path):
            os.makedirs(path)
        filepath = path + os.path.sep + name
        print(filepath)
        if not os.path.exists(filepath):
            with open(filepath, 'wb') as f:
                f.write(content)

    def chr_parse_int(self, s):
        s_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                  'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        i_list = list(range(0, 36))
        for i in range(len(s_list)):
            if s == s_list[i]:
                return i_list[i]

    def str_parse_int(self, s):
        result = 0
        for i in range(len(s)):
            i = self.chr_parse_int(s[i])
            result = result * 36 + i
        return result

    def parse_key(self, key):
        key = bytes(key, "utf-8")
        se = ord("a")
        if len(key) == 20:
            r = key[0]
            i = chr(r).lower()
            a = self.chr_parse_int(i) % 7
            n = key[a]
            o = chr(n)
            s = key[a + 1]
            l = chr(s)
            u = self.str_parse_int(o + l) % 3
            if u == 2:
                d = key[8]
                h = key[9]
                c = key[10]
                f = key[11]
                p = key[15]
                g = key[16]
                v = key[17]
                y = key[18]
                m = d - se + 26 * (int(chr(h)) + 1) - se
                b = c - se + 26 * (int(chr(f)) + 1) - se
                E = p - se + 26 * (int(chr(g)) + 1) - se
                T = v - se + 26 * (int(chr(y)) + 2) - se
                result = [key[0], key[1], key[2], key[3], key[4], key[5], key[6], key[7], m, b, key[12], key[13],
                          key[14], E, T, key[19]]
                return bytes(result)
            elif u == 1:
                result = [key[0], key[1], key[2], key[3], key[4], key[5], key[6], key[7], key[18], key[16], key[15],
                          key[13], key[12], key[11], key[10], key[8]]
                return bytes(result)
            else:
                if u != 0:
                    pass
                result = [key[0], key[1], key[2], key[3], key[4], key[5], key[6], key[7], key[8], key[10], key[11],
                          key[12], key[14], key[15], key[16], key[18]]
                return bytes(result)
        elif len(key) == 17:
            key = key[1:]
            result = [key[8], key[9], key[2], key[3], key[4], key[5], key[6], key[7], key[0], key[1], key[10], key[11],
                      key[12], key[13], key[14], key[15]]
            return bytes(result)
        else:
            return key

    def decoding(self):
        key = ""
        for i in range(0, len(self.ts_url_list)):
            ts_url = self.ts_url_list[i]
            print("No", i, "file\t", ts_url)
            ts = self.save_ts_url(ts_url)

            key_name = ts_url.split("/")[-1].split(".ts")[0] + ".key"
            iv_name = ts_url.split("/")[-1].split(".ts")[0] + ".iv"
            ts_name = ts_url.split("/")[-1].split(".ts")[0] + "_convert.ts"

            if i <= 1:
                key = self.get(self.key_url_dealt[i])
                key = self.parse_key(key)
            iv = self.iv_dealt[i]
            print("key_url:", self.key_url_dealt[i])
            print("key:", key)
            print("iv", iv)

            self.save_content(key_name, key, self.path)
            self.save_content(iv_name, iv, self.path)

            iv = a2b_hex(iv)
            pc = PrpCrypt(key, iv)
            result = pc.decrypt(ts)
            with open(self.ts_path + "\\" + ts_name, 'wb') as f:
                f.write(result)
            self.ts_list.append(result)

    def merge_ts(self):
        out_file = open(self.result_path + os.path.sep + "1.ts", "wb")

        for i in range(0, len(self.ts_list)):
            in_file = self.ts_list[i]
            out_file.write(in_file)
        out_file.close()


def main():
    url = "https://edu.aliyun.com/hls/2452/stream/hd/0gxCAtRVHB64yCzbZiwLh0Su3JQ47HFb.m3u8?courseId=137"
    cookie = 'cna=Iku1Em9R7wMCARtzUoTKcixa; _ga=GA1.2.1104457312.1524625881; acw_tc=76b20f4515611199516521378e35d2c' \
             'da57c578ceebbaba3ad76862902491f; aliyun_choice=CN; UM_distinctid=16b7a00185c50f-0981055932157f-3b6542' \
             '00-13c680-16b7a00185d929; login_aliyunid_pk=1820660914581414; aliyun_lang=zh; aliyungf_tc=AQAAAAXAhzu' \
             'IOQMA5FNzG9fmt0QcPy6D; PHPSESSID=dkjpkpn45h58dea3jaobh9b9v3; t=863b9776ad1b0e36a938e07b8ffb2511; _tb_' \
             'token_=e14e0f56b353e; cookie2=1ae8007c674f74166d497546b5965b78; _hvn_login=6; FECS-XSRF-TOKEN=0699f50' \
             '4-e6e3-43c3-bbda-61d857015bff; FECS-UMID=%7B%22token%22%3A%22Y165bf70b1d9b381174e620d6b3ca94d2%22%2C%' \
             '22timestamp%22%3A%224976240455555E46534D6579%22%7D; __yunlog_session__=1561794014220; CLOSE_HELP_GUID' \
             'E_V2=true; onIn=true; CNZZDATA1261859658=1365441422-1561119589-%7C1561870124; ping_test=true; csg=5cd' \
             'c54b4; login_aliyunid="wobushisong****"; login_aliyunid_ticket=Rt7mGxbigG2Cd4fWaCmBZHIzsgdZq64XXWQgyK' \
             'Feuf0vpmV*s*CT58JlM_1t$w37r$sajs9lzhfMANasxmSeOsMilaRW2ZnlGay1TQSdG_0gpof_BNTwUhTOoNC1ZBeeMfKJzxdnb95' \
             'hYssNIZor6qCS0; login_aliyunid_luid="BG+Ee69KfTQ4b404c88f48467c2bde71cb9bbb32044+RC0C0lCGbcq7d7bFEYNE' \
             'kg=="; login_aliyunid_csrf=_csrf_tk_1600861871809750; login_aliyunid_suid="+ygggPDggMV/esU1RDIFOLQs+9' \
             'qiees4n9A0pEJ8bR0Mz8CfAQY="; login_aliyunid_abi="BG+c371Alg6c2e2219ca42bf1bff961e339d22c703b+ChDiJeNo' \
             'dWunkDhWgCcPDR3t+T2PchJfFSMcCQl5s/EHr0AOKkg="; login_aliyunid_pks="BG+bS/qKd8FxUWo0HuZMjOOlLulfrRhkpj' \
             'bYkSuyueUD/8="; hssid=1uouweHkz9vAVQGIPJUTU4g1; hsite=6; aliyun_country=CN; aliyun_site=CN; l=bBrv8LN' \
             '4vwkA-0ebKOCwourza77OSIRAguPzaNbMi_5Kt1YsMVQOkAeQfev6Vj5R_LLB4VsrWwy9-etki; isg=BOjoQLSyIZObgQvYnsNx9' \
             '8HPudaVqyy-auo3AqIZNGNW_YhnSiEcq34_8dWoTQTz; SERVERID=da001b2578bb0f24c16ff5fb13383a0a|1561871845|156' \
             '1871842'
    referer = "https://edu.aliyun.com/bundles/customweb/lib/cloud-player/1.1.37.3/player.html"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729" \
                 ".169 Safari/537.36"

    save_path = r"F:\crawler\aliyun_video\aliyun_video\tmp"
    ts_path = r"F:\crawler\aliyun_video\aliyun_video\convert"
    result_path = r"F:\crawler\aliyun_video\aliyun_video"

    if not os.path.exists(save_path):
        os.makedirs(save_path)
    if not os.path.exists(ts_path):
        os.makedirs(ts_path)
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    crawler = VideoCrawler(save_path, ts_path, result_path)
    crawler.set_headers(cookie, referer, user_agent)
    m3u8 = crawler.get(url)
    if not os.path.exists(save_path + "\\list2.m3u8"):
        with open(save_path + "\\list2.m3u8", "w") as f:
            f.write(m3u8)
    crawler.parse_m3u8(m3u8)
    crawler.decoding()
    crawler.merge_ts()


if __name__ == "__main__":
    main()
