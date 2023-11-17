build:
	docker build -t nenavizhuleto/emergency-button:latest .

compose:
	docker-compose up

run:
	docker-compose up -d
