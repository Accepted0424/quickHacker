from datetime import datetime
import os

from dataMaker.unit1.dataMakerH1 import DataMakerH1
from dataMaker.unit1.dataMakerH2 import DataMakerH2
from utils.JavaTools import *
from utils.cmp import compare_expr, compare_match

def test(folder):
    # 编译Java代码
    java_dir = f'{folder}'
    folder = os.path.basename(folder)
    output_filename = f'test_{folder}.jar'
    compile_output_dir = f'out/compiled/{folder}'
    jar_output_dir = './'
    JavaTools.generate_jar(java_dir, output_filename, compile_output_dir, jar_output_dir)
    
    # 生成num_cases个测试用例
    num_cases = 100
    data_output_dir = f'tests_{folder}'
    data_maker = DataMakerH2(unit=1, homework=2)
    data_maker.generate_test_cases(num_cases, data_output_dir)
    
    accepted = 0
    # 逐个运行测试用例
    for i in range(num_cases):
        test_file = os.path.join(data_output_dir, f'test{i}.txt')
        input_expr,output_expr = JavaTools.run_jar(test_file, output_filename)
        
        is_eq, expected_expr = compare_expr(input_expr, output_expr)
        print(f"Test {i} in {folder}:")
        print("Result: " + ("\033[32mAccepted\033[0m" if is_eq else "\033[31mWrong Answer\033[0m"))
        if is_eq:
            accepted += 1
        else:
            print(f"Input:  {input_expr}")
            print(f"Output: {output_expr}")
            print(f"Expected: {expected_expr}")
            
    print("{} Finished: {}/{}".format(folder, accepted, num_cases))

def match(match_folder, test_folder):
    # 编译对拍文件Java代码
    java_dir = f'{match_folder}'
    folder_base_name = os.path.basename(match_folder)
    output_match_filename = f'standard_{folder_base_name}.jar'
    compile_output_dir = f'out/compiled/match/{folder_base_name}'
    jar_output_dir = './'
    JavaTools.generate_jar(java_dir, output_match_filename, compile_output_dir, jar_output_dir)
    
    # 编译测试文件Java代码
    java_dir = f'{test_folder}'
    folder_base_name = os.path.basename(test_folder)
    output_test_filename = f'test_{folder_base_name}.jar'
    compile_output_dir = f'out/compiled/test/{folder_base_name}'
    jar_output_dir = './'
    JavaTools.generate_jar(java_dir, output_test_filename, compile_output_dir, jar_output_dir)
    
    # 生成num_cases个测试用例
    num_cases = 50
    now = datetime.now()
    time = now.strftime("%m%d%H%M%S")
    data_output_dir = f'tests_u1h2_{time}'
    data_maker = DataMakerH2(unit=1, homework=2)
    data_maker.generate_test_cases(num_cases, data_output_dir)
    
    accepted = 0
    # 逐个运行测试用例
    for i in range(num_cases):
        test_file = os.path.join(data_output_dir, f'test{i}.txt')
        input_expr,output_match_expr, match_err = JavaTools.run_jar(test_file, output_match_filename)
        _, output_test_expr, test_err = JavaTools.run_jar(test_file, output_test_filename)
        
        is_eq, expected_expr = compare_match(output_match_expr, output_test_expr)
        print(f"Test {i} in {folder_base_name}:")
        print("Result: " + ("\033[32mAccepted\033[0m" if is_eq else "\033[31mWrong Answer\033[0m"))
        if is_eq:
            accepted += 1
            print(f"Standard: {output_match_expr}")
            print(f"test_Output: {output_test_expr}")
        else:
            print(f"Input:  {input_expr}")
            print(f"Standard: {output_match_expr}")
            print(f"test_Output: {output_test_expr}")
            print(f"Error in standard file: {match_err}")
            print(f"Error in test file: {test_err}")
            
    print("{} Finished: {}/{}".format(folder_base_name, accepted, num_cases))

if __name__ == '__main__':
    test(folder='test.jar')