import re,hashlib
from urllib.parse import urlparse, parse_qs

def generate_md5_hash(content):
    # 创建MD5对象
    md5 = hashlib.md5()
    # 对提供的内容进行编码，并更新MD5对象
    md5.update(content.encode('utf-8'))
    # 返回十六进制的摘要字符串
    return md5.hexdigest()

# Define constants simulating the Go constants
CustomValueMark = "{{HXHunter}}"
UpperMark = "{{upper}}"
TooLongMark = "{{long}}"
NumberMark = "{{number}}"
ChineseMark = "{{chinese}}"
UrlEncodeMark = "{{urlencode}}"
UnicodeMark = "{{unicode}}"
TimeMark = "{{time}}"
MixAlphaNumMark = "{{mix_alpha_num}}"
MixSymbolMark = "{{mix_symbol}}"
MixNumMark = "{{mix_num}}"
NoLowerAlphaMark = "{{no_lower}}"
MixStringMark = "{{mix_str}}"
BoolMark = "{{bool}}"
ListMark = "{{list}}"
#WithNameOrTitleMark= "{{with_name_or_title}}"
MixAlphaHyphen= "{{mix_alpha_hyphen}}"


# Define regular expressions
# Regular expressions equivalent to the Go version
chinese_regex = re.compile(r"[\u4e00-\u9fa5]+")
urlencode_regex = re.compile(r"(?:%[A-Fa-f0-9]{2,6})+")
unicode_regex = re.compile(r"(?:\\u\w{4})+")
only_alpha_regex = re.compile(r"^[a-zA-Z]+$")
only_alpha_upper_regex = re.compile(r"^[A-Z]+$")
alpha_upper_regex = re.compile(r"[A-Z]+")
alpha_lower_regex = re.compile(r"[a-z]+")
replace_num_regex = re.compile(r"[0-9]+\.[0-9]+|\d+")
only_number_regex = re.compile(r"^[0-9]+$")
number_regex = re.compile(r"[0-9]+")
one_number_regex = re.compile(r"[0-9]")
num_symbol_regex = re.compile(r"\.|_|-")
time_symbol_regex = re.compile(r"-|:|\s")
only_alpha_num_regex = re.compile(r"^[0-9a-zA-Z]+$")
only_alpha_hyphen_regex = re.compile(r"^[a-zA-Z\-_]+$")
marked_string_regex = re.compile(r"^{{.+}}$")
html_replace_regex = re.compile(r"\.shtml|\.html|\.htm")


# Function to check if a string has special symbols
SPECIAL_SYMBOLS = set("{ } | # @ $ * , < > / ? \\ + =".split())

def has_special_symbol(value_str):
    # 将字符串转换为集合并与特殊字符集合进行交集操作
    # 如果结果非空，表明至少有一个特殊符号存在
    return bool(set(value_str) & SPECIAL_SYMBOLS)

