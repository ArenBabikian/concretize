# Setting up and trying out textX

## Install

In the root directory of the project, activate virtual environment, then
```
pip install -r requirements.txt
```
(I have already added the dependency to `requirements.txt`. If it does not work, try `pip install 'textx[cli]`)

(The `[cli]` option is needed to generate the diagram of the metamodel from the command line (outside Python).)

## Run
```
python src/language/parser.py
```

## Generate metamodel diagram

First make sure `graphviz` is installed: [https://graphviz.org/download/], because the image is generated using `dot` that it provides.

Then,
```
textx generate src/language/grammar.tx --target dot --overwrite
dot -Tpng src/language/grammar.dot -o src/language/metamodel.png
```
