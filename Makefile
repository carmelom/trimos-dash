.ONESHELL:
.PHONY: prepare run clean services

prepare:
	poetry install

run:
	poetry run calculators

clean:
	rm -r .venv poetry.lock


services: services/calculators.service
	echo "> Creating links to services in /etc/systemd/system/"
	sudo ln -s `pwd`/services/*.service /etc/systemd/system/
	sudo systemctl daemon-reload

	echo "> Enabling services and starting server"
	sudo systemctl enable calculators.service
	sudo systemctl start calculators.service


services/calculators.service:
	echo "> Creating services..."
	mkdir -p services
	cat <<EOF > $@
	[Unit]
	Description=A dashboard of physics calculators
	After=network.target
	
	[Service]
	User=$$USER
	WorkingDirectory=$$(pwd)
	ExecStart=$$(pwd)/.venv/bin/python -m calculators.main
	Restart=always
	RestartSec=10
	
	[Install]
	WantedBy=multi-user.target
	EOF
