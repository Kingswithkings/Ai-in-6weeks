def get_current_time():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def simple_calculator(expression: str):
    try:
        return str(eval(expression))
    except:
        return "Invalid calculation"