from calendar import c
from datetime import datetime
from math import e
import os
import random
import re


class DataMakerH3:
    def __init__(self, unit=1, homework=3):
        self.unit = unit
        self.homework = homework
        self.inBrackets = 5

    # 生成一个随机索引
    def _rand_index(self):
        return str(random.choices(range(9), weights=[2, 1, 1, 1, 1, 1, 1, 1, 2])[0])

    # 生成一个随机整数 
    def _rand_int(self):
        return str(random.choices(range(10), weights=[1, 2, 2, 1, 1, 1, 1, 1, 1, 1])[0])

    # 生成一个随机带符号的整数
    def _rand_signed_int(self):
        sign = random.choice(['+', '-'])
        return sign + self._rand_int()

    # 生成一个随机幂
    def _rand_power(self, isY):
        # base = self._rand_int()
        index = self._rand_index()
        if isY:
            return f"y^{index}"
        else:
            return f"x^{index}"

    # 生成一个随机表达式因子
    def _rand_expr_factor(self, isY, hasRecursiveFactor, formal_param, gFunc=False, hFunc=False):
        self.inBrackets = self.inBrackets + 1
        expr = self._rand_expr(isY, hasRecursiveFactor, formal_param, gFunc, hFunc)
        self.inBrackets = self.inBrackets - 1
        if random.random() < 0.4: # 40%的概率不加指数
            return f'({expr})'
        return f'({expr})^{self._rand_index()}'
    
    # 生成一个随机三角函数因子
    def _rand_sin_cos(self, isY, hasRecursiveFactor, formal_param, gFunc=False, hFunc=False):
        self.inBrackets = self.inBrackets + 1
        factor = self._rand_factor(isY, hasRecursiveFactor, formal_param, gFunc, hFunc)
        self.inBrackets = self.inBrackets - 1
        func = random.choice(["sin", "cos"]) + f"(({factor}))" 
        if random.random() < 0.4: # 40%的概率不加指数
            return f'({func})'
        return f'({func})^{self._rand_index()}'

    # 生成一个随机因子
    def _rand_factor(self, isY, hasRecursiveFactor=False, formal_param="", gFunc=False, hFunc=False):
        rand = random.random()
        if rand < 0.2 and self.inBrackets < 3:
            return self._rand_expr_factor(isY, hasRecursiveFactor, formal_param, gFunc, hFunc)
        elif rand < 0.4 and hasRecursiveFactor:
            return self._rand_recursive_factor(formal_param)
        elif rand < 0.5:
            return self._rand_signed_int()
        elif rand < 0.7 and self.inBrackets < 3:
            return self._rand_sin_cos(isY, hasRecursiveFactor, formal_param, gFunc, hFunc)
        elif rand < 0.9 and (gFunc or hFunc):
            return self._rand_normal_factor(hasRecursiveFactor, formal_param, gFunc=gFunc, hFunc=hFunc)
        else:
            return self._rand_power(isY)

    # 生成一个随机项
    def _rand_term(self, isY, hasRecursiveFactor, formal_param, gFunc=False, hFunc=False):
        rand = random.random()
        if rand < 0.4:
            final_term = random.choice(['+ ', '- ']) + self._rand_factor(isY, hasRecursiveFactor, formal_param, gFunc, hFunc)
        else:
            final_term = self._rand_factor(isY, hasRecursiveFactor, formal_param)
        # 随机生成1~10个因子
        for _ in range(random.randint(1, 5)):
            final_term += " * " + self._rand_factor(isY, hasRecursiveFactor, formal_param)
        return final_term

    # 生成一个随机表达式
    def _rand_expr(self, isY, hasRecursiveFactor, formal_param, gFunc=False, hFunc=False):
        if random.random() < 0.5:
            expr = random.choice([' + ', ' - ']) + self._rand_term(isY, hasRecursiveFactor, formal_param, gFunc, hFunc)
        else:
            expr = self._rand_term(isY, hasRecursiveFactor, formal_param, gFunc, hFunc)
        for _ in range(random.randint(0, 2)):
            op = random.choice(['+', '-'])
            expr += f" {op} " + self._rand_term(isY, hasRecursiveFactor, formal_param, gFunc, hFunc)
        return expr

    # 生成一个单独的表达式
    def _generate_single_expr(self, isY ,hasRecursiveFactor, formal_param):
        expr = self._rand_expr(isY, hasRecursiveFactor, formal_param)
        # while True:
        #    if len(expr) < 300:
        #    expr += ' + ' + self._rand_term(isY, hasRecursiveFactor, formal_param)
        #        return expr
        #    else:
        #        continue
        return expr
    
    # 生成自定义函数的表达式（普通和递归）
    def _rand_func_expr(self, formal_param, gFunc=False, hFunc=False):
        if formal_param == "x,y" or formal_param == "y,x":
            func_expr = self._rand_expr(isY=True, hasRecursiveFactor=False, formal_param=formal_param, gFunc=gFunc, hFunc=hFunc)
            if random.random() < 0.5:
                func_expr += self._rand_expr(isY=False, hasRecursiveFactor=False, formal_param=formal_param, gFunc=gFunc, hFunc=hFunc)
        elif formal_param == "y":
            func_expr = self._rand_expr(isY = True, hasRecursiveFactor=False, formal_param=formal_param, gFunc=gFunc, hFunc=hFunc)
        else:
            func_expr = self._rand_expr(isY = False, hasRecursiveFactor=False, formal_param=formal_param, gFunc=gFunc, hFunc=hFunc)
        return func_expr
    
    # 生成f{n}的表达式
    def _rand_recursive_func_expr(self, formal_param):
        if formal_param == "x,y" or formal_param == "y,x":
            sub1_expr = str(random.randint(-10, 10)) + "*f{n-1}" + "(" + self._rand_factor(isY=False) + ", " + self._rand_factor(isY = True) + ")"
            sub2_expr = str(random.randint(-10, 10)) + "*f{n-2}" + "(" + self._rand_factor(isY=False) + ", " + self._rand_factor(isY = True) + ")"
        elif formal_param == "x":
            sub1_expr = str(random.randint(-10, 10)) + "*f{n-1}" + "(" + self._rand_factor(isY=False) + ")"
            sub2_expr = str(random.randint(-10, 10)) + "*f{n-2}" + "(" + self._rand_factor(isY=False) + ")"
        else:
            sub1_expr = str(random.randint(-10, 10)) + "*f{n-1}" + "(" + self._rand_factor(isY = True) + ")"
            sub2_expr = str(random.randint(-10, 10)) + "*f{n-2}" + "(" + self._rand_factor(isY = True) + ")"
        return sub1_expr + "+" + sub2_expr
    
    # 生成随机递归规则
    def _rand_recursive_rule(self, formal_param):
        func_zero = "f{0}" + "(" + formal_param + ")" + "=" + self._rand_func_expr(formal_param)
        func_one = "f{1}" + "(" + formal_param + ")" + "=" + self._rand_func_expr(formal_param)
        func_n = "f{n}" + "(" + formal_param + ")" + "=" + self._rand_recursive_func_expr(formal_param)
        rule_list = [func_zero, func_one, func_n]
        random.shuffle(rule_list)
        return rule_list[0] + "\n" + rule_list[1] + "\n" + rule_list[2] + "\n"
    
    def _rand_recursive_factor(self, formal_param, gFunc=False, hFunc=False):
        index = str(random.randint(0, 5))
        if formal_param == "x,y" or formal_param == "y,x":
            factor = f"f{{{index}}}({self._rand_factor(isY=False, hasRecursiveFactor=True, formal_param=formal_param, gFunc=gFunc, hFunc=hFunc)}, {self._rand_factor(isY=False, hasRecursiveFactor=True, formal_param=formal_param, gFunc=gFunc, hFunc=hFunc)})"
        else:
            factor = f"f{{{index}}}( {self._rand_factor(isY=False, hasRecursiveFactor=True, formal_param=formal_param, gFunc=gFunc, hFunc=hFunc)} )"
        return factor
    
    def _rand_recursive_example(self):
        formal_param = random.choice(["x,y", "x", "y", "y,x"])
        return self._rand_recursive_rule(formal_param) + self._generate_single_expr(isY=False, hasRecursiveFactor=True, formal_param=formal_param)
    
    # 自定义普通函数规则 f(x, y) = sin(x) + y
    def _rand_normal_rule(self, formal_param, num):
        rule = ""
        funcName = ""
        for i in range(num):
            if random.random() < 0.5:
                rule += f"f({formal_param})" + "=" + self._rand_func_expr(formal_param)
            else:
                rule += f"g({formal_param})" + "=" + self._rand_func_expr(formal_param)
        return ""
    
    # 自定义函数因子 g(factor, factor)
    def _rand_normal_factor(self, hasRecursiveFactor, formal_param, gFunc=False, hFunc=False):
        if gFunc: 
            funcName = "g"
        elif hFunc:
            funcName = "h"
        if formal_param == "x,y" or formal_param == "y,x":
            return f"{funcName}({self._rand_factor(isY=False, hasRecursiveFactor=hasRecursiveFactor, formal_param=formal_param)}, {self._rand_factor(isY=False, hasRecursiveFactor=hasRecursiveFactor, formal_param=formal_param)})"
        else:
            return f"{funcName}({self._rand_factor(isY=False, hasRecursiveFactor=hasRecursiveFactor, formal_param=formal_param)})"

    # 生成测试用例
    def generate_test_cases(self, num_cases, data_output_dir):
        """
        生成测试用例
        Args:
            num_cases: 测试用例数量
            output_dir: 输出目录
        
        return:
            None
        """
        if not os.path.exists(data_output_dir):
            os.makedirs(data_output_dir)
        for i in range(num_cases):
            normal_example = "0\n" + self._generate_single_expr(isY=False, hasRecursiveFactor=False, formal_param="") + "\n"
            recursive_example = "1\n" + self._rand_recursive_example() + "\n"
            with open(os.path.join(data_output_dir, f'test{i}.txt'), 'w') as f:
                rand = random.random()
                if rand < 0.5:
                    f.write(normal_example)
                else:
                    f.write(recursive_example)
                
if __name__ == '__main__':
    
    """
    now = datetime.now()
    dic_name = now.strftime("%m%d%H%M%S")
    dataMaker.generate_test_cases(10, "tests_u1h2_" + dic_name)
    """