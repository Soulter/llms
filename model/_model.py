import abc
import traceback

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

class Model():
    @abc.abstractmethod
    def text_chat(self, prompt: str) -> str:
        pass
    
    @abc.abstractmethod
    def reset_chat(self):
        pass
        