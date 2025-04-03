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
    
    def log(str, log_output, color):
        with open(log_output, "a") as f:
            f.write(str)
        if color == "red":
            print("\033[31m" + str + "\033[0m")
        elif color == "green":
            print("\033[32m" + str + "\033[0m")
        elif color == "yellow":
            print("\033[33m" + str + "\033[0m")
        elif color == "blue":
            print("\033[34m" + str + "\033[0m")
        else:
            print(str)
    
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
    schedule_data = {}
    elevator_data = {}
    for i in range(0, 7):
        elevator_data[i] = {
            "STATUS": "CLOSE",
            "INSCHEDULE": False,
            "beforeBegin": True,
            "beforeBeginArriveNum": 0,
            "SPEED": 0.4 # 0.4s/floor
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
            if parts[0] == "SCHE":
                entry = {
                    "ELEVATOR": parts[1],
                    "SPEED": float(parts[2]),
                    "TARGET": int(parts[3]),
                    "DONE": False,
                }
                schedule_data[parts[1]] = entry

            else :
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
            
            if parts[0] == "ARRIVE":
                # 接收到临时调度指令的电梯必须在两次移动楼层操作内输出SCHE-BEGIN-电梯ID开始临时调度动作
                if elevator_data[parts[2]]["beforeBegin"]:
                    elevator_data[parts[2]]["beforeBeginArriveNum"] = elevator_data[parts[2]]["beforeBeginArriveNum"] + 1
                    if elevator_data[parts[2]]["beforeBeginArriveNum"] > 2:
                        error = True
                        JavaTools.log("ERROR: Arrive num exceed 2 After schdule accept before schedule begin ", output, "red")
                power_conusmed += 0.4
                
            elif parts[0] == "RECEIVE":
                if schedule_data[parts[1]] is None or schedule_data[parts[1]]["DONE"] == True:
                    schedule_data[parts[1]] = entry
                    elevator_data[int(parts[1])]["INSCHEDULE"] = True
                    elevator_data[int(parts[1])]["SPEED"] = float(parts[2])
                else:
                    error = True
                    JavaTools.log("ERROR: Elevator " + parts[1] + " has schedule undone!\n", output, "red")
                
            elif parts[0] == "SCHE":
                if (parts[1] == "ACCEPT"):
                    elevator_data[parts[2]]["beforeBegin"] = True
                if (parts[1] == "BEGIN"):
                    if elevator_data[parts[2]]["STATUS"] != "CLOSE":
                        JavaTools.log("ERROR: Schedule begin but door is open", output, "red")
                    elevator_data[parts[2]]["beforeBegin"] = False
                elif (parts[1] == "END"):
                    elevator_data[parts[2]]["INSCHEDULE"] = False
                
            elif (parts[0] == "OPEN" or parts[0] == "CLOSE"):
                if elevator_data[parts[2]]["INSCHEDULE"] and elevator_data[parts[2]]["beforeBegin"] == False:
                    error = True
                    JavaTools.log("ERROR: you can't open or close door in schedule!", output, "red")
                elevator_data[int(parts[2])]["STATUS"] = parts[0]
                power_conusmed += 0.1
                
            elif (parts[0] == "OUT"):
                passenger_data[parts[1]]["INELEVATOR"] = False
                if elevator_data[int(parts[3])]["STATUS"] == "CLOSE":
                    error = True
                    JavaTools.log("Passenger " + parts[1] + " cannot leave Elevator " + parts[3] + " when the door closed\n", output, "red")
                if parts[3] == passenger_data[parts[2]]["TO"] and parts[1] == 'F':
                    passenger_data[parts[1]]["ARRIVE"] = True
                    passenger_data[parts[1]]["CONSUME_TIME"] = (info_time - passenger_data[parts[1]]["REQUEST_TIME"])
                    average_time += passenger_data[parts[1]]["CONSUME_TIME"] * passenger_data[parts[1]]["PRI"]
                elif parts[3] != passenger_data[parts[2]]["TO"] and parts[1] == "S":
                    /* TODO */
                    
            elif parts[0] == "IN":
                if passenger_data[parts[1]]["INELEVATOR"] == True:
                    error = True
                    JavaTools.log("Passenger " + parts[1] + " cannot enter Elevator " + parts[3] + " when already in the elevator\n", output, "red")
                passenger_data[parts[1]]["INELEVATOR"] = True
                if elevator_data[int(parts[3])]["Status"] == "CLOSE":
                    error = True
                    JavaTools.log("Passenger " + parts[1] + " cannot enter Elevator " + parts[3] + " when the door closed\n", output, "red")
            
            # 判断是否超时
            if time.time() - start_time > timeout:
                raise subprocess.TimeoutExpired(cmd, timeout)
            
        average_time /= total_pri
        
        all_arrived = True
        for value in passenger_data.values():
            if value["ARRIVE"] == False:
                all_arrived = False
                JavaTools.log("Passenger " + value["ID"] + " did not arrive at the destination!\n", output, "red")
        
        if all_arrived:
            JavaTools.log("All passengers arrived!\n", output, "green")
            
        if error:
            JavaTools.log("Error occurred!\n", output, "red")
            
        JavaTools.log("Run Time: " + str(Max(final_info_time, time.time() - start_time)) + "\n", output, "blue")
        JavaTools.log("Average Time: " + str(average_time) + "\n", output, "blue")
        JavaTools.log("Power Consumed: " + str(power_conusmed) + "\n", output, "blue")
        
        cmd = input("Whether to save the log? (Y/N)\n")
        if cmd == 'Y' or cmd == 'y':
            print("Log saved!")
        elif cmd == 'N' or cmd == 'n':
            os.remove(output)
            print("Log has been deleted!")
        else:
            os.remove(output)
            print("Log has been deleted!")

        # 等待进程结束（确保 stderr 也被读取）
        process.stdout.close()
        stderr = process.stderr.read()
        process.wait()
        if stderr:
            print("Error output:", stderr)
            
    except subprocess.TimeoutExpired:
        print("Process timed out! Killing process...")
        process.kill() 