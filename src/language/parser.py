from textx import metamodel_from_file

metamodel = metamodel_from_file('grammar.tx')

model = metamodel.model_from_file('example.concretize')
# Also possible to just take a string:
# model = metamodel.model_from_str(str)

for o in model.objects:
	print(type(o).__name__, o.name)
