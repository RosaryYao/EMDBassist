class Shape:
	dimensions = 2 # class variables applies to all shape instances

	def __init__(self, name):
		self.name = name # self refers to instances

	def __str__(self):
		return f"I am a {self.name} of dimension {self.dimensions} but in general we have {Shape.dimensions} dimensions"

	@classmethod
	def show_dimensions(cls):
		print(f"Shapes generally have {cls.dimensions}")


s = Shape("triangle")

print(s)

m = Shape("circle")
m.dimensions = 3

m.show_dimensions()

print(m)
print(s)
