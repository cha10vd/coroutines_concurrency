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

if __name__ == '__main__':
    # A very simple generator
    def foo():
        print('part 1')
        yield
        print('part 2')
        yield

    t1 = Task(foo())
    t1.run()
    t1.run()
