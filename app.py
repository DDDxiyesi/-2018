# -*- coding: utf-8 -*-

import io
import sys
import os

from extractor.ChongZuExtractor import ChongZuExtractor
#sfsafsf

# 改变标准输出的默认编码
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# def print_2d_dict(rs_dict):
#     if rs_dict is None:
#         return
#     for (row_id, row) in sorted(rs_dict.items()):
#         print(row_id, " => ", sorted(row.items()))


# def test_html_parser_table(html_parser, html_file_path):
#     for table_dict in html_parser.parse_table(html_file_path):
#         print_2d_dict(table_dict)
#         print('-' * 80)


# def test_html_parser_paragraph(html_parser, html_file_path):
#     for paragraph in html_parser.parse_content(html_file_path):
#         print(paragraph)


# def test_content_extract(zjc_ex):
#     paras = [
#         "2014年5月27日，本公司接到控股股东彩虹集团电子股份有限公司（以下简称“彩虹电子”）通知，彩虹电子于2014年3月25日通过上海证券交易所大宗交易系统出售了本公司无限售条件流通股股份500万股，占公司股份总数的0.6786%，均价100元；于2014年5月26日通过上海证券交易所大宗交易系统出售了本公司无限售条件流通股股份500万股，占公司股份总数的0.6786%，合计减持1000万股，占公司股份总数的1.357% ",
#         "上述两次减持前，彩虹电子持有本公司股份165004798股，占公司股份总数的22.40% ；本次减持后，彩虹电子持有本公司股份155004798股，占公司股份总数的21.04% 。"]
#     for record in zjc_ex.extract_from_paragraphs(paras):
#         print(record.to_result())
#     print(zjc_ex.com_abbr_dict)
#     print(zjc_ex.com_full_dict)


#######################################################################################################################


# def extract_zengjianchi(zjc_ex, html_dir_path, html_id, zengjianchi_result_file_path):
#     record_list = []
#     f = open(zengjianchi_result_file_path, 'a' ,encoding='utf-8')
#     for record in zjc_ex.extract(os.path.join(html_dir_path, html_id)):
#         if record is not None and record.shareholderFullName is not None and \
#                 len(record.shareholderFullName) > 1 and \
#                 record.finishDate is not None and len(record.finishDate) >= 6:
#             record_list.append("%s\t%s" % (html_id, record.to_result()))
#     for record in record_list:
#         print(record, file= f)
#     f.close()
#     return record_list


# def extract_zengjianchi_from_html_dir(zjc_ex, html_dir_path, zengjianchi_result_file_path):
#     f = open(zengjianchi_result_file_path, 'a' ,encoding='utf-8')
#     print('公告id\t股东全称\t股东简称\t变动截止日期\t变动价格\t变动数量\t变动后持股数\t变动后持股比例', file = f)
#     f.close()
#     for html_id in os.listdir(html_dir_path):
#         extract_zengjianchi(zjc_ex, html_dir_path, html_id, zengjianchi_result_file_path)


def segment(sentence):
    words = segmentor.segment(sentence)
    print(' '.join(words))

def postag(words):
    postags = postagger.postag(words)  # 词性标注
    print(' '.join(postags))

def ner(words, postags):
    recognizer = NamedEntityRecognizer()  # 初始化实例
    recognizer.load(ner_model_path)  # 加载模型
    nertags = recognizer.recognize(words, postags)  # 命名实体识别
    print(' '.join(nertags))
    recognizer.release()


if __name__ == "__main__":
    # zengjianchi_config_file_path = 'config/ZengJianChiConfig.json'
    # ner_model_dir_path = 'D:/ltp_data_v3.4.0'
    # ner_blacklist_file_path = 'config/ner_com_blacklist.txt'
    chongzu_result_file_path = 'chongzu.txt'
    chongzu_html_file_path = 'D:\\fddc2018\\round2\\复赛新增类型测试数据-20180712\\资产重组\\html'

    # LTP_DATA_DIR = 'D:/ltp_data_v3.4.0/'  # ltp模型目录的路径
    # cws_model_path = os.path.join(
    #     LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`

    # segmentor = Segmentor()  # 初始化实例
    # segmentor.load(cws_model_path)  # 加载模型

    # segmentor.release()  # 释放模型

    # # 词性标注模型路径，模型名称为`pos.model`
    # pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')
    # # 命名实体识别模型路径，模型名称为`ner.model`
    # ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')

    # postagger = Postagger()  # 初始化实例
    # postagger.load(pos_model_path)  # 加载模型
    # postagger.release()

    ner_model_dir_path = 'D:/ltp_data_v3.4.0'
    ner_blacklist_file_path = 'config/ner_com_blacklist.txt'

    cz_ex = ChongZuExtractor(
     ner_model_dir_path, ner_blacklist_file_path)

    cz_ex.extract_chongzu_from_html_dir(chongzu_html_file_path, chongzu_result_file_path)
    # extract_chongzu_from_html_dir(cz_ex,
    #     chongzu_html_file_path, chongzu_result_file_path)
