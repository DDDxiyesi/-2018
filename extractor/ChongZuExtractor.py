#!/bin/python
# -*- coding: utf-8 -*-

import os
import json
from bs4 import BeautifulSoup
from ner import NERTagger
import re
import regex


def strQ2B(ustring):
    """全角转半角"""
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:  # 全角空格直接转换
            inside_code = 32
        elif (inside_code >= 65281 and inside_code <= 65374):  # 全角字符（除空格）根据关系转化
            inside_code -= 65248

        rstring += chr(inside_code)
    return rstring


class ChongZuRecord(object):
    def __init__(self, jiaoYiBiaoDi, biaoDiCompany, jiaoYiDuiFang, jiaoYiZuoJia, pingGuFangFa):
        # 交易标的
        self.jiaoYiBiaoDi = jiaoYiBiaoDi
        # 标的公司
        self.biaoDiCompany = biaoDiCompany
        # 交易对方
        self.jiaoYiDuiFang = jiaoYiDuiFang
        # 标的作价
        self.jiaoYiZuoJia = jiaoYiZuoJia
        # 评估方法
        self.pingGuFangFa = pingGuFangFa

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False)

    def normalize_num(self, text):
        coeff = 1.0
        if '亿' in text:
            coeff *= 100000000
        if '万' in text:
            coeff *= 10000
        if '千' in text or '仟' in text:
            coeff *= 1000
        if '百' in text or '佰' in text:
            coeff *= 100
        if '%' in text:
            coeff *= 0.01
        try:
            # number = float(TextUtils.extract_number(text))
            # number_text = '%.4f' % (number * coeff)
            # if number_text.endswith('.0'):
            #     return number_text[:-2]
            # elif number_text.endswith('.00'):
            #     return number_text[:-3]
            # elif number_text.endswith('.000'):
            #     return number_text[:-4]
            # elif number_text.endswith('.0000'):
            #     return number_text[:-5]
            # else:
            #     if '.' in number_text:
            #         idx = len(number_text)
            #         while idx > 1 and number_text[idx-1] == '0':
            #             idx -= 1
            #         number_text = number_text[:idx]
            return "number_text"
        except:
            return text

    def normalize(self):
        if self.jiaoYiZuoJia is not None:
            self.jiaoYiZuoJia = self.normalize_num(self.jiaoYiZuoJia)

    def to_result(self):
        self.normalize()
        return "%s\t%s\t%s\t%s\t%s" % (
            # return "%s(full)\t%s(short)\t%s(date)\t%s(price)\t%s(num)\t%s(numAfter)\t%s(pcntAfter)" % (
            self.jiaoYiBiaoDi if self.jiaoYiBiaoDi is not None else '',
            self.biaoDiCompany if self.biaoDiCompany is not None else '',
            self.jiaoYiDuiFang if self.jiaoYiDuiFang is not None else '',
            self.jiaoYiZuoJia if self.jiaoYiZuoJia is not None else '',
            self.pingGuFangFa if self.pingGuFangFa is not None else '')


