# 异步 I/O：等待网络数据时不阻塞整个程序，可以同时处理多个下载任务。

# 流式读取：不把整个文件一次性读进内存，而是分块读取、分块写入。

# 适合大文件：几 GB、几十 GB 的文件也不会撑爆内存。

# 可并发：可以同时下载多个文件，或对同一个文件开多个连接分段下载

# 核心：用异步和流式处理，高效、低内存地下载大文件

# 注意：异步不等于多线程，也不等于一定更快。它主要解决 I/O 等待 问题。如果带宽已经跑满，再增加并发也不会让总速度更快

import aiofiles # pip install aiohttp aiofiles
import asyncio
import aiohttp
import os

async def download_one(session,url,path,sem,chunk_size=1024 * 1024):
    async with sem:
        tmp_path = path + '.part'
        try:
            timeout = aiohttp.ClientTimeout(
                total=None,         # 总时间不限，适合大文件
                sock_connect=30,    # 连接超时 30 秒
                sock_read=60        # 读取超时 60 秒
            )
            async with session.get(url,timeout=timeout) as resp:
                resp.raise_for_status()
                total = int(resp.headers.get('content-length',0))
                downloaded = 0

                async with aiofiles.open(tmp_path,'wb') as f:             # aiofiles 异步写文件
                    async for chunk in resp.content.iter_chunked(chunk_size):   # iter_chunked 流式读取
                        await f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            percent = downloaded / total * 100
                            print(f'{url}已下载{percent:.1f}%')    # 1f之前学的，保留一位小数的浮点数

            os.replace(tmp_path,path)   # 把tmp_path(临时文件重命名)移动到path(最终路径)注意记得这俩文件在同一个目录下
            print(f'{url}下载完成 ->{path}')

        except Exception as e:
            print(f'{url}下载完成 ->{path}')

        # except BaseException as e:  # 【修改】由 Exception 改为 BaseException，测试勿用
        #     print(f"\n{url} 下载中断: {type(e).__name__} - {e}")
        #     # 释放文件句柄后，尝试清理残留
        #     if os.path.exists(tmp_path):
        #         try:
        #             os.remove(tmp_path)
        #             print(f"已清理临时文件: {tmp_path}")
        #         except Exception as clean_err:
        #             print(f"清理失败: {clean_err}")
            raise

async def main():
    urls = [
        'http://127.0.0.1:8080/download',    # 改成你本地服务器的地址
        'http://127.0.0.1:8080/download',    # 多填几个测试并发
        ''  # 你也可以你需要的其他东西输入对应的url就行（别去搞一些有的没的，务必遵守目标网站的 robots.txt，不要搞一些商业或恶意爬取）
    ]
    os.makedirs('downloads',exist_ok=True)  # 创建目录:如果目录已存在也不报错,如果改成False就会抛出异常

    sem = asyncio.Semaphore(3)  # 限流，最多同时下载 3 个

    async with aiohttp.ClientSession() as session:
        tasks = [
            download_one(session,u,f'downloads/{i}.bin',sem=sem)
            for i,u in enumerate(urls)
        ]

        # 接收结果，包括异常
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 【新增】遍历结果，把异常打印出来,以下注释为测试勿用
        # for i, res in enumerate(results):
        #     if isinstance(res, Exception):
        #         print(f"任务 {i} 失败: {res}")

if __name__ == '__main__':
    asyncio.run(main())

    # 用完关机之前记得运行一下清理器（模块导入也行看你自己）