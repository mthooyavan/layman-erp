# Layman ERP Platform
An open source ERP tool that anyone can use.

Welcome to the technical documentation for the Layman ERP Platform!

## Local Setup

* Install Docker
* Install Git & setup [SSH access](https://help.github.com/en/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
* ssh clone this repository (`git clone git@github.com:mthooyavan/layman-erp.git`)
* cd into the repository
* run `make build` to build the images

### Postgres

Migrations (locally, production is run on deploy)
```shell
> make setup-db
```

### One-Time

Create a Super User
```shell
> docker-compose run web python3 manage.py createsuperuser --username testuser --email testuser@example.com
```

###  Running the Server

Run Server
```shell
> make start
```

Visit
http://localhost:8000/

#### Console

```shell
> make console
