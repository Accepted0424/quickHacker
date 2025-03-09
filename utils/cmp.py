import sympy as sp

# 比较两个表达式是否相等
def compare_expr(origin_expr, output_expr):
    """
    比较两个表达式是否相等
    Args:
        origin_expr: 原表达式
        output_expr: Java程序输出的表达式
    return:
        是否相等，预期结果
    """
    try:
        expr1 = sp.sympify(origin_expr)
        expr2 = sp.sympify(output_expr)
        return sp.simplify(expr1 - expr2) == 0, expr1
    except sp.SympifyError:
        return False, expr1
    
def compare_match(match_expr, test_expr):
    """
    比较两个表达式是否相等
    Args:
        match_expr: 对拍文件输出的表达式
        test_expr: 测试文件输出的表达式
    return:
        是否相等，预期结果
    """
    try:
        expr1 = sp.sympify(match_expr)
        expr2 = sp.sympify(test_expr)
        return sp.simplify(expr1 - expr2) == 0, match_expr
    except sp.SympifyError:
        return False, match_expr