class ChongZuExtractor(object):

    def __init__(self, ner_model_dir_path, ner_blacklist_file_path):
        self.ner_tagger = NERTagger.NERTagger(
            ner_model_dir_path, ner_blacklist_file_path)

    def extract_chongzu_from_html_dir(self, chongzu_html_file_path, chongzu_result_file_path):
        f = open(chongzu_result_file_path, 'a', encoding='utf-8')
        print('交易标的\t标的公司\t交易对方\t交易标的作价\t评估方法', file=f)
        f.close()
        count = 0
        for html_id in os.listdir(chongzu_html_file_path):
            self.extract_chongzu(html_id, chongzu_html_file_path,
                                 chongzu_result_file_path)
            count = count +1
            print(str(html_id) + ' ' + str(count) + 'finish~')

    def extract_chongzu(self, html_id, chongzu_html_file_path, chongzu_result_file_path):
        record_list = []
        f = open(chongzu_result_file_path, 'a', encoding='utf-8')
        for record in self.extract(os.path.join(chongzu_html_file_path, html_id)):
            if record is not None and record.jiaoYiBiaoDi is not None and record.biaoDiCompany is not None:
                record_list.append("%s\t%s" %
                                   (html_id.split('.')[0], record.to_result()))
        for record in record_list:
            print(record, file=f)
        f.close()
        return record_list

    def extract(self, file_path):
        record_list = []
        f = open(file_path, encoding='utf-8')
        text = f.read()
        text = strQ2B(text)
        soup = BeautifulSoup(text, "html.parser")
        valid_table = None
        has_valid = False
        #todo 释义
        for table in soup.find_all("table"):
            if has_valid:
                break
            for tr in table.find_all("tr"):
                if len(tr.find_all("td")) > 0:
                    if "本公司" in tr.find_all("td")[0].get_text():
                        valid_table = table
                        break
        if valid_table is not None:
            record_list = self.extract_chongzu_from_table(valid_table)
            for record in record_list:
                record.jiaoYiZuoJia = self.extract_jiaoyi_zuojia(soup.get_text(), record)
        return record_list

    def extract_chongzu_from_table(self, table):
        record_list = []
        index_list = []
        # for tr in table.find_all("tr"):
        #     if len(tr.find_all("td")) > 0:
        #         row = tr.find_all("td")
        for tr in table.find_all("tr"):
            if len(tr.find_all("td")) > 0:
                row = tr.find_all("td")
                index_list.append(row[0].get_text().replace(
                    '\t', '').replace('\n', '').replace(' ', ''))
                if "交易标的" in row[0].get_text() or "标的资产" in row[0].get_text() or "拟购买资产" in row[0].get_text() or "拟注入资产" in row[0].get_text():
                    if(len(row) > 2):
                        record_list = self.extract_jiaoyi_biaodi(
                            tr.find_all("td")[2].get_text(), index_list)
        return record_list

    def extract_jiaoyi_zuojia(self, text, record):
        zuojia = None
        zuojia_reg = r'(?<=(本次.{0,20}作价.{0,20}))(\d+\,?\，?\d+\.?\d+).{0,2}元'
        if regex.search(zuojia_reg, text) is not None:
            print("zuojia")
            zuojia = regex.search(zuojia_reg,text).group().replace('元','')
        return zuojia

    def extract_jiaoyi_biaodi(self, text, index_list):
        record_list = []
        part_list = []
        text = text.replace('\t', '').replace('\n', '').replace(' ', '')
        text_arr = []
        seg = ""
        gufen_reg = r'(\d+\.?\d+%{1}的?股份|\d+\.?\d+%{1}的?股权|\d+\.?\d+%{1}的?权益)'
        if "、" in text or ";" in text or "；" in text:
            text_arr = re.split("、|;|；", text)
        else:
            text_arr.append(text)
        for word in text_arr:
            end = True
            if len(word) <= 6:
                end = False
                seg = seg + word + "、"
            if end:
                part_list.append(seg + word)
                seg = ""
        print(part_list)
        for part in part_list:
            # match_gufen = gufen_reg.match(part)
            company_match = None
            for company in index_list:
                if company in part and len(part) > 2:
                    # record = ChongZuRecord(None, None, None, None, None)
                    # # \d+\.?\d?%的?(股份|股权)
                    # # record.jiaoYiBiaoDi, record.biaoDiCompany = self.handleBiaoDiCompany(part)
                    # # record.jiaoYiBiaoDi = part
                    # # record.biaoDiCompany = "test"
                    record_list.extend(self.handleBiaoDiCompany(part))
                    company_match = company
                    break
            if company_match is None and re.search(gufen_reg, part) is not None:
                print("match")
                record_list.extend(self.handleBiaoDiCompany(part))
        return record_list

    def handleBiaoDiCompany(self, text):
        biaoDi = None
        company = None
        record_list = []
        gufen_reg = r'(\d+\.?\d+%{1}的?股份|\d+\.?\d+%{1}的?股权|\d+\.?\d+%{1}的?权益)'
        text_list = []
        chiyou = "所持有的|所持有|所持的|所持|持有的|持有"
        if re.search(gufen_reg, text) is not None and len(re.findall(gufen_reg, text)) > 1:
            text_list = re.split("和|及", text)
        else:
            text_list.append(text)
        for seg in text_list:
            record = ChongZuRecord(None, None, None, None, None)
            # record.jiaoYiBiaoDi, record.biaoDiCompany = self.handleBiaoDiCompany(part)
            if re.search(chiyou, seg) is not None and len(re.split(chiyou, seg)) > 1:
                try:
                    record.jiaoYiBiaoDi = re.search(
                        gufen_reg, re.split(chiyou, seg)[1]).group()
                except:
                    print('error')
                if record.jiaoYiBiaoDi is not None:
                    record.biaoDiCompany = re.sub(
                        gufen_reg, '', re.split(chiyou, seg)[1])
                    record.jiaoYiDuiFang = re.split(chiyou, seg)[0].replace("合计", "")
            elif re.search(gufen_reg, seg) is not None:
                record.jiaoYiBiaoDi = re.search(gufen_reg, seg).group()
                record.biaoDiCompany = re.sub(gufen_reg, '', seg)
            else:
                record.biaoDiCompany = seg
                record.jiaoYiDuiFang = seg
            record_list.append(record)
        return record_list
