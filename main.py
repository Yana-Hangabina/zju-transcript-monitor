from halo import Halo
from apscheduler.schedulers.blocking import BlockingScheduler
import getpass
import time, datetime, os, sys
import requests, json, re
from tkinter import messagebox
import pandas as pd
pd.set_option('colheader_justify', 'left')

transcript = []
scheduler = []

def _rsa_encrypt(password_str, e_str, M_str):
    password_bytes = bytes(password_str, 'ascii')
    password_int = int.from_bytes(password_bytes, 'big')
    e_int = int(e_str, 16)
    M_int = int(M_str, 16)
    result_int = pow(password_int, e_int, M_int)
    return hex(result_int)[2:].rjust(128, '0')

def check_transcript(username, password):
    global transcript
    global scheduler
    login_url = "https://zjuam.zju.edu.cn/cas/login?service=https%3A%2F%2Fhealthreport.zju.edu.cn%2Fa_zju%2Fapi%2Fsso%2Findex%3Fredirect%3Dhttps%253A%252F%252Fhealthreport.zju.edu.cn%252Fncov%252Fwap%252Fdefault%252Findex"
    request_url = "http://eta.zju.edu.cn/zftal-xgxt-web/api/teacher/xshx/getKccjList.zf"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.66"
    }
    sess = requests.Session()

    spinner = Halo(text='Loading', spinner='dots')

    spinner.start(text='登录到浙大统一身份认证平台...')
    try:
        res = sess.get(login_url, headers=headers)
        execution = re.search('name="execution" value="(.*?)"', res.text).group(1)
        res = sess.get(url='https://zjuam.zju.edu.cn/cas/v2/getPubKey', headers=headers).json()
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
            raise LoginError('登录失败，请核实账号密码重新登录')
        spinner.succeed('已登录到浙大统一身份认证平台')
    except Exception as err:
        spinner.fail(str(err))

    if transcript.empty:
        spinner.start(text='首次获取成绩单中...')
        response = sess.get(request_url, params={'showCount': 999}, headers=headers)
        ts_items = json.loads(response.text)['data']['items']
        transcript = pd.DataFrame(ts_items).drop(['ROW_ID'], axis=1)
        transcript.columns = ['学年', '成绩', '学期', '绩点', '课程名称', '学分']
        transcript = transcript[['学年', '学期', '课程名称', '成绩', '绩点', '学分']]
        print('\n', transcript)
        spinner.succeed('成功获取成绩单！')
    else:
        print("\n[Time] %s" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        new_ts = pd.DataFrame()
        spinner.start(text='获取成绩单中...')
        response = sess.get(request_url, params={'showCount': 999}, headers=headers)
        ts_items = json.loads(response.text)['data']['items']
        new_ts = pd.DataFrame(ts_items).drop(['ROW_ID'], axis=1)
        new_ts.columns = ['学年', '成绩', '学期', '绩点', '课程名称', '学分']
        new_ts = new_ts[['学年', '学期', '课程名称', '成绩', '绩点', '学分']]
        new = len(new_ts) - len(transcript)
        if new > 0:
            transcript = new_ts
            print('\n', transcript.iloc[0:new])
            spinner.succeed('出成绩啦！')
            #messagebox.showinfo("出成绩了吗？", "出成绩啦！")
            scheduler.shutdown()
        else:
            spinner.fail('还没出呢~')
    return

def main():
    print("················🦅 出成绩了吗？················")
    print("····················BY YANA····················")

    # 获取当前绝对路径
    current_path = os.path.abspath(os.path.realpath(os.path.dirname(sys.argv[0])) + os.path.sep + ".")
    print(current_path)

    # 获取浙大通行证账密
    if not os.path.exists(current_path + '\config.json'):
       user = dict()
       user['username'] = input("👤 浙大统一认证用户名: ")
       user['password'] = getpass.getpass("🔑 浙大统一认证密码: ")
       with open(current_path + '\config.json', "w") as configs:
           json.dump(user, configs)
    configs = json.loads(open(current_path + '\config.json', 'r').read())

    # 拉取成绩单
    global transcript
    global scheduler
    transcript = pd.DataFrame()
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    scheduler.add_job(check_transcript, "interval", args=[configs['username'], configs['password']], seconds=10, next_run_time=datetime.datetime.now())
    scheduler.start()

if __name__=="__main__":
    main()

# Exceptions
class LoginError(Exception):
    """Login Exception"""
    pass