from math import e
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

from sympy import Max


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
    mode = 'windows' # 'mac' or 'windows'
    JavaTools.generate_jar(java_dir="../oo_homework_2025_23373112_hw_5", # .java文件所在目录
                           output_filename="code.jar", 
                           external_jar_path="elevator1.jar", # 外部jar包路径
                           compile_output_dir="hw5/compile",
                           jar_output_dir="./", 
                           mode = mode)
    if (mode == 'mac'):
        os.system('chmod +x datainput_student_darwin_m1')
        cmd = "./datainput_student_darwin_m1 | java -jar code.jar"
    elif (mode == 'windows'):
        cmd = ".\\datainput_student_win64.exe | java -jar code.jar"

    # 读取stdin.txt文件，提取乘客数据
    passenger_data = {}
    elevator_data = {}
    for i in range(0, 7):
        elevator_data[i] = {
            "Status": "CLOSE"
        }
    Trun = 0
    average_time = 0
    power_conusmed = 0
    total_pri = 0
    
    
    os.makedirs("log", exist_ok=True)
    output = "log/output_" + time.strftime("%m%d_%H%M%S") + ".txt" 
    with open("stdin.txt", "r") as f:
        line = f.readline()
            
        while line:
            with open(output, "a") as out:
                out.write(line)
            
            match = re.search(r"\[(\d+(\.\d+)?)\]", line)
            if match:
                request_time = float(match.group(1))
                
            line = re.sub(r"\[\d+(\.\d+)?\]\s*", "", line)
            parts = line.strip().split('-')
            entry = {
                "ID": parts[0],
                "PRI": int(parts[2]),
                "FROM": parts[4],
                "TO": parts[6],
                "ELEVATOR": parts[8],
                "REQUEST_TIME": request_time,
                "CONSUME_TIME": 0,
                "ARRIVE": False,
                "INELEVATOR": False,
            }
            total_pri += int(parts[2])
            passenger_data[parts[0]] = entry
            line = f.readline()
        
    timeout = 65
    start_time = time.time()
    error = False
    try:
        # 启动进程
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # 逐行读取并实时打印输出
        
        final_info_time = 0
        for line in iter(process.stdout.readline, ''):
            print(line, end="")
            with open(output, "a") as f:
                f.write(line)
                
            match = re.search(r"\[(.*)?(\d+(\.\d+)?)\]", line)
            if match:
                info_time = float(match.group(1))
                final_info_time = info_time
            
            line = re.sub(r"\[(.*)?\d+(\.\d+)?\]\s*", "", line)
            parts = line.strip().split('-')
            
            if (parts[0] == "ARRIVE"):
                power_conusmed += 0.4
            elif (parts[0] == "OPEN" or parts[0] == "CLOSE"):
                elevator_data[int(parts[2])]["Status"] = parts[0]
                power_conusmed += 0.1
            elif (parts[0] == "OUT"):
                passenger_data[parts[1]]["INELEVATOR"] = False
                if elevator_data[int(parts[3])]["Status"] == "CLOSE":
                    error = True
                    with open(output, "a") as f:
                        f.write("Passenger " + parts[1] + " cannot leave Elevator " + parts[3] + " when the door closed\n")
                    print("\033[31mPassenger", parts[1], "cannot leave Elevator ", parts[3], " when the door closed\033[0m")
                if (parts[2] == passenger_data[parts[1]]["TO"]):
                    passenger_data[parts[1]]["ARRIVE"] = True
                    passenger_data[parts[1]]["CONSUME_TIME"] = (info_time - passenger_data[parts[1]]["REQUEST_TIME"])
                    average_time += passenger_data[parts[1]]["CONSUME_TIME"] * passenger_data[parts[1]]["PRI"]
            elif (parts[0] == "IN"):
                if passenger_data[parts[1]]["INELEVATOR"] == True:
                    error = True
                    with open(output, "a") as f:
                        f.write("Passenger " + parts[1] + " cannot enter Elevator " + parts[3] + " when already in the elevator\n")
                    print("\033[31mPassenger", parts[1], "cannot enter Elevator ", parts[3], " when already in the elevator\033[0m")
                passenger_data[parts[1]]["INELEVATOR"] = True
                if elevator_data[int(parts[3])]["Status"] == "CLOSE":
                    error = True
                    with open(output, "a") as f:
                        f.write("Passenger " + parts[1] + " cannot enter Elevator " + parts[3] + " when the door closed\n")
                    print("\033[31mPassenger", parts[1], "cannot enter Elevator ", parts[3], " when the door closed\033[0m")
            
            # 判断是否超时
            if time.time() - start_time > timeout:
                raise subprocess.TimeoutExpired(cmd, timeout)
            
        average_time /= total_pri
        
        all_arrived = True
        for value in passenger_data.values():
            if value["ARRIVE"] == False:
                all_arrived = False
                with open(output, "a") as f:
                    f.write("Passenger " + value["ID"] + " did not arrive at the destination!\n")
                print("\033[31mPassenger", value["ID"], "did not arrive at the destination!\033[0m")
        
        if all_arrived:
            with open(output, "a") as f:
                f.write("All passengers arrived!\n")
            print("\033[32mAll passengers arrived!\033[0m")
            
        if error:
            with open(output, "a") as f:
                f.write("Error occurred!\n")
            print("\033[31mError occurred! Please check errors in log\033[0m")
                
        with open(output, "a") as f:
            f.write("Run Time: " + str(Max(final_info_time, time.time() - start_time)) + "\n")
            f.write("Average Time: " + str(average_time) + "\n")
            f.write("Power Consumed: " + str(power_conusmed) + "\n")
        print("\033[34mRun Time:", Max(final_info_time, time.time() - start_time), "\033[0m")
        print("\033[34mAverage Time:", average_time, "\033[0m")
        print("\033[34mPower Consumed:", power_conusmed, "\033[0m")
        
        cmd = input("Whether to save the log? (Y/N)\n")
        if cmd == 'Y' or cmd == 'y':
            print("Log saved!")
        elif cmd == 'N' or cmd == 'n':
            os.remove(output)
            print("Log not saved!")
        else:
            print("Invalid input!")

        # 等待进程结束（确保 stderr 也被读取）
        process.stdout.close()
        stderr = process.stderr.read()
        process.wait()

        if stderr:
            print("Error output:", stderr)
    except subprocess.TimeoutExpired:
        print("Process timed out! Killing process...")
        process.kill() 