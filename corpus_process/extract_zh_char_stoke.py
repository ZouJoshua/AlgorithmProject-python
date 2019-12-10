#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 12/10/19 7:22 PM
@File    : extract_zh_char_stoke.py
@Desc    : 抽取汉字笔画信息

"""

from corpus_process.Stoke.character_stoke_handian import Stoke
import sys
import os
from optparse import OptionParser


class Extract_stoke(object):
    """
        Extract_stoke
    """
    def __init__(self, input_file, output_file):
        """
        :param input_file:
        :param output_file:
        """
        input_file = input_file
        output_file_found = output_file + ".Found"
        output_file_found_temp = output_file + ".TempFound"
        output_file_NoFound = output_file + ".NoFound"
        if os.path.exists(output_file_found):
            os.remove(output_file_found)
        if os.path.exists(output_file_NoFound):
            os.remove(output_file_NoFound)
        if os.path.exists(output_file_found_temp):
            os.remove(output_file_found_temp)
        print(output_file_found_temp)
        self.file_word = open(output_file_found_temp, encoding="UTF-8", mode="w")
        self.stoke_opera = Stoke()
        self.dict = {}
        self.stoke_dict = {}
        self.stoke_NoFound_dict = {}
        self.NoFound = "NoFound"
        self.read_dict(in_file=input_file, all_line=-1)
        self.get_char_stoke()
        self.write_stoke(out_file=output_file_found, write_dict=self.stoke_dict)
        self.write_stoke(out_file=output_file_NoFound, write_dict=self.stoke_NoFound_dict)
        # print(self.dict)
        # print(len(self.dict))

    @staticmethod
    def is_chinese(uchar):
        """判断一个unicode是否是汉字"""
        if (uchar >= u'\u4e00') and (uchar <= u'\u9fa5'):
            return True
        else:
            return False

    def read_dict(self, in_file=None, all_line=None):
        """
        :param in_file:
        :param all_line:
        :return:
        """
        line_count = all_line
        if all_line is None:
            line_count = "Unknown"
        now_line = 0
        with open(in_file, encoding="UTF-8") as f:
            for line in f:
                now_line += 1
                sys.stdout.write("\r handling with the {} line, all {} lines.".format(now_line, line_count))
                # if now_line == 2:
                #     break
                line = line.strip("\n")
                for char in line:
                    if char in self.dict:
                        continue
                    if self.is_chinese(char) is False:
                        continue
                    self.dict[char] = 1
        f.close()
        print("\nHandle Finished.")

    def get_char_stoke(self):
        """
        :return:
        """
        now_line = 0
        line_count = len(self.dict)
        for char in self.dict:
            now_line += 1
            sys.stdout.write("\r handling with the {} line, all {} lines.".format(now_line, line_count))
            char_stoke = self.stoke_opera.get_stoke(char)
            if char_stoke is not None:
                self.write_word(self.file_word, word=char, stoke=char_stoke)
                self.stoke_dict[char] = char_stoke
            else:
                self.stoke_NoFound_dict[char] = [self.NoFound]
        # print(self.stoke_dict)
        print("\nHandle Finished.")

    def write_stoke(self, out_file=None, write_dict=None):
        """
        :param out_file:
        :param write_dict:
        :return:
        """
        print("save stoke to {}".format(out_file))
        if os.path.exists(out_file):
            os.remove(out_file)
        file = open(out_file, encoding="UTF-8", mode="w")
        for key, value in write_dict.items():
            # print("key {}, value {}".format(key, str(value)))
            v_str = self.dict_value2str(value)
            file.write(key + " " + v_str[1:].replace(" ", "") + "\n")
        file.close()
        print("Save Finished.")

    def write_word(self, file_word, word, stoke):
        """
        :param file_word:
        :param word:
        :param stoke:
        :return:
        """
        v_str = self.dict_value2str(stoke)
        # print(v_str[1:].replace(" ", ""))
        file_word.write(word + " " + v_str[1:].replace(" ", "") + "\n")

    @staticmethod
    def dict_value2str(v_list=None):
        """
        :param v_list:
        :return:
        """
        if v_list is None:
            return ""
        if isinstance(v_list, list) is False:
            return ""
        v_str = ""
        for v in v_list:
            v_str += (" " + v)
        return v_str


if __name__ == "__main__":
    print("Extract Chinese Character Stoke Information")
    # input_file = "./Data/giga_small.txt"
    # output_file = "./Data/giga_small_out"
    # Extract_stoke(input_file=input_file, output_file=output_file)

    parser = OptionParser()
    parser.add_option("--input", dest="input", help="input file")
    parser.add_option("--output", dest="output", help="output file")
    (options, args) = parser.parse_args()

    input_file = options.input
    output_file = options.output
    try:
        Extract_stoke(input_file=input_file, output_file=output_file)
    except Exception as err:
        print(err)
    print("All Finished.")