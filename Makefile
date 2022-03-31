.PHONY: clean all

all: index.html

clean:
	rm index.html

index.html: src/ Seminars.csv render.py css/
	python render.py Seminars.csv
	pug --doctype html --pretty src/index.pug --out .
