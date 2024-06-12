from textx import metamodel_from_file
import pathlib

baseFile = pathlib.Path(__file__).parent.resolve()

def parse(specification_file, classes):
	metamodel = metamodel_from_file(f'{baseFile}/grammar.tx', classes = classes)
	model = metamodel.model_from_file(specification_file)
	# Also possible to just take a string:
	# model = metamodel.model_from_str(str)

	# TODO remove below?
	# for o in model.actors:
	# 	print(f"{type(o).__name__}: {o.__dict__}\n")
	# for o in model.constraints:
	# 	print(f"{type(o).__name__}: {o.__dict__}\n")

	return model
