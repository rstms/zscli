# test - testing with pytest and tox

options ?= -x --log-cli-level 30
testfiles ?= $(wildcard tests/test_*.py)
options := $(if $(test),$(options) -k $(test),$(options))

# run pytest;  example: make options=-svvvx test=cli test 
test: test_env
	envdir secrets pytest $(options) $(testfiles)

# run pytest, dropping into pdb on exceptions or breakpoints
debug: test_env
	${MAKE} options="$(options) --log-cli-level 0 -xvvvs --pdb" test

# check code coverage quickly with the default Python
coverage: test_env
	envdir secrets coverage run --source $(project) -m pytest
	coverage report -m
	coverage html
	$(browser) htmlcov/index.html

# show available test cases 
testls:
	@echo $$($(foreach test,$(testfiles),grep -o '^def test_[[:graph:]]*' $(test);)) |\
	  tr ' ' '\n' | grep -v def | awk -F\( 'BEGIN{xi=0} {printf("%s",$$1);\
	  if(++xi==3){xi=0; printf("\n");} else {printf("\t");}}' |\
	  awk 'BEGIN{print ".TS\nbox,nowarn;\nl | l | l ." } {print} END{print ".TE";}' |\
	  tbl | groff  -T utf8 | awk 'NF';

# test with tox if sources have changed
.PHONY: tox
tox: .tox 
.tox: $(python_src) test_env tox.ini
	envdir secrets tox
	@touch $@

test_env:
	echo 1 >secrets/TESTING

