import random
import string
from datetime import datetime


@staticmethod
def generate_message_id():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    random_str = ''.join(random.choices(string.digits, k=6))

    message_id = f"{timestamp}N{random_str}"

    return message_id


