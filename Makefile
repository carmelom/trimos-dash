.ONESHELL:
.PHONY: install run nohup_run nohup_kill clean services

install:
	poetry install

run:
	poetry run trimos_dash

clean:
	rm -r .venv poetry.lock

nohup_run:
	nohup poetry run trimos_dash & echo $$! > nohup.pid

nohup_kill:
	pkill -F nohup.pid
	rm nohup.pid