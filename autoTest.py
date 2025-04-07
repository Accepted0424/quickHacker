import os
import subprocess

# 定义文件夹路径和目标 Python 脚本路径
folder_path = 'testcase'  # 替换为实际的文件夹路径
python_script = './utils/quickInput_elevator2_refactor.py'  # 替换为实际的 Python 脚本文件路径

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)

    # 只处理文件，忽略文件夹
    if os.path.isfile(file_path):
        # 将文件内容写入 stdin.txt
        with open(file_path, 'r') as f:
            content = f.read()

        os.remove('stdin.txt')
        with open('stdin.txt', 'w') as stdin_file:
            stdin_file.write(content)

        # 启动目标 Python 文件中的 main 函数
        subprocess.run(['python', python_script])
