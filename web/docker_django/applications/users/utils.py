from datetime import (
    datetime,
    timedelta,
)

def get_dept_final_date():
    return datetime.now() + timedelta(days=30000)