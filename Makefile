generate: data.json
	./generator.py

clean:
	rm -rf 2012

git:
	git add */*/*

.PHONY: clean git
