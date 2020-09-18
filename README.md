# 今日校园自动签到脚本

**今日校园每日疫情填报和夜间查寝自动提交并邮件通知,通用各大高校**

**写此项目的初衷是厌烦了每日三餐的疫情重复化填写，加之自己有嗜睡的习惯，也因此时常被辅导喵请喝茶😀**


# 开发环境
- Win10, Python3.8, PyCharm 2020.2.1 (Community Edition)
- 模拟登录需要chrome浏览器及[chromedriver](https://chromedriver.storage.googleapis.com/index.html)驱动,驱动版本需与chrome浏览器一致

# 项目说明
- 📄`config.yml`  配置文件
- 🍩`jinri.py`  自动化脚本
- 🍕`generate.py` 配置文件生成
- 🍥`requirements.txt` 脚本依赖的库模块


# 食用方式
## 川信学院的同学
1. clone 或下载项目到本地
```bash
git clone https://github.com/voiin/Cpdaily-submit.git
```
2. 安装脚本所需依赖库
```bash
pip install -r requirements.txt
```
3. 打开config.yml文件，修改相应的今日校园登录学号密码等信息
4. 运行
```bash
python index.py
```
配合Windows or Linux服务器定时任务即可实现自动化运行

## 其他学院的同学

**根据自己学院疫情填报选项，运行`python generate.py`生成对应的填报配置信息**

# 关于邮件接口限制
> 为了防止接口被滥用的情况，一个IP在1个小时内只能进行5次请求。
# 更新日志
> 优化代码结构，新增邮件接口IP访问限制

# 最后

- 如果本项目或多或少帮助到了你，请给个⭐再走吧
- 学生一枚，代码不足的地方请多指教


