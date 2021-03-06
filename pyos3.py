from queue import Queue
from time import sleep

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
            except StopIteration:
                self.exit(task)
                continue
            self.schedule(task)     # Put task back into back of array


if __name__ == '__main__':
    # A very simple generator
    def foo():
        for i in range(0,10):
            print("I'm foo")
            sleep(1)
            yield

    def bar():
        for i in range(0,3):
            print("I'm bar")
            sleep(1)
            yield

    sched = Scheduler()
    sched.new(foo())
    sched.new(bar())
    sched.mainloop()
