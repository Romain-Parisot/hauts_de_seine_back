# Hello Hauts de seine

cd in the projetc
activate the venv and install

## Run with podamn (also work the same with docker) 

build container
```bash
  podman build -t pcc:latest . 
  podman run --name pcc-prod -p 80:80 -e POSTGRES_USER=xxxxxx -e POSTGRES_PASSWORD=xxxxxx -e POSTGRES_DB=xxxxxxx -e POSTGRES_HOST=xxxxxx -e POSTGRES_PORT=xxxxx --replace pcc:latest

```
