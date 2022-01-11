RM=rm -f

generate: data.json
	./generator.py

clean:
	$(RM) -r generation/*

git:
	git add generation/*
	git add generation/*/*/*

.PHONY: clean git
