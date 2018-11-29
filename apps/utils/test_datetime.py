__author__ = 'hewei'
__date__ = '18-11-24'
import time
import uuid
from datetime import datetime, timedelta

start_time = datetime.now()
time.sleep(2.5)
end_time = datetime.now() + timedelta(hours=10)


val = end_time - start_time
print(val, type(val))
print(val.seconds)
a = uuid.uuid1()
print(a, type(a))
s = str(a)
print(s, type(s))