class SmartFilter:
    def __init__(self, strict_mode=False):
        self.strict_mode = strict_mode
        self.filter_result_DB= {}


    def mark_param_value(self, param_map, url,method):
        marked_param_map = {}
        for key, value in param_map.items():
            if isinstance(value, bool):
                marked_param_map[key] = BoolMark
                continue
            if isinstance(value, list):
                marked_param_map[key] = ListMark
                continue
            if isinstance(value, float) or isinstance(value, int):
                marked_param_map[key] = NumberMark
                continue

            # Only process string types
            if not isinstance(value, str):
                continue

            value_str = value
            #name = method + url + key
            if "HXHunter" in value_str:
                marked_param_map[key] = CustomValueMark
            elif only_alpha_upper_regex.match(value_str):
                marked_param_map[key] = UpperMark
            elif len(value_str) >= 24:
                marked_param_map[key] = TooLongMark
            elif only_number_regex.match(value_str) or only_number_regex.match(num_symbol_regex.sub("", value_str)):
                marked_param_map[key] = NumberMark
            elif chinese_regex.search(value_str):
                marked_param_map[key] = ChineseMark
            elif urlencode_regex.search(value_str):
                marked_param_map[key] = UrlEncodeMark
            elif unicode_regex.search(value_str):
                marked_param_map[key] = UnicodeMark
            elif only_number_regex.match(time_symbol_regex.sub("", value_str)):
                marked_param_map[key] = TimeMark
            elif only_alpha_num_regex.match(value_str) and number_regex.search(value_str):
                marked_param_map[key] = MixAlphaNumMark
            elif only_alpha_hyphen_regex.match(value_str):
                marked_param_map[key] = MixAlphaHyphen
            elif has_special_symbol(value_str):
                marked_param_map[key] = MixSymbolMark
            elif self.is_mixNum(value_str)==True:
                marked_param_map[key] = MixNumMark
            elif self.strict_mode and not alpha_lower_regex.search(value_str):
                marked_param_map[key] = NoLowerAlphaMark
            else:
                # Check for mixed string mark condition
                count = 0
                if alpha_lower_regex.search(value_str):
                    count += 1
                if alpha_upper_regex.search(value_str):
                    count += 1
                if number_regex.search(value_str):
                    count += 1
                if "_" in value_str or "-" in value_str:
                    count += 1
                if count >= 3:
                    marked_param_map[key] = MixStringMark
                else:
                    marked_param_map[key] = value
        return marked_param_map

    def is_mixNum(self,part):
        OneNumberRegex = re.compile(r'\d')  # 正则表达式，匹配任何数字
        b = OneNumberRegex.sub('0', part)  # 替换字符串中的数字为'0'
        if b.count('0') >= 3:  # 如果'0'的数量超过3
            return True
        return False

    def mark_path(self,path):
        path_parts = path.split('/')
        for index, part in enumerate(path_parts):
            if len(part) >= 32:
                path_parts[index] = TooLongMark
            elif only_number_regex.match(num_symbol_regex.sub("", part)):
                path_parts[index] = NumberMark
            elif part.endswith(".html") or part.endswith(".htm") or part.endswith(".shtml"):
                part = html_replace_regex.sub("", part)
                if number_regex.search(part) and alpha_upper_regex.search(part) and alpha_lower_regex.search(part):
                    path_parts[index] = MixAlphaNumMark
                elif only_number_regex.match(num_symbol_regex.sub("", part)):
                    path_parts[index] = NumberMark
            elif has_special_symbol(part):
                path_parts[index] = MixSymbolMark
            elif chinese_regex.search(part):
                path_parts[index] = ChineseMark
            elif unicode_regex.search(part):
                path_parts[index] = UnicodeMark
            elif only_alpha_upper_regex.match(part):
                path_parts[index] = UpperMark
            elif only_number_regex.match(num_symbol_regex.sub("", part)):
                path_parts[index] = NumberMark
            elif self.is_mixNum(part)==True:
                path_parts[index] = MixNumMark

        new_path = '/'.join(path_parts)
        return new_path


    def url_parser(self,url,method):
        # 解析URL
        parsed_url = urlparse(url)
        # 解析查询字符串部分
        query_params = parse_qs(parsed_url.query)
        #url_path=parsed_url.hostname+parsed_url.path
        # parse_qs 默认情况下会将参数值存储在列表中，因为查询字符串中的参数可能出现多次
        params_dict = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}

        return params_dict,parsed_url.hostname,parsed_url.path,method

    def is_duplicate_req(self,total_result_hash,limit=1):
        hash_key = total_result_hash
        if hash_key in self.filter_result_DB:
            count=self.filter_result_DB[hash_key]
            if count<=limit:
                return False
        return True

    def add_hash_to_filter_result_DB(self,total_result_hash):
        # 依据total_result_hash进行累加
        self.filter_result_DB[total_result_hash] = self.filter_result_DB.get(total_result_hash, 0) + 1

    def gen_mark_hash_data(self,url,is_debug=False):
        url_data={}
        url_data.update({url: {}})
        url_dicts, host, path, method = self.url_parser(url, "GET")
        result = self.mark_param_value(url_dicts, host + path, method)
        url_data[url].update({"params_mark": result})
        result2 = self.mark_path(path)

        total_result = str(result) + str(result2)
        total_result_hash = generate_md5_hash(total_result)
        url_data[url].update({"path_mark": result2})
        url_data[url].update({"total_result_hash": total_result_hash})

        if is_debug:
            print(result)
            print(result2)
            print(total_result_hash)

        return url_data,total_result_hash

    def de_deplicate_url(self,url_list):
        method="GET"
        duplicate_count = 0
        smart_duplicate_count = 0
        total_count=len(url_list)

        total_need_send_request_data = []
        total_duplicate_send_request_data = []

        for url in url_list:
            url_data, total_result_hash = self.gen_mark_hash_data(url)
            self.add_hash_to_filter_result_DB(total_result_hash)
            if self.is_duplicate_req(total_result_hash, limit=1) == False:
                total_need_send_request_data.append(
                    {'url': url, 'method': method,
                     "smart_hash": total_result_hash, "type": "smart_duplicate"})
                resp_code = 0
                #print(f'Send URL: {url} - Method: {method} - Status Code: {resp_code}')
            else:
                #print(f'smart_filter Duplicate request skipped : {url} - Method: {method}')
                total_duplicate_send_request_data.append(
                    {'url': url, 'method': method,
                     "smart_hash": total_result_hash, "type": "smart_duplicate"})
                duplicate_count += 1
                smart_duplicate_count += 1
        print("total_count: ", total_count)
        print("duplicate_count: ", duplicate_count)
        print("smart_duplicate_count: ", smart_duplicate_count)
        print("left count: ", total_count - duplicate_count)
        return total_need_send_request_data, total_duplicate_send_request_data

