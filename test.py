class Duck:
    def quack(self):
        print "Quaaaaack..."
    def feathers(self):
        print "The Duck has feathers."

class Person:
    def quack(self):
        print "Person is not a duck"
    def feathers(self):
        print "The person takes a feather from the ground and shows it."

class Car:
    def run(self):
        print "Car is running"

def in_the_forest(duck):
    duck.quack()
    duck.feathers()

def game():
    donald = Duck()
    john = Person()
    in_the_forest(donald)
    in_the_forest(john)
    car = Car()
    try: # will throw exception
        in_the_forest(car)
    except (AttributeError, TypeError):
        print "No the method for duck typing"

game()