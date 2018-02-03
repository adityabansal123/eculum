from premium import Premium
from cleo import Application

application = Application()
application.add(Premium())

if __name__ == '__main__':
    application.run()
