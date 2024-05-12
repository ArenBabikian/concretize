from textx import metamodel_from_file
import pathlib

baseFile = pathlib.Path(__file__).parent.resolve()

metamodel = metamodel_from_file(f'{baseFile}/grammar.tx')

model = metamodel.model_from_file(f'{baseFile}/example.concretize')
# Also possible to just take a string:
# model = metamodel.model_from_str(str)

for o in model.objects:
	print(f"{type(o).__name__}: {o.__dict__}\n")