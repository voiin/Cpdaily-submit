# coding: utf-8
import sys
import requests
import json
import yaml
import random
import oss2
from urllib.parse import urlparse
from urllib3.exceptions import InsecureRequestWarning
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from datetime import datetime, timedelta, timezone

# debug模式
debug = False
if debug:
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 读取yml配置
def getYmlConfig(yaml_file='config.yml'):
    file = open(yaml_file, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    config = yaml.load(file_data, Loader=yaml.FullLoader)
    return dict(config)

# 全局配置
config = getYmlConfig()
rand = random.randint(363,372)/10

headers = {
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; vmos Build/LMY48G; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Mobile Safari/537.36  cpdaily/8.2.2 wisedu/8.2.2',
    'content-type': 'application/json',
    'Accept-Encoding': 'gzip,deflate',
    'Accept-Language': 'zh-CN,en-US;q=0.8',
    'Content-Type': 'application/json;charset=UTF-8'
}

submitHeaders = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; MI 9 Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 okhttp/3.8.1',
    'CpdailyStandAlone': '0',
    'Cpdaily-Extension': 'RADCSRminiMgqqlqqEeUIlGO1ivakMDZTJtYYN8fwbnuQ2vxpCSovbApowOc hQFZE4yLOkuCm0dSLgpTi27Z9JO5pnFLmjkMt6M3efLkTVuhv9qrhJ6Y4YSn xepXhPCDK8aX9PslM+hgsRPqz8JEA8IDK/F7Bw93AP1S/1Dg6XSdX/EjSb1w cbFBjlmeC6GvUSELsGD1B6DMIQbTYuGRpnnd34DiICWuko0pou0yAuHOSLSY QHQzrcGoQV/VFulz',
    'extension': '1',
    'Content-Type': 'application/json; charset=utf-8',
    'Host': 'scitc.cpdaily.com',
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip'
}

# 获取今日校园api
def getCpdailyApis(user):
    apis = {}
    user = user['user']
    schools = requests.get(url='https://www.cpdaily.com/v6/config/guest/tenant/list', verify=not debug).json()['data']
    flag = True
    for one in schools:
        if one['name'] == user['school']:
            if one['joinType'] == 'NONE':
                log(user['school'] + ' 未加入今日校园')
                exit(-1)
            flag = False
            params = {
                'ids': one['id']
            }
            res = requests.get(url='https://www.cpdaily.com/v6/config/guest/tenant/info', params=params,
                               verify=not debug)
            data = res.json()['data'][0]
            joinType = data['joinType']
            idsUrl = data['idsUrl']
            ampUrl = data['ampUrl']
            ampUrl2 = data['ampUrl2']
            if 'campusphere' in ampUrl or 'cpdaily' in ampUrl:
                parse = urlparse(ampUrl)
                host = parse.netloc
                apis['login-url'] = idsUrl + '/login?service=' + parse.scheme + r"%3A%2F%2F" + host + r'%2Fportal%2Flogin'
                apis['host'] = host
            if 'campusphere' in ampUrl2 or 'cpdaily' in ampUrl2:
                parse = urlparse(ampUrl2)
                host = parse.netloc
                apis['login-url'] = idsUrl + '/login?service=' + parse.scheme + r"%3A%2F%2F" + host + r'%2Fportal%2Flogin'
                apis['host'] = host
            if joinType == 'NOTCLOUD':
                res = requests.get(url=apis['login-url'], verify=not debug)
                if urlparse(apis['login-url']).netloc != urlparse(res.url):
                    apis['login-url'] = res.url
            break
    if flag:
        log(user['school'] + ' 未找到该院校信息，请检查是否是学校全称错误')
        exit(-1)
    log(apis)
    return apis

# 获取当前utc时间，并格式化为北京时间
def getTimeStr():
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    return bj_dt.strftime("%Y-%m-%d %H:%M:%S")

# 输出调试信息，并及时刷新缓冲区
def log(content):
    print(getTimeStr() + ' ' + str(content))
    sys.stdout.flush()

# 登陆并获取cookies
def getSession(user, loginUrl):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    brower = webdriver.Chrome(options=options)
    brower.get(loginUrl)
    brower.find_element_by_id('username').send_keys(user['user']['username'])
    brower.find_element_by_id('password').send_keys(user['user']['password'])
    brower.find_element_by_class_name('auth_login_btn').click()
    wait = WebDriverWait(brower, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'icon-aixin')))
    cookiestr = brower.get_cookies()
    brower.close()
    # 解析cookie
    #cookies = requests.cookies.RequestsCookieJar()
    cookies = {}
    for line in cookiestr:
        name,value = line['name'],line['value']
        cookies[name] = value
    session = requests.session()
    session.cookies = requests.utils.cookiejar_from_dict(cookies)
    return session

