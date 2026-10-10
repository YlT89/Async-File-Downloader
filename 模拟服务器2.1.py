from fastapi import FastAPI, Request
# fastapi 是一个现代、高性能的 Python Web 框架，专门用来构建 API。FastAPI 是一个类，用来创建你的 Web 应用实例。Request 是 FastAPI 提供的类，它封装了客户端发来的所有 HTTP 请求信息（比如请求头、请求体、URL 参数等）

from fastapi.responses import StreamingResponse
# StreamingResponse 是 FastAPI 专门提供的一个响应类。普通的响应（比如返回一个字典）会等所有数据准备好后一次性发给客户端；而 StreamingResponse 允许你把数据分块、持续地推送给客户端，这就是“流式响应”的核心

import asyncio
import json

import uvicorn  # 是 ASGI 服务器。FastAPI 只是一个框架，它本身不能监听端口、处理网络连接。需要一个服务器来运行它，uvicorn 就是最常用的那个

# 测试“流式 JSON 读取“

# app = FastAPI() # 实例化一个 FastAPI 应用对象。后续所有的路由、配置都绑定在这个 app 上。uvicorn 启动时，就是去找这个 app
#
# @app.post("/stream")    # 作用：当客户端向 http://127.0.0.1:8000/stream 发送 POST 请求时，就会触发下面这个函数
# async def stream_endpoint(request: Request):    # request: Request是类型注解，告诉上面的FastAPI需要Request类型的参数
#
#     # 接收客户端发来的 JSON
#     body = await request.json() # 是Request对象的方法，作用是读取客户端的请求体（body），并将其解析成字典的格式，如果是不合法的json会报错
#     print(f"服务器收到 JSON: {body}")
#
#     # 定义一个异步生成器，模拟流式返回
#     async def event_generator():    # 异步生成器函数，每次调用yield就吐出一个值，然后暂停，等待再次唤醒
#         for i in range(5):
#             await asyncio.sleep(1)  # 模拟服务器处理耗时
#
#             # 每行返回一个独立的 JSON
#             data = {"id": i, "message": f"数据块 {i}"}
#             yield json.dumps(data) + "\n"   # 如果这里不加 \n，客户端可能会一直等不到换行，导致卡住或者一次性全部返回
#     # json.dumps()，它的作用是将 Python 字典转换成 JSON 格式的字符串（因为 HTTP 传输只能传文本/字节）
#
#     # 返回流式响应
#     return StreamingResponse(event_generator(), media_type="application/x-ndjson")
# 接收两个响应类：前面是上面的异步生成器函数，作用是生成器生成一个数据就发送给客户端，而不是等生成器执行完
# 后面这是 HTTP 响应头中的 Content-Type，application/x-ndjson 表示“换行分隔的JSON(常见格式)，规定了每一行都是一个独立的 JSON 对象。这在客户端代码里按行读取 resp.content 的逻辑完美契合

# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)   # 启动服务器，监听本机 8000 端口（1024-65535都可以）

# 异步大文件下载器本地服务器
app = FastAPI()

# 生成大文件模拟数据流：1MB * 100 = 100MB
async def fake_big_file_generator():
    # 生成 1MB 的二进制数据
    chunk = b"0" * (1024 * 1024)
    for i in range(100):
        # if i == 50: # 测试异常,勿用
        #     raise RuntimeError('服务器模拟崩溃了')
        yield chunk
        # 模拟网络延迟，让下载器能看到进度条在走
        await asyncio.sleep(0.05)

@app.get("/download")
async def download_file():
    # 关键：手动设置 Content-Length，让下载器的进度条能正常工作
    total_size = 2 * 1024 * 1024 * 1024  # 100MB
    headers = {
        "Content-Length": str(total_size),
        "Content-Disposition": "attachment; filename=test.bin"
    }
    return StreamingResponse(
        fake_big_file_generator(),
        media_type="application/octet-stream",
        headers=headers
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)   # http://（加host（想改的话1024-65535都可以）里面的ip地址）（加语法糖里面写的）