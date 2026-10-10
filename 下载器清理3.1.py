import os

DIR = "downloads"

if os.path.exists(DIR):
    count = 0
    for filename in os.listdir(DIR):
        # 这里可以改成只删 .part，或者删所有文件
        if filename.endswith(".part") or filename.endswith(".bin"):
            file_path = os.path.join(DIR, filename)
            try:
                os.remove(file_path)
                count += 1
                print(f"已删除: {filename}")
            except Exception as e:
                print(f"删除 {filename} 失败: {e}")
    print(f"清理完成，共删除 {count} 个文件。")
else:
    print("downloads 目录不存在。")