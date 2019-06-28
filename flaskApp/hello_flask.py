# coding:utf-8

import json, re, time
from flask import Flask, Response, request
from werkzeug.routing import Rule
import TestPinpointDaily


class CIRule(Rule):
    """
    Create my own rule for Case Insensitivity. This class will be inherited by my own Flask Application.
    It will be used for replacing 'url_rule_class' in class 'Flask'.
    """
    def compile(self):
        Rule.compile(self)
        self._regex = re.compile(self._regex.pattern, re.UNICODE | re.IGNORECASE)


class CaseInsensitivityFlask(Flask):
    url_rule_class = CIRule

pp = TestPinpointDaily.PinPoint()
app_names2return = pp.get_applications()

# 那么我的flask应用会对URL忽略大小写,\
# 如果不想用这种啰嗦的自定义rule类, 你也可以给你自己的路由单独给出一个小写的url
my_app = CaseInsensitivityFlask(__name__)
# 这样是采用缺省设置(要求大小写)
# my_app = Flask(__name__)


@my_app.route('/')
@my_app.route('/home')
def home_page():
    """
    提供一个首页，说明接口使用方法。
    由于Pinpoint内置的规则，无法查到超过2天的数据，那么要求每个接口URL传入的时间跨度不可超出48小时。
    :return: json
    """
    index_page = "URL接口使用示例:  " \
                 "客户端程序请求全都用GET,；查询时间跨度不可超出48小时！" \
                 "(1)首页可查看有哪些URL可用: http://10.4.94.129:8080/ 或者http://10.4.94.129:8080/home  " \
                 "(2)查看所有已接入Pinpoint的应用列表: http://10.4.94.129:8080/PinpointApplicationsList " \
                 "(3)获取指定时段内所有应用调用链明细: http://10.4.94.129:8080/ppEveryApplicationDetails?from=2019-06-24 20:10:30&to=2019-06-25 20:10:30" \
                 "(4)获取指定时段内单个应用调用链明细: http://10.4.94.129:8080/getSingleAppDetails?app_name=devops_monitor_service&from=2019-06-20 21:05:30&to=2019-06-22 21:05:30"
    return json.dumps(index_page, ensure_ascii=False)


@my_app.route('/PinpointApplicationsList')
@my_app.route('/pinpointapplicationslist')
def get_applications():
    """
    获取所有已接入Pinpoint的应用列表
    http返回码被设为201，取代了Flask默认的200，表示请求已被成功处理
    :return: application/json
    """
    # json.dumps(obj) transform a dict type into a str type.
    json_data = json.dumps(app_names2return, ensure_ascii=False)
    return Response(json_data, 201, mimetype='application/json')


@my_app.route('/ppEveryApplicationDetails', methods=['GET'])
def get_every_app_details_with_time_range():
    """
    获取在指定时间段内(48h)的每个应用的调用链明细
    :return: application/json
    """
    start = request.args.get('from')
    end = request.args.get('to')
    if len(start) == 19 and len(end) == 19:
        timeArray1 = time.strptime(start, '%Y-%m-%d %H:%M:%S')
        from_timestamp = time.mktime(timeArray1)
        timeArray2 = time.strptime(end, '%Y-%m-%d %H:%M:%S')
        to_timestamp = time.mktime(timeArray2)
        timestamp_diff = int(to_timestamp - from_timestamp)
        query_time_range = timestamp_diff / 3600
        if 0 <= query_time_range <= 48:
            every_details_list = list()
            for app in app_names2return:
                one_dict = pp.get_one_app_details(app, start, end)
                every_details_list.append(one_dict)
            # ensure_ascii=False设置浏览器显示中文,若不生效可尝试将浏览器的字符编码改成UTF-8
            json_data = json.dumps(every_details_list, ensure_ascii=False)
            return Response(json_data, 201, mimetype='application/json')
        else:
            error_arg_response = {'error': "GET请求的参数不正确，请根据首页检查后重试"}
            json_data = json.dumps(error_arg_response, ensure_ascii=False)
            return Response(json_data, mimetype='application/json')


@my_app.route('/getSingleAppDetails', methods=['GET'])
def single_app_details():
    """
    获取指定某一个应用的调用链明细
    :return: application/json
    """
    app = request.args.get('app_name')
    start = request.args.get('from')
    end = request.args.get('to')
    if len(start) == 19 and len(end) == 19:
        timeArray1 = time.strptime(start, '%Y-%m-%d %H:%M:%S')
        from_timestamp = time.mktime(timeArray1)
        timeArray2 = time.strptime(end, '%Y-%m-%d %H:%M:%S')
        to_timestamp = time.mktime(timeArray2)
        timestamp_diff = int(to_timestamp - from_timestamp)
        query_time_range = timestamp_diff / 3600
        if 0 <= query_time_range <= 48:
            res = pp.get_one_app_details(app, start, end)
            json_data = json.dumps(res, ensure_ascii=False)
            return Response(json_data, 201, mimetype='application/json')
        else:
            error_arg_response = {'error': "GET请求的参数不正确，请根据首页检查后重试"}
            json_data = json.dumps(error_arg_response, ensure_ascii=False)
            return Response(json_data, mimetype='application/json')
