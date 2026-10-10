# 仅供参考

# asyncio 构成部分：事件循环、协程函数、协程对象、任务和 await
# import asyncio  # 导入
# import datetime
# 事件循环
# event_loop = asyncio.new_event_loop()
# event_loop.run_forever()  # 反复循环，毫无作用
# def hello_printer():
#     print('你好，我是一个低微、简单的打印机，尽管我拥有所有的生活所需--\n新鲜纸张和‘罪犯’伙伴')
# hello_printer()
# def loudmouth_penguin(magic_number:int):
#     print('我是企鹅，比打印机强。'f'顺便问一下我的幸运数字是:{magic_number}')
# loudmouth_penguin(3)    # 调用协程函数
# loudmouth_penguin(magic_number=3) # 调用协程对象
# async def main():     # 定义一个协程函数,调用 fetch(...) 不会立刻执行函数体，而是返回一个协程对象
#     print('hhh')
#     await asyncio.sleep(9)
#     print('嘿嘿恶化')
#     await asyncio.sleep(5)
#     print('aaaa')
#     await asyncio.sleep(5)
# if __name__ == '__main__':
#     asyncio.run(main())
#     print('coroutine main() 结束了')   # 跟睡眠操作无异
# async def hello():  # 错误示例
#     print("hello")
# async def main():
#      asyncio.create_task(hello())   # 后台执行这个，前台继续别的任务
#      asyncio.create_task(main())    # 创建一个协程对象
#      await asyncio.sleep(1)     # 因为协程对象被反复创建导致
#      print("hello")
# asyncio.run(main())

# await的原理和用法
# async def hello():
#     print("hello 任务开始")
#     await asyncio.sleep(0.5)  # 模拟耗时操作
#     print("hello 任务结束")
# async def main():
#     # 1. 创建后台任务
#     task = asyncio.create_task(hello())   # 创建任务，创建任务会自动安排它的执行
#     # 2. main 自己干别的（睡1秒）
#     await asyncio.sleep(1)
#     print("main 睡醒了")
#     # 3. 确保后台任务执行完毕
#     await task
#     print("main 结束")
# asyncio.run(main())
# async def	            定义协程函数	                                async def func():
# await	                挂起当前协程，等待异步操作完成，让出 CPU 给其他任务	await asyncio.sleep(1)
# asyncio.create_task()	将协程立即调度为任务，后台并发执行，不等待	        task = asyncio.create_task(func())
# await task	        等待之前创建的任务完成	                        await task
# asyncio.run()	        启动事件循环，运行主协程	                        asyncio.run(main())

# 协程的内部工作原理
# class Rock:
#     def __await__(self):    # 手动创建__await__函数
#         value_sent_in = yield 7 # 外部发送值，然后接受再赋值给value_sent_in
#         print(f"Rock.__await__ resuming with value: {value_sent_in}.")
#         return value_sent_in    # 赋值后暂停等待
# async def main():
#     print("Beginning coroutine main().")
#     rock = Rock()
#     print("Awaiting rock...")
#     value_from_rock = await rock   # 关键：触发 __await__(也就是上面那个函数)（await rock等价于 yield from rock.__await__()）
#     print(f"Coroutine received value: {value_from_rock} from rock.")
#     return 23
# # 整个 main() 协程如果被驱动，会依次执行打印、实例化、再次打印，然后卡在 await rock 处，把控制权交出去
# coroutine = main()  # 只是创建了协程对象，没有任何输出
# intermediate_result = coroutine.send(None)  # Python 规定，刚创建的生成器/协程，第一次 send 必须传 None，否则报错。
# # 代码先运行一次然后在yield抛出七之后暂停等待下一次发送（send）
# print(f"Coroutine paused and returned intermediate value: {intermediate_result}.")  # 接着这里运行，intermediate_result 是7
# print(f"Resuming coroutine and sending in value: 42.")  # 纯粹是为了凑输出，无实际作用
# try:
#     coroutine.send(42)  # 第二次 send，传入 42。然后全部赋值打印最后再抛出23
# except StopIteration as e:  # 捕获异常
#     returned_value = e.value    # 得到23
# print(f"Coroutine main() finished and provided value: {returned_value}.")

