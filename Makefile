.ONESHELL:
.PHONY: install run nohup_run nohup_kill clean services

install:
	poetry install

run:
	poetry run trimos_dash 8475

clean:
	rm -r .venv poetry.lock

nohup_run:
	nohup poetry run trimos_dash 8475 & echo $$! > nohup.pid

nohup_kill:
	pkill -F nohup.pid
	rm nohup.pid

services: services/trimos_dash.service
	echo "> Creating links to services in /etc/systemd/system/"
	sudo ln -s `pwd`/services/*.service /etc/systemd/system/
	sudo systemctl daemon-reload

	echo "> Enabling services and starting server"
	sudo systemctl enable trimos_dash.service
	sudo systemctl start trimos_dash.service


services/trimos_dash.service:
	echo "> Creating services..."
	mkdir -p services
	cat <<EOF > $@
	[Unit]
	Description=A dashboard for a mode solver
	After=network.target
	
	[Service]
	User=$$USER
	WorkingDirectory=$$(pwd)
	ExecStart=$$(pwd)/.venv/bin/python -m trimos_dash.main
	Restart=always
	RestartSec=10
	
	[Install]
	WantedBy=multi-user.target
	EOF
