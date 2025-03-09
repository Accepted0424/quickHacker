import os
import random


class DataMakerH1:
    def __init__(self, unit=1, homework=1):
        self.unit = unit
        self.homework = homework
        self.hasBrackets = False

    # 生成一个随机索引
    def _rand_index(self):
        return str(random.choices(range(9), weights=[2, 1, 1, 1, 1, 1, 1, 1, 2])[0])

    # 生成一个随机整数 
    def _rand_int(self):
        return str(random.choices(range(10), weights=[2, 1, 1, 1, 1, 1, 1, 1, 1, 2])[0])

    # 生成一个随机带符号的整数
    def _rand_signed_int(self):
        sign = random.choice(['+', '-'])
        return sign + self._rand_int()

    # 生成一个随机幂
    def _rand_power(self):
        base = self._rand_int()
        index = self._rand_index()
        return f"{base}*x^{index}"

    # 生成一个随机表达式因子
    def _rand_expr_factor(self):
        self.hasBrackets = True
        expr = self._rand_expr()
        self.hasBrackets = False
        if random.random() < 0.4: # 40%的概率不加指数
            return f'({expr})'
        return f'({expr})^{self._rand_index()}'

    # 生成一个随机因子
    def _rand_factor(self):
        # 50%的概率生成表达式因子，50%的概率生成带符号整数
        if random.random() < 0.5 and not self.hasBrackets:
            return self._rand_expr_factor()
        elif random.random() < 0.2:
            return self._rand_signed_int()
        else:
            return self._rand_power()

    # 生成一个随机项
    def _rand_term(self):
        if random.random() < 0.5:
            final_term = random.choice(['+ ', '- ']) + self._rand_factor()
        else:
            final_term = self._rand_factor()
        # 随机生成1~10个因子
        for _ in range(random.randint(1, 10)):
            final_term += " * " + self._rand_factor()
        return final_term

    # 生成一个随机表达式
    def _rand_expr(self):
        if random.random() < 0.5:
            term = random.choice([' + ', ' - ']) + self._rand_term()
        else:
            term = self._rand_term()
        # 随机生成1~10项
        for _ in range(random.randint(1, 10)):
            op = random.choice(['+', '-'])
            term += f" {op} " + self._rand_term()
        return term

# 生成一个单独的表达式
    def _generate_single_expr(self):
        expr = self._rand_expr()
        # 设置表达式最短长度为30
        while len(expr) < 100:
            expr += ' + ' + self._rand_term()
        return expr

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
            expr = self._generate_single_expr()
            with open(os.path.join(data_output_dir, f'test{i}.txt'), 'w') as f:
                f.write(expr + '\n')
                
if __name__ == '__main__':
    dataMaker = DataMaker()
    dataMaker.generate_test_cases(10, 'tests_u1h1')