# 手动模拟 asyncio.sleep() 的底层实现,Future 是一个灵活的接口，你可以自定义等待和恢复的条件
import time
# async def other_work():
#     print("I like work. Work work.")
#
# class YieldToEventLoop: # YieldToEventLoop 是让 Python 在用户态死循环看表，这是极其消耗 CPU 的“忙等待”，仅适合用于学习原理，绝对不要用在生产代码里
#     def __await__(self):
#         yield
#
# async def _sleep_watcher(future, time_to_wake):
#     while True:
#         if time.time() >= time_to_wake:
#             future.set_result(None)
#             break
#         else:
#             await YieldToEventLoop()
#
# async def async_sleep(seconds: float):
#     future = asyncio.Future()   # 创建一个空承诺
#     time_to_wake = time.time() + seconds    # seconds：是你传给 async_sleep(3) 的参数，时间戳加传的参数就等于自动可变闹钟
#     # 将监视任务添加到事件循环
#     watcher_task = asyncio.create_task(_sleep_watcher(future, time_to_wake))    #
#     # 阻塞直到 future 被标记为已完成
#     await future    # main 协程在这里暂停，等待这个承诺被兑现
#
# async def main():   # 1、main 协程执行到 await future 时，会挂起自己，把控制权交还给事件循环 2、main 协程被唤醒，继续往下执行
#     # 向事件循环添加一些其他任务，这样在异步休眠时就可以做一些事情
#     work_tasks = [  # 1、事件循环在等待期间，执行这三个任务
#         asyncio.create_task(other_work()),
#         asyncio.create_task(other_work()),
#         asyncio.create_task(other_work())
#     ]
#     print(
#         "Beginning asynchronous sleep at time: "
#         f"{datetime.datetime.now().strftime('%H:%M:%S')}."
#     )
#     await async_sleep(3)
#     print(
#         "Done asynchronous sleep at time: "
#         f"{datetime.datetime.now().strftime('%H:%M:%S')}."
#     )
#     # asyncio.gather 有效地等待集合中的每个任务。（它能一次性并发多个协程，并按顺序收集结果）
#     await asyncio.gather(*work_tasks)
#
# # 关键：启动事件循环
# asyncio.run(main())

# 简单的协程函数（全过程）

# import asyncio
#
# # 1. 定义协程函数：async def,调用后不会立刻执行函数体，而是返回一个协程对象
# async def job(name: str, delay: float = 1.0) -> str:
#     print(f"{name} start")
#     try:
#         await asyncio.sleep(delay)  # 模拟异步 I/O，不要用 time.sleep
#         return f"{name} done"
#     finally:
#         print(f"{name} end")
#
# # 2. 顺序执行：一个 await 完再 await 下一个
# async def serial():
#     a = await job("A", 1)
#     b = await job("B", 1)
#     return a, b
#
# # 3. 并发执行：asyncio.gather
# async def concurrent():
#     results = await asyncio.gather( # asyncio.gather：并发等待多个协程，返回结果顺序与传入顺序一致。
#         job("A", 1),
#         job("B", 2),
#         return_exceptions=True,  # 异常也作为结果返回，不中断其他任务
#     )
#     return results
#
# # 4. 创建 Task：适合后台并发任务
# async def with_tasks():
#     t1 = asyncio.create_task(job("T1", 1))
#     t2 = asyncio.create_task(job("T2", 2))
#
#     # 注意：立即把协程调度成任务。create_task 后最好保存引用，避免任务被垃圾回收
#     r1 = await t1
#     r2 = await t2
#     return r1, r2
#
# # 5. 限流：Semaphore 控制最大并发数
# async def limited(sem: asyncio.Semaphore, name: str, delay: float):
#     async with sem:  # 获取信号量，超过限制就等待
#         return await job(name, delay)
#
# async def with_semaphore():
#     sem = asyncio.Semaphore(3)  # 最多同时 3 个任务
#     tasks = [limited(sem, f"L{i}", 1) for i in range(10)]
#     return await asyncio.gather(*tasks, return_exceptions=True)
#
# # 6. 超时控制：asyncio.wait_for（超时就会抛出时间错误）
# async def with_timeout():
#     try:
#         return await asyncio.wait_for(job("slow", 5), timeout=1)
#     except asyncio.TimeoutError:
#         return "timeout"
#
# # 7. 异步上下文管理器：async with
# class AsyncRes:
#     async def __aenter__(self):
#         print("open")
#         return self
#
#     async def __aexit__(self, exc_type, exc, tb):
#         print("close")
#         return False  # False 表示不吞异常
#     # 返回False或None：不吞异常，异常继续往外抛。返回True：吞掉异常，外层看不到这个异常
#
# async def use_async_with():
#     async with AsyncRes():
#         await asyncio.sleep(0.1)
#
# # 8. 异步迭代器 / 异步生成器：async for
# async def async_gen():
#     for i in range(3):
#         await asyncio.sleep(0.1)
#         yield i
#
# async def use_async_for():
#     out = []
#     async for x in async_gen():
#         out.append(x)
#     return out
#
# # 9. 主入口
# async def main():
#     print(await serial())
#     print(await concurrent())
#     print(await with_tasks())
#     print(await with_semaphore())
#     print(await with_timeout())
#     await use_async_with()
#     print(await use_async_for())
#
# if __name__ == "__main__":
#     asyncio.run(main())