IMAGE ?= flask-jenkins-app
TAG   ?= latest

.PHONY: install lint test run docker-build docker-run

install:
	pip install -r requirements-dev.txt

lint:
	flake8 app tests wsgi.py

test:
	pytest --cov=app --cov-report=term-missing

run:
	APP_ENV=development python wsgi.py

docker-build:
	docker build -t $(IMAGE):$(TAG) .

docker-run:
	docker run --rm -p 5000:5000 $(IMAGE):$(TAG)