if __name__ == '__main__':
    smart_filter=SmartFilter()
    url_list=[
        'https://pre.test.com/v1/api/items/1704701705084',
        'https://pre.test.com/v1/api/items/1704701712084',
        'https://api-dev.test.com/shippedTimeout/getUnShippedCnt?time=1704701940803'
        'https://api-dev.test.com/shippedTimeout/getUnShippedCnt?time=1704711940803'
        ,'https://open-pre.test.com/open/videos/8732184001006?_token=20ba672516d6a0&_client_id=8ec7abb8c13b0f'
        ,'https://prod.test.com/project/get/a7bd9230-7604-4523-92ed-cbbc4b2c4546'
        ,'https://prod.test.com/project/get/a7bd9230-7604-4523-92ed-cbbc4b2c4546?aa=7604-4523-92ed-cbbc4b2c4546'
        ,'https://prod.test.com/project/get/a7bd9230-7604-4523-92ed-cbbc4b2c4546?aa=1111-1111-92ed-cbbc4b2c4546'
        ,'https://test.test.com/device/release?symbol=XKKBB19111205782'
        ,'https://test.test.com/device/release?symbol=XKKBB19111'
        ,'https://passport.test.com/status?k=1704702672747'
        ,'https://passport.test.com/status?k=1704731231347'
        ,'https://live.test.com/live/common/meta?type=2&ts=1704702831691'
        ,'https://live.test.com/live/common/meta?type=2&ts=1704702222691'
        ,'https://gst.test.com/open/api/securityData/c?appId=206'
        ,'https://gst.test.com/open/api/securityData/c?appId=333'
        ,'https://kv.test.com/address/list?time=0.830512089201636'
        ,'https://kv.test.com/address/list?time=0.123131313123131'
        ,'https://oe-manage.test.com/api/v1/app/publish/flow/logs?publishId=2175&startId=17282&limit=500'
        ,'https://oe-manage.test.com/api/v1/app/publish/flow/logs?publishId=2175&startId=88888&limit=500'
              ]


    total_need_send_request_data, total_duplicate_send_request_data=smart_filter.de_deplicate_url(url_list)
    for url in total_need_send_request_data:
        print(url)
    print("--------------------------------------")
    for url in total_duplicate_send_request_data:
        print(url)

