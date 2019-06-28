# coding:utf-8


import sys

default_path = '/Users/tonykidkid/anaconda2/envs/python36'
sys.path.insert(0, default_path)

import requests
import time
import datetime


class PinPoint(object):
    """
    pinpoint api介绍:
    /applications.pinpoint 获取applications基本信息
    /getAgentList.pinpoint 获取对应application agent信息
    /getServerMapData.pinpoint 获取对应app 基本数据流信息
    # URL1_所有应用的调用链明细(1个Json包含33个应用的dict)： /PinpointAppcationsList'
        传参：from，to
    # URL2_获取单个应用的调用链关系： /pinpointapp/appName?from='yyyy-MM-dd HH:mm:ss'&to='yyyy-MM-dd HH:mm:ss'
        传参：appName，from，to
    """
    def __init__(self):
        self.pp_url = "http://10.4.106.158:8080"
        super(PinPoint, self).__init__()

    def get_applications(self):
        """
        获取已接入pinpoint的应用列表
        return application dict
        """
        applicationListUrl = self.pp_url + "/applications.pinpoint"
        res = requests.get(applicationListUrl)
        appList_jsonList = res.json()
        list_for_show = list()
        if res.status_code != 200:
            print("请求异常,请检查")
            return
        for app_name_dict in appList_jsonList:
            dict_for_show = dict()
            dict_for_show['applicationName'] = app_name_dict.get('applicationName')
            dict_for_show['serviceType'] = app_name_dict.get('serviceType')
            list_for_show.append(dict_for_show)

        app_names2return = list()
        for dic in list_for_show:
            app_names2return.append(dic['applicationName'])
        print(u'\n==== 所有已接入Pinpoint的应用列表 ====\n', app_names2return)
        return app_names2return

    def get_one_app_details(self, appname, start, end, serviceType='SPRING_BOOT'):
        """
        将python的dict类型转换成json类型(str)之后返回
        :param appname: 应用名称
        :param serviceType: 应用类型
        :return json
        """
        # http://10.4.106.158:8080/getServerMapData.pinpoint?applicationName=HPS_APP_PROVIDER&from=1560916290000\
        # &to=1561002700000&callerRange=1&calleeRange=1&serviceTypeName=SPRING_BOOT
        from_ymd_hms = start
        timeArray = time.strptime(from_ymd_hms, '%Y-%m-%d %H:%M:%S')
        datetime_from_timestamp = int(time.mktime(timeArray)) * 1000
        to_ymd_hms = end
        target_timeArray = time.strptime(to_ymd_hms, '%Y-%m-%d %H:%M:%S')
        to_time_stamp = int(time.mktime(target_timeArray)) * 1000
        param = {
            'applicationName': appname,
            'from': datetime_from_timestamp,
            'to': to_time_stamp,
            'callerRange': 1,
            'calleeRange': 1,
            'serviceTypeName': serviceType
        }
        serverMapUrl = "{}{}".format(self.pp_url, "/getServerMapData.pinpoint")
        res = requests.get(serverMapUrl, params=param)
        if res.status_code != 200:
            print("请求异常,请检查")
            return
        links = res.json()["applicationMapData"]["linkDataArray"]  # links列表由3个字典元素组成
        upstream_list = list()
        downstream_details_list = list()
        for link in links:
            # 排除test的应用
            # if 'test' in link['sourceInfo']['applicationName']:
            #     continue
            # 应用名称、应用类型、下游应用名称、下游应用类型、应用节点数、下游应用节点数、\
            # 总请求数、错误请求数、慢请求数(本应用到下一个应用的慢请求数量)
            application = link['sourceInfo']['applicationName']
            serviceType = link['sourceInfo']['serviceType']
            to_application = link['targetInfo']['applicationName']
            to_serviceType = link['targetInfo']['serviceType']
            agents = len(link.get('fromAgent', ' '))
            to_agents = len(link.get('toAgent', ' '))
            totalCount = link['totalCount']
            errorCount = link['errorCount']
            slowCount = link['slowCount']
            if application != appname and serviceType != 'USER':
                upstream_list.append({
                    u'上游应用': application,
                    u'上游应用类型': serviceType,
                    u'上游访问总次数': totalCount,
                    u'上游错误请求次数': errorCount,
                    u'上游慢请求数': slowCount
                })
            elif application != appname and serviceType == 'USER':
                upstream_list.append({
                    u'上游其他应用': 'USER',
                    u'上游应用类型': serviceType,
                    u'上游访问总次数': totalCount,
                    u'上游错误请求次数': errorCount,
                    u'上游慢请求数': slowCount
                })
            else:
                downstream_details_list.append({
                    u'下游应用名': to_application,
                    u'下游应用类型': to_serviceType,
                    u'请求下游的总次数': totalCount,
                    u'对下游的错误请求数': errorCount,
                    u'对下游的慢请求数': slowCount
                })
        print(u"\n《应用 {0} 从 ".format(appname) + start + u'到{}的调用链概况》'.format(end))
        print(u'\n与应用{an}相连的调用链共有{ln}条'.format(an=appname, ln=len(links)))
        print(u'{an}的下游有{down_num}个应用，它们是:\n{down_list}' \
              .format(an=appname, down_num=len(downstream_details_list), down_list=downstream_details_list))
        print(u'{an}的上游有{up_num}个应用，它们是:\n{up_list}' \
              .format(an=appname, up_num=len(upstream_list), up_list=upstream_list))
        daily_report = {
            u"日报时间跨度": '从{}'.format(start) + '到{}'.format(end),
            u"本应用名称": appname,
            u"上游访问本应用明细": upstream_list,
            u"本应用访问下游明细": downstream_details_list
        }
        return daily_report


if __name__ == '__main__':
    pp = PinPoint()
    # pp.get_applications()
    pp.get_one_app_details('HPS_APP_PROVIDER')
    # pp.get_one_app_details('energy-provider-bus-te')
    # pp.update_all_servermaps()
