import re

with open("backtest_logic.py", "r", encoding="utf-8") as f:
    content = f.read()

# Mock Streamlit
mock_code = """
class MockSt:
    class session_state_class(dict):
        def __getattr__(self, item):
            return self.get(item)
        def __setattr__(self, key, value):
            self[key] = value

    session_state = session_state_class()
    session_state["USE_PHASE_11"] = True

    @staticmethod
    def cache_data(ttl=None):
        def decorator(func):
            return func
        return decorator
    
    @staticmethod
    def markdown(*args, **kwargs): pass
    @staticmethod
    def title(*args, **kwargs): pass
    @staticmethod
    def caption(*args, **kwargs): pass
    @staticmethod
    def set_page_config(*args, **kwargs): pass
    @staticmethod
    def sidebar(*args, **kwargs): return MockContext()
    @staticmethod
    def header(*args, **kwargs): pass
    @staticmethod
    def selectbox(*args, **kwargs): return "6/55"
    @staticmethod
    def success(*args, **kwargs): pass
    @staticmethod
    def warning(*args, **kwargs): pass
    @staticmethod
    def info(*args, **kwargs): pass
    @staticmethod
    def error(*args, **kwargs): pass
    @staticmethod
    def multiselect(*args, **kwargs): return []
    @staticmethod
    def radio(*args, **kwargs): return "Hiện đại"
    @staticmethod
    def button(*args, **kwargs): return False
    @staticmethod
    def progress(*args, **kwargs): return MockContext() # progress bar
    @staticmethod
    def empty(*args, **kwargs): return MockContext()
    @staticmethod
    def toast(*args, **kwargs): pass
    @staticmethod
    def tabs(*args, **kwargs): return [MockContext(), MockContext()]
    @staticmethod
    def subheader(*args, **kwargs): pass
    @staticmethod
    def columns(*args, **kwargs): return [MockContext(), MockContext()]
    @staticmethod
    def select_slider(*args, **kwargs): return 10
    @staticmethod
    def spinner(*args, **kwargs): return MockContext()
    @staticmethod
    def expander(*args, **kwargs): return MockContext()
    @staticmethod
    def date_input(*args, **kwargs): 
        from datetime import datetime
        return datetime.now().date()
    @staticmethod
    def write(*args, **kwargs): pass
    @staticmethod
    def rerun(*args, **kwargs): pass

class MockContext:
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): pass
    def progress(self, *args): pass
    def text(self, *args): pass
    def empty(self): pass
    def header(self, *args): pass
    def __getattr__(self, name): return lambda *args, **kwargs: None

import sys
sys.modules["streamlit"] = MockSt
import streamlit as st
"""

# Remove `import streamlit as st` from valid imports if possible, or just prepend the mock
# Actually, since python executes top-down, if we inject the mock BEFORE the file content, it works.
# But `app.py` has `import streamlit as st`.
# If `sys.modules["streamlit"]` is set, `import streamlit` returns it.

final_content = mock_code + "\n# ORIGINAL CONTENT BELOW\n" + content

# We also need to guard main() execution
final_content = final_content.replace('if __name__ == "__main__":', 'if False and __name__ == "__main__":')

with open("backtest_logic.py", "w", encoding="utf-8") as f:
    f.write(final_content)

print("Sanitized backtest_logic.py")
