### Local Deployment

If you want to deploy it locally or run it locally, all you need to do is to run the following command:

```bash
cd ./API
docker-compose up
```

And then open the browser and go to `http://localhost:8000` to login with username `admin` and password `password`.

If you are within your local network, and want to access the API from another device, you can use the private IP address
of the machine where the API is running.
So go to the `http://<private-ip>:8000` to access the API.

### Deploy on Cloud

You will need to have a cloud server, it can be AWS EC2, Azure Compute Engine or any VPS server you can access.
It will need to have a public IP address.
The demonstration about how to deploy it to a cloud server is in our CI/CD process.

You will need to access the server and install `docker` first.
Test out the command `docker` and `docker compose` to verify the installation.

And then you can fork our repo, and replace the IP in the `.github/workflows/deploy.yml` file with the public IP of your
server, also remember to set the `Actions -> Secrets`, add a secret with the name `SERVER_PASSWORD` and the value as
your server password.

In this way, you can continuously deploy the API to your server when code changes, and merge to the `develop` branch.

If you want to manually to do so, it is also simple, just follow the steps in the `deploy.yml` file.
Pull the code to your server and mainly run the command in last step:

```bash
cd /root 
rm -rf omni
mkdir omni
tar xopf omni.tar -C omni
cd /root/omni/API
docker compose -f docker-compose.yml down
docker compose -f docker-compose.yml up --build -d
```

Configuration of Nginx will be like this:

```nginx
server {
    server_name openomni.ai4wa.com;
    client_max_body_size 100M;
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