# 查询问卷表单
def queryForm(session, host):
    queryCollectWidUrl = 'https://{host}/wec-counselor-collector-apps/stu/collector/queryCollectorProcessingList'.format(host=host)
    params = {
        'pageSize': 6,
        'pageNumber': 1
    }
    res = session.post(queryCollectWidUrl, headers=headers, data=json.dumps(params), verify=not debug)
    if len(res.json()['datas']['rows']) < 1:
        return None
    collectWid = res.json()['datas']['rows'][0]['wid']
    formWid = res.json()['datas']['rows'][0]['formWid']

    detailCollector = 'https://{host}/wec-counselor-collector-apps/stu/collector/detailCollector'.format(host=host)
    res = session.post(url=detailCollector, headers=headers,
                       data=json.dumps({"collectorWid": collectWid}), verify=not debug)
    schoolTaskWid = res.json()['datas']['collector']['schoolTaskWid']

    getFormFields = 'https://{host}/wec-counselor-collector-apps/stu/collector/getFormFields'.format(host=host)
    res = session.post(url=getFormFields, headers=headers, data=json.dumps(
        {"pageSize": 100, "pageNumber": 1, "formWid": formWid, "collectorWid": collectWid}), verify=not debug)
    form = res.json()['datas']['rows']

    return {'collectWid': collectWid, 'formWid': formWid, 'schoolTaskWid': schoolTaskWid, 'form': form}

# 填写form
def fillForm(session, form):
    for formItem in form[:]:
        # 只处理必填项
        if formItem['isRequired'] == 1:
            sort = int(formItem['sort'])
            default = config['cpdaily']['defaults'][sort - 1]['default']
            if formItem['title'] != default['title']:
                log('第%d个默认配置不正确，请检查' % sort)
                exit(-1)
            # 文本直接赋值
            if formItem['fieldType'] == 1:
                formItem['value'] = default['value']
            if formItem['title'] in '实测体温（℃）':
                formItem['value'] = rand
            # 单选框需要删掉多余的选项
            if formItem['fieldType'] == 2:
                # 填充默认值
                formItem['value'] = default['value']
                fieldItems = formItem['fieldItems']
                for i in range(0, len(fieldItems))[::-1]:
                    if fieldItems[i]['content'] != default['value']:
                        del fieldItems[i]
            # 多选需要分割默认选项值，并且删掉无用的其他选项
            if formItem['fieldType'] == 3:
                fieldItems = formItem['fieldItems']
                defaultValues = default['value'].split(',')
                for i in range(0, len(fieldItems))[::-1]:
                    flag = True
                    for j in range(0, len(defaultValues))[::-1]:
                        if fieldItems[i]['content'] == defaultValues[j]:
                            # 填充默认值
                            formItem['value'] += defaultValues[j] + ' '
                            flag = False
                    if flag:
                        del fieldItems[i]
            log('必填问题%d：' % sort + formItem['title'])
            log('答案%d：' % sort + formItem['value'])
            sort += 1
        else:
            form.remove(formItem)
    return form

# 提交表单
def submitForm(formWid, address, collectWid, schoolTaskWid, form, session, host):
    params = {"formWid": formWid, "address": address, "collectWid": collectWid, "schoolTaskWid": schoolTaskWid,
              "form": form}
    submitForm = 'https://{host}/wec-counselor-collector-apps/stu/collector/submitForm'.format(host=host)
    res = session.post(url=submitForm, headers=submitHeaders, data=json.dumps(params), verify=not debug)
    msg = res.json()['message']
    return msg

#查询查寝表单
def sleepCheckFrom(session, host):
    querySignWid = 'https://{host}/wec-counselor-attendance-apps/student/attendance/getStuAttendacesInOneDay'.format(host=host)
    res = session.post(url=querySignWid, headers=headers, verify=not debug)
    signInstanceWid = res.json()['datas']['unSignedTasks'][0]['signInstanceWid']
    signWid = res.json()['datas']['unSignedTasks'][0]['signWid']

    queryCoordinate = 'https://{host}/wec-counselor-attendance-apps/student/attendance/detailSignInstance'.format(host=host)
    res = session.post(url=queryCoordinate, headers=headers, data=json.dumps(
        {"signInstanceWid": signInstanceWid, "signWid": signWid}), verify=not debug)
    longitude = res.json()['datas']['signPlaceSelected'][0]['longitude']
    latitude =  res.json()['datas']['signPlaceSelected'][0]['latitude']

    return {'signInstanceWid': signInstanceWid, 'signWid': signWid, 'longitude': longitude, 'latitude': latitude}

