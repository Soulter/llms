import traceback
from util.plugin_dev.api.v1.llm import LLMProvider

def retry(n):
    def decorator(func):
        def wrapper(*args, **kwargs):
            err_msg = ""
            for i in range(n):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    traceback.print_exc()
                    print(f"重试第 {i+1} 次...")
                    err_msg = str(e)
            raise Exception(err_msg)
        return wrapper
    return decorator

Model = LLMProvider