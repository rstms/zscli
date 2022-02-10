# lint / source format

lint_src = $(project) tests docs

# blacken python source (code formatter)
fmt:  
	isort $(lint_src)
	black $(lint_src)

# check style, lint with flake8
lint: fmt
	flake8 --config tox.ini $(lint_src)

# vim:ft=make