# 上传图片到阿里云oss
def uploadPicture(session, image, host):
    url = 'https://{host}/wec-counselor-collector-apps/stu/collector/getStsAccess'.format(host=host)
    res = session.post(url=url, headers={'content-type': 'application/json'}, data=json.dumps({}), verify=not debug)
    datas = res.json().get('datas')
    fileName = datas.get('fileName')
    accessKeyId = datas.get('accessKeyId')
    accessSecret = datas.get('accessKeySecret')
    securityToken = datas.get('securityToken')
    endPoint = datas.get('endPoint')
    bucket = datas.get('bucket')
    bucket = oss2.Bucket(oss2.Auth(access_key_id=accessKeyId, access_key_secret=accessSecret), endPoint, bucket)
    with open(image, "rb") as f:
        data = f.read()
    bucket.put_object(key=fileName, headers={'x-oss-security-token': securityToken}, data=data)
    res = bucket.sign_url('PUT', fileName, 60)
    # log(res)
    return fileName

# 获取图片上传位置
def getPictureUrl(session, fileName, host):
    url = 'https://{host}/wec-counselor-collector-apps/stu/collector/previewAttachment'.format(host=host)
    data = {
        'ossKey': fileName
    }
    res = session.post(url=url, headers={'content-type': 'application/json'}, data=json.dumps(data), verify=not debug)
    photoUrl = res.json().get('datas')
    return photoUrl

#提交查寝表单
def submitSign(signInstanceWid, longitude, latitude, photoUrl, position, session, host):
    submitSign = 'https://{host}/wec-counselor-attendance-apps/student/attendance/submitSign'.format(host=host)
    res = session.post(url=submitSign, headers=submitHeaders, data=json.dumps(
        {"signInstanceWid": signInstanceWid, "longitude": longitude, "latitude": latitude,
         "isMalposition": 0, "abnormalReason": "", "signPhotoUrl": photoUrl, "position": position,
         "qrUuid": ""}))
    msg = res.json()['message']
    return msg

#疫情填报启动函数
def formMain(user, session, host):
    log('正在查询最新待填写问卷。。。')
    params = queryForm(session, host)
    if str(params) == 'None':
        log('获取最新待填写问卷失败，可能是辅导员还没有发布。。。')
        exit(-1)
    log('查询最新待填写问卷成功。。。')
    log('正在自动填写问卷。。。')
    form = fillForm(session, params['form'])
    log('填写问卷成功。。。')
    log('正在自动提交。。。')
    msg = submitForm(params['formWid'], user['user']['address'], params['collectWid'],
                     params['schoolTaskWid'], form, session, host)
    return msg

#查寝拍照启动函数
def photoMain(user,session,host):
    log('正在查询最新待拍照的查寝表单。。。')
    params = sleepCheckFrom(session, host)
    if str(params) == 'None':
        log('获取最新待拍照的查寝表单失败，可能是辅导员还没有发布。。。')
        exit(-1)
    log('查询最新待拍照的查寝表单成功。。。')
    log('正在自动上传图片至阿里云oss。。。')
    fileName = uploadPicture(session,config['photo']['url'], host)
    photoUrl = getPictureUrl(session,fileName, host)
    log('上传图片至阿里云oss成功。。。')
    log('正在自动提交。。。')
    msg = submitSign(params['signInstanceWid'], params['longitude'],
                     params['latitude'], photoUrl, user['user']['address'], session, host)
    return msg

# 启动主函数
def main():
    try:
        for user in config['users']:
            log('当前用户：' + str(user['user']['username']))
            apis = getCpdailyApis(user)
            log('脚本开始执行。。。')
            log('开始模拟登陆。。。')
            session = getSession(user, apis['login-url'])
            if session != 'None':
                log('模拟登陆成功。。。')
                nowHours = datetime.now().strftime("%H")
                if nowHours not in range(18, 24):
                    msg = formMain(user, session, apis['host'])
                else:
                    msg = photoMain(user, session, apis['host'])
                if msg == 'SUCCESS':
                    log('自动提交成功！')
                    sendMessage(user['user']['email'], '自动提交成功！')
                elif msg == '该收集已填写无需再次填写':
                    log('今日已提交！')
                    sendMessage(user['user']['email'], '自动提交成功！')
                else:
                    log('自动提交失败。。。')
                    log('错误是' + msg)
                    sendMessage(user['user']['email'], '自动提交失败！错误是' + msg)
                    exit(-1)
            else:
                log('模拟登陆失败。。。')
                log('原因可能是学号或密码错误，请检查配置后，重启脚本。。。')
                exit(-1)
    except Exception as e:
        raise e
    else:
        return 'auto submit success.'

# 发送邮件通知
def sendMessage(send,msg):
    if send != '':
        log('正在发送邮件通知。。。')
        res = requests.post('https://voiin.com/sendmail', data=json.dumps({'title': '今日校园疫情上报自动提交结果通知', 'content': getTimeStr() + msg, 'to': send}))
        res.encoding = 'utf-8'
        code = res.json()['code']
        if code == 0:
            log('发送邮件通知成功。。。')
        else:
            log('发送邮件通知失败。。。')
            log(res.json()['msg'])


if __name__ == '__main__':
    main()


