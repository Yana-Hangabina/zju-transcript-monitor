# 🦅出成绩了吗？

考试周结束了，摸个浙大出分监控器

- 魔改自[ZJU-nCov-Hitcarder](https://github.com/QSCTech-Sange/ZJU-nCov-Hitcarder)项目
- 数据接口来自[浙江大学三全育人学生信息平台](http://eta.zju.edu.cn/)
- 项目用于学习交流，默认5分钟查询一次，请勿改得太小不然把ETA土豆服务器刷炸了就不妙了

## Usage

### Windows

下载最新[Releases](https://github.com/Yana-Hangabina/zju-transcript-monitor/releases)，开箱即用。

### Others

1. clone 本项目（为了加快 clone 速度，可以指定 clone 深度`--depth 1`，只克隆最近一次 commit），并 cd 到本目录
    ```bash
    $ git clone https://github.com/Yana-Hangabina/zju-transcript-monitor.git --depth 1
    $ cd zju-transcript-monitor
    ```
    
2. 安装依赖

    ```bash
    $ pip3 install -r requirements.txt
    ```

4. 启动监控器

   ```bash
   $ python3 main.py
   ```
