from email import errors
import os
from pathlib import Path
import shutil
import subprocess
import time


class JavaTools:
    def __init__(self):
        pass

    def generate_jar(java_dir, output_filename = "test.jar",external_jar_path = "", compile_output_dir = "./out/test", jar_output_dir = "./", mode = "windows"):
        """
        生成jar包
        
        Args:
            java_dir: java文件所在目录
            output_filename: jar包输出文件名
            compile_output_dir: 编译class输出目录
            jar_output_path: jar包输出目录
        
        return: 
            是否成功
        """
        if (mode == 'mac'):
            java_dir = os.path.expanduser(java_dir)
            external_jar_path = os.path.expanduser(external_jar_path)
        
        # 检查compile_output_dir是否存在，不存在则创建
        os.makedirs(compile_output_dir, exist_ok=True)
        
        # 使用os删除compile_output_dir下的所有文件
        if os.path.exists(compile_output_dir):
            for file_name in os.listdir(compile_output_dir):
                file_path = os.path.join(compile_output_dir, file_name)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)  # 删除文件或符号链接
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # 删除子目录
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")
        
        # 编译file_path中的所有java文件
        java_files = list(Path(java_dir).rglob("*.java"))
        print("Found Java files:")
        print("\n".join(str(file) for file in java_files))
        process = subprocess.Popen(
            ['javac', '-d', compile_output_dir, '-encoding', 'utf-8', '-classpath', external_jar_path] + [str(file) for file in java_files],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            if (mode == 'mac'):
                print(f"Error in compiling {java_dir}: {stderr.decode('utf-8', errors='ignore')}")
            elif (mode == 'windows'):
                print(f"Error in compiling {java_dir}: {stderr.decode('gbk', errors='ignore')}")
            return False

        # 生成MANIFEST.MF文件
        with open('MANIFEST.MF', 'w') as f:
            f.write('Main-Class: MainClass\n')
            f.write(f'Class-Path: {os.path.basename(external_jar_path)}\n')

        process = subprocess.Popen(
            ['jar', 'cfm', output_filename, 'MANIFEST.MF', '-C', compile_output_dir, jar_output_dir],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print(f"Error in creating {output_filename}: {stderr.decode('gbk', errors='ignore')}")
            return False
        return True
    
    # 运行测试用例
    def run_jar(test_data_path, test_jar):
        """
        运行测试用例
        
        Args:
            test_data_path: 测试数据文件
            test_jar: 测试jar包
            
        return: 
            jar包运行结果
        """
        with open(test_data_path, 'r') as f:
            input_expr = f.read().strip()
        process = subprocess.Popen(
            ['java', '-jar', test_jar],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        try:
            stdout, stderr = process.communicate(input=input_expr.encode('gbk', errors='ignore'), timeout=5)
            output_expr = stdout.decode('gbk', errors="ignore").strip()
        except subprocess.TimeoutExpired:
            process.kill()  # 终止 Java 进程
            stdout, stderr = process.communicate()  # 获取部分输出
            output_expr = stdout.decode('gbk', errors="ignore").strip()
        err = stderr.decode('gbk', errors='ignore')
        return input_expr, output_expr, err
    
if __name__ == "__main__":
    # 确保elevator1.jar、stdin.txt和datainput_student_win64.exe / datainput_student_darwin_m1在当前目录下
    mode = 'mac' # or 'windows'
    JavaTools.generate_jar(java_dir="~/oo/oo_homework_2025_23373112_hw_5", # .java文件所在目录
                           output_filename="code.jar", 
                           external_jar_path="~/Downloads/elevator1.jar", # 外部jar包路径
                           compile_output_dir="hw5/compile",
                           jar_output_dir="./", 
                           mode = mode)
    if (mode == 'mac'):
        os.system('chmod +x datainput_student_darwin_m1')
        cmd = "./datainput_student_darwin_m1 | java -jar code.jar"
    elif (mode == 'windows'):
        cmd = ".\\datainput_student_win64.exe | java -jar code.jar"
              
    timeout = 100
    start_time = time.time()
    try:
        # 启动进程
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # 逐行读取并实时打印输出
        for line in iter(process.stdout.readline, ''):
            print(line, end="")  # 直接输出，不要额外换行
            if time.time() - start_time > timeout:
                raise subprocess.TimeoutExpired(cmd, timeout)

        # 等待进程结束（确保 stderr 也被读取）
        process.stdout.close()
        stderr = process.stderr.read()
        process.wait()

        if stderr:
            print("Error output:", stderr)
    except subprocess.TimeoutExpired:
        print("Process timed out! Killing process...")
        process.kill() 
    