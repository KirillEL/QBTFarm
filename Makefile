.PHONY: start
start:
	docker compose up --build -d

.PHONY: stop
stop:
	docker compose down -v

.PHONY: restart
restart:
	docker compose restart

.PHONY: clean
clean:
	rm -rf vol

.PHONY: reset
reset: stop clean

.PHONY: logs
logs:
	docker compose logs -f

.PHONY: clear_bad_flags
clear_bad_flags:
	python3 clear_bad_flags.py