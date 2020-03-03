__author__ = 'tonykidkid'

class Solution:
    """
    需求：判断输入的字符串是否为回文，具体描述如下
        给定一个字符串，验证它是否是回文串，只考虑字母和数字字符，可以忽略字母的大小写。
        说明：本题中，我们将空字符串定义为有效的回文串。
    示例 1:
        输入: "A man, a plan, a canal: Panama"
        输出: true
    示例 2:
        输入: "race a car"
        输出: false
    思路：
        第一步判断是否为空，空则返回真，不为空则做下一步；
        第二步，从输入字符串中找出字母或数字字符并转化成小写，放入列表list1；
        第三步，把list1转化成字符串S1后翻转S1变为S2
        第四步，比较S2和S1是否一致，一致则返回真
    """
    def __init__(self):
        import re
        self.__pattern = re.compile("[0-9]+|[a-zA-Z]+")

    def isPalindrome(self, input_string):
        if len(input_string) == 0:
            return True
        cleaned_char_ls = self.__pattern.findall(input_string.lower())
        ignore_case_string = "".join(cleaned_char_ls)
        list2 = [ignore_case_string[j] for j in range(len(ignore_case_string)-1, -1, -1)]
        if ignore_case_string == "".join(list2):
            return True
        else:
            return False


if __name__ == "__main__":
    str_y = ""
    str_z = "A man, a plan, a canal: Panama"
    pss = Solution()
    pss.isPalindrome(str_z)