# Importing Scheduler Module to Schedule Hourly Scans:
from scheduler import Scheduler

# Importing mock
from pytest_mock import mocker


# Importing Datetime
from datetime import timedelta as td

# Importing Time module
import time

class HelloProgram:

    def __init__(self, scheduler):
        self.schedule = scheduler
        

    def schedule_program(self):
        self.schedule.once(td(seconds=1),self.message)


    def message(self):
        introduction = 'hello world'
        return introduction
    

def test_schedule_function():
    scheduler = Scheduler()

    test_program = HelloProgram(scheduler)
    
    assert test_program.message() == 'hello world'

def test_schedule_time(mocker):
    mock_schedule = mocker.Mock()

    test_program = HelloProgram(mock_schedule)

    test_program.schedule_program()

    time.sleep(1.2)

    mock_schedule.once.assert_called_once_with(
        td(seconds=1),
        test_program.message
    )





