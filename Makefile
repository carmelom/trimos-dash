.ONESHELL:
.PHONY: prepare run clean services

prepare:
	poetry install

run:
	poetry run mode_solver_dashboard

clean:
	rm -r .venv poetry.lock


services: services/mode_solver_dashboard.service
	echo "> Creating links to services in /etc/systemd/system/"
	sudo ln -s `pwd`/services/*.service /etc/systemd/system/
	sudo systemctl daemon-reload

	echo "> Enabling services and starting server"
	sudo systemctl enable mode_solver_dashboard.service
	sudo systemctl start mode_solver_dashboard.service


services/mode_solver_dashboard.service:
	echo "> Creating services..."
	mkdir -p services
	cat <<EOF > $@
	[Unit]
	Description=A dashboard for a mode solver
	After=network.target
	
	[Service]
	User=$$USER
	WorkingDirectory=$$(pwd)
	ExecStart=$$(pwd)/.venv/bin/python -m mode_solver_dashboard.main
	Restart=always
	RestartSec=10
	
	[Install]
	WantedBy=multi-user.target
	EOF
