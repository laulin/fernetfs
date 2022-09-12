build :
	python3 setup.py sdist bdist_wheel

upload:
	twine upload dist/*

clean:
	rm -rf build/ dist/

tests:
	python3 -m unittest discover -s test #-p "test_file.py"