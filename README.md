# 今日校园
**实现今日校园每日疫情自动填写并提交,基本支持各大高校**

**写此项目的初衷是厌烦了每日三餐的疫情重复化填写，加之自己有嗜睡的习惯，也因此时常被辅导喵请喝茶**

**本项目仅供学习交流使用，若侵犯您公司或企业的利益，请及时告知删除**

# 项目说明
- `config.yml`  配置文件
- `jinri.py`  自动化脚本
- `requirements.txt` 脚本依赖的库模块

# 食用方式
## 川信学院的同学
1.clone 项目到本地
```bash
git clone https://github.com/voiin/jinrixiaoyuan.git
```
2.运行脚本
`python jinri.py`

若你有服务器的话，也可配合Windows or Linux定时任务 将项目clone到服务器上

## 其他学院的同学
- 配合config.yml 自行修改url前缀 如 *.cpdaily.com `*`一般为学校简称  `scitc`为本学校
- `login-url`为学校金智系统登录网址,请自己修改
- `defaults`项为默认信息提交方式，也请根据自己学校发布信息为准进行修改或添加

# 说明
1. 此项目基于python3.8环境实现，请提前安装好
2. 项目需要requests selenium等模块 请使用`pip install -r requirements.txt`安装脚本所需模块
3. 模拟登录需要chrome浏览器及[chromedriver](https://chromedriver.storage.googleapis.com/index.html)驱动,驱动版本需与chrome浏览器一致

# 最后

- 此项目开发借鉴了[子墨](https://github.com/ZimoLoveShuang/auto-submit)的开源项目,在此特别感谢！

- 书写不易，觉得不错的话 给个star吧

- 学生一枚，若有不足的地方请各位大佬指点
