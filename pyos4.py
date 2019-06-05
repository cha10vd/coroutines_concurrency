from queue import Queue
from time import sleep


#------------------------------------------------------------------------------
# System calls
#------------------------------------------------------------------------------
class SystemCall(object):
    ''' base class for more complex system calls'''
    def handle(self):
        pass


class GetTid(SystemCall):
    def handle(self):
        self.task.sendval = self.task.tid
        self.sched.schedule(self.task)


class NewTask(SystemCall):
    def __init__(self,target):
        self.target = target
    def handle(self):
        tid = self.sched.new(self.target)
        self.task.sendval = tid
        self.sched.schedule(self.task)


class KillTask(SystemCall):
    def __init__(self,tid):
        self.tid = tid
    def handle(self):
        task = self.sched.taskmap.get(self.tid,None)
        if task:
            task.target.close()
            self.task.sendval = True
        else:
            self.task.sendval = False
        self.sched.schedule(self.task)

#------------------------------------------------------------------------------
# Task class
#------------------------------------------------------------------------------
class Task(object):
    ''' Wrapper object for coroutines'''
    taskid = 0
    def __init__(self, target):
        Task.taskid += 1
        self.tid     = Task.taskid  # Task ID
        self.target  = target       # Target coroutine
        self.sendval = None         # Value to send
    def run(self):
        return self.target.send(self.sendval)


#------------------------------------------------------------------------------
# Our model OS
#------------------------------------------------------------------------------
class Scheduler(object):
    ''' Our operating system of sorts'''
    def __init__(self):
        ''' Set up a queue and a dictionary of tid:task entries'''
        self.ready = Queue() # FIFO array
        self.taskmap = {}

    def new(self, target):
        newtask = Task(target)
        self.taskmap[newtask.tid] = newtask
        self.schedule(newtask)
        return newtask.tid

    def schedule(self, task):
        self.ready.put(task)

    def exit(self,task):
        print(f"task {task.tid} terminated")
        del self.taskmap[task.tid]

    def mainloop(self):
        while self.taskmap: # i.e. while taskmap not empty
            task = self.ready.get() # Pull next item from front of array
            try:
                result = task.run()
                if isinstance(result, SystemCall):
                    result.task  = task # Record task responsible for sys call
                    result.sched = self # Record parent scheduler
                    result.handle()     # Carry out system call action
                    continue
            except StopIteration:
                self.exit(task)
                continue
            self.schedule(task)     # Put task back into back of array


if __name__ == '__main__':
    # A very simple generator
    def foo():
        mytid = yield GetTid()
        for i in range(0,10):
            print(f"I'm foo, with tid {mytid}")
            sleep(1)
            yield

    def bar():
        mytid = yield GetTid()
        for i in range(0,3):
            print(f"I'm bar, with tid {mytid}")
            sleep(1)
            yield

    sched = Scheduler()
    sched.new(foo())
    sched.new(bar())
    sched.mainloop()
