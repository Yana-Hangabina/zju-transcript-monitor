from win10toast import ToastNotifier
#from halo import Halo
#from apscheduler.schedulers.blocking import BlockingScheduler
import getpass
import time
import datetime
import os
import sys
import requests
import json
import re
from pandas import DataFrame

transcript = []
#scheduler = []
# 获取当前绝对路径
current_path = os.path.abspath(os.path.realpath(
    os.path.dirname(sys.argv[0])) + os.path.sep + ".")


def get_passcard():
    global current_path
    print("❗ 获取成绩单需要登录您的浙大通行证，请输入您的账号密码")
    print("❗ 您的账号密码仅保存在本地，请放心使用")
    user = dict()
    user['username'] = input("👤 浙大统一认证用户名: ")
    user['password'] = getpass.getpass("🔒 浙大统一认证密码: ")
    with open(current_path + '\config.json', "w") as configs:
        json.dump(user, configs)
    return
    # return user['username'], user['password']


def _rsa_encrypt(password_str, e_str, M_str):
    password_bytes = bytes(password_str, 'ascii')
    password_int = int.from_bytes(password_bytes, 'big')
    e_int = int(e_str, 16)
    M_int = int(M_str, 16)
    result_int = pow(password_int, e_int, M_int)
    return hex(result_int)[2:].rjust(128, '0')


def check_transcript(username, password):
    global transcript
    #global scheduler
    login_url = "https://zjuam.zju.edu.cn/cas/login?service=https%3A%2F%2Fhealthreport.zju.edu.cn%2Fa_zju%2Fapi%2Fsso%2Findex%3Fredirect%3Dhttps%253A%252F%252Fhealthreport.zju.edu.cn%252Fncov%252Fwap%252Fdefault%252Findex"
    request_url = "http://eta.zju.edu.cn/zftal-xgxt-web/api/teacher/xshx/getKccjList.zf"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.66"
    }
    sess = requests.Session()
    #spinner = Halo(text='Loading', spinner='dots')

    # 登录浙大通行证
    res = sess.get(login_url, headers=headers)
    execution = re.search(
        'name="execution" value="(.*?)"', res.text).group(1)
    res = sess.get(
        url='https://zjuam.zju.edu.cn/cas/v2/getPubKey', headers=headers).json()
    n, e = res['modulus'], res['exponent']
    encrypt_password = _rsa_encrypt(password, e, n)
    data = {
        'username': username,
        'password': encrypt_password,
        'execution': execution,
        '_eventId': 'submit'
    }
    res = sess.post(url=login_url, data=data, headers=headers)

    # 检查登录状态
    if '统一身份认证' in res.content.decode():
        print("⚠ 登录失败，请核实账号密码重新登录")
        get_passcard()
        #username, password = get_passcard()
        #scheduler.modify(args=[username, password])
        return

    # 获取成绩单
    if transcript.empty:
        # spinner.start(text='首次获取成绩单中...')
        print("📊 首次获取成绩单中...")
        response = sess.get(request_url, params={
                            'showCount': 999}, headers=headers)
        ts_items = json.loads(response.text)['data']['items']
        transcript = DataFrame(ts_items).drop(['ROW_ID'], axis=1)
        transcript.columns = ['学年', '成绩', '学期', '绩点', '课程名称', '学分']
        transcript = transcript[['学年', '学期', '课程名称', '成绩', '绩点', '学分']]
        print("📊 成绩单获取成功")
        # spinner.succeed('成功获取成绩单！')
        print(transcript)
        print("⏰ 出分了吗？大兄弟正在监控...")
        # spinner.start(text='出分了吗？大兄弟正在监控...')
    else:
        new_ts = DataFrame()
        response = sess.get(request_url, params={
                            'showCount': 999}, headers=headers)
        ts_items = json.loads(response.text)['data']['items']
        new_ts = DataFrame(ts_items).drop(['ROW_ID'], axis=1)
        new_ts.columns = ['学年', '成绩', '学期', '绩点', '课程名称', '学分']
        new_ts = new_ts[['学年', '学期', '课程名称', '成绩', '绩点', '学分']]
        #new_ts = new_ts.append([{'学年': 0, '学期': 0, '课程名称': 0, '成绩': 0, '绩点': 0, '学分': 0}], ignore_index=True)
        new = len(new_ts) - len(transcript)
        if new > 0:
            transcript = new_ts
            print("💯 %s 出成绩啦！" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            # spinner.succeed('出成绩啦！')
            # spinner.stop_and_persist()
            print(transcript.iloc[0:new])
            toast_info = ""
            for i in range(new):
                toast_info += "🦅 您{}的成绩是{}({})~ ".format(
                    transcript.iloc[i]['课程名称'], transcript.iloc[i]['成绩'], transcript.iloc[i]['绩点'])
            toaster = ToastNotifier()
            toaster.show_toast("出成绩啦！", toast_info,
                               icon_path=None, duration=15, threaded=True)
            # 等待提示框关闭
            # while toaster.notification_active():
            #    time.sleep(0.1)
            #scheduler.reschedule(trigger='date', run_date=datetime(2009, 11, 6, 16, 30, 5))
            control = input("😄 继续监控请按1，退出请按2，人工客服请…没有人工客服：")
            if control == '1':
                print("⏰ 出分了吗？大兄弟正在监控...")
                # spinner.start(text='出分了吗？大兄弟正在监控...')
                #scheduler.reschedule(trigger='interval', seconds=10)
            else:
                sys.exit(0)
        else:
            print("%s 还没出哦~" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return


def main():
    print("················🦅 出成绩了吗？················")
    print("····················BY YANA····················")

    # 获取浙大通行证账密
    global current_path
    if not os.path.exists(current_path + '\config.json'):
        get_passcard()

    # 拉取成绩单
    global transcript
    #global scheduler
    transcript = DataFrame()
    while True:
        configs = json.loads(open(current_path + '\config.json', 'r').read())
        check_transcript(configs['username'], configs['password'])
        time.sleep(300)
    #scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    # scheduler.add_job(check_transcript, "interval", args=[
    #                  configs['username'], configs['password']], seconds=10, next_run_time=datetime.datetime.now(), max_instances=2, coalesce=True)
    # scheduler.start()


if __name__ == "__main__":
    main()
