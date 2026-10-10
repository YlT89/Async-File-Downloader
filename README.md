# 异步大文件下载器
基于 aiohttp 和 asyncio 的异步并发大文件下载器，附带 FastAPI 模拟流式服务器。
## 功能特性
- 异步并发下载（asyncio.gather）
- 并发限流控制（asyncio.Semaphore）
- 流式分块读取写入（iter_chunked + aiofiles）
- 实时进度条显示
- 异常捕获与临时文件清理（.part）
## 运行方法
1. 安装依赖: `pip install -r requirements`
2. 启动模拟服务器: `python 模拟服务器2.1.py`
3. 运行下载器: `python 异步大文件下载器3.py`