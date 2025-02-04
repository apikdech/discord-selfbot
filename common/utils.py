import asyncio
from contextlib import contextmanager
from dataclasses import dataclass
import signal
import math

class ResponseTaskManager:
    def __init__(self):
        self.current_task = None
        self.lock = asyncio.Lock()

    async def set_current_task(self, task):
        async with self.lock:  # Only lock during task switching
            self.cancel_current_task()
            self.current_task = task

    def cancel_current_task(self):
        if self.current_task and not self.current_task.done():
            self.current_task.cancel()

class TimeoutException(Exception):
    pass


@contextmanager
def timeout(seconds):
    def timeout_handler(signum, frame):
        raise TimeoutException("Computation timed out")

    # Set the signal handler and alarm
    original_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # Restore the original handler and disable alarm
        signal.alarm(0)
        signal.signal(signal.SIGALRM, original_handler)


def evaluate_number(s: str):
    s = s.lower()
    import re
    
    # Math function replacements
    math_funcs = {
        r'(?<!math\.)(cos|sin|tan|pi|tau|log|sqrt|floor|ceil|gamma)': r'math.\1',
        r'ln': 'math.log',
        r'[∧^]|pow': '**',
        r'γ': '0.57721566490153286060651209008240243104215933593992',
        r'(?:phi|φ)': '1.61803398874989484820458683436563811772030917980576',
        r'π': 'math.pi',
        r'τ': 'math.tau',
        r'_': '',
        r'[²³⁴⁵⁶⁷⁸⁹]': lambda m: f'**{ord(m.group()) - 0x2070}',
        r'−': '-',
        r'×': '*', 
        r'÷': '/',
        r'√': 'math.sqrt',
        r'fact\(': 'factorial(',
        r'(?<!math\.)factorial': 'math.factorial',
        r'[\'"]': '',
        r'¼': '0.25',
        r'½': '0.5',
        r'¾': '0.75',
        r'⅐': '0.142857',
        r'⅑': '0.111111',
        r'⅒': '0.1',
        r'⅓': '0.333333',
        r'⅔': '0.666667',
        r'⅕': '0.2',
        r'⅖': '0.4',
        r'⅗': '0.6',
        r'⅘': '0.8',
        r'⅙': '0.166667',
        r'⅚': '0.833333',
        r'⅛': '0.125',
        r'⅜': '0.375',
        r'⅝': '0.625',
        r'⅞': '0.875'
    }
    
    for pattern, repl in math_funcs.items():
        s = re.sub(pattern, repl, s)
    if len(s) > 1:
        # Replace e when it's between operators/spaces and numbers (e.g., e+2, 2+e)
        s = re.sub(r'(?<![a-z\d])e(?![a-z\d])', 'math.e', s)
    
    try:
        with timeout(2):  # Set 2 second timeout
            res = eval(s)
            return custom_round(res)
    except TimeoutException:
        print("Computation took too long")
        return -1
    except Exception as e:
        print(f"Error evaluating number: {e}")
        return -1
    
def custom_round(x: float) -> int:
    # check if the floating point number is less than 0.5, if so, return 0, else return 1
    if x - int(x) < 0.5:
        return int(x)
    return int(x) + 1

@dataclass
class NumberState:
    number: int
    valid: bool

@dataclass
class MessageNumber:
    message_id: int
    author_id: int
    number: int
    timestamp: str