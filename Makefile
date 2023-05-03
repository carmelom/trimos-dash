.ONESHELL:
.PHONY: install run clean services

install:
	poetry install

run:
	poetry run trimos_dash

clean:
	rm -r .venv poetry.lock


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
