generate: data.json
	./generator.py

clean:
	rm -rf generation/*

git:
	git add generation/*/*/*

.PHONY: clean git
