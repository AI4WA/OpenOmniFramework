# Your Cloud

This will be similar to the **Trail on Cloud** section, only differences is that the API end is on your cloud server.

Under this mode, your storage solution will be *s3*, you will need to

- create a s3 bucket, and replace it to the *S3_BUCKET* setting in AI/API/Client
- create an access key and secret key, set it properly for both AI, API and Client, refer to AWS documentation for more
  details

After this, the first step you will need to do is deploying it to your cloud server.

We will assume it is a Linux Machine.

## **Step 1**: Deploy the API on Cloud

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
export STORAGE_SOLUTION=s3
docker compose -f docker-compose.yml down
docker compose -f docker-compose.yml up --build -d
```

Configuration of Nginx will be like this:

```nginx
server {
    server_name openomni.ai4wa.com; # replace with your domain
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

Then run

```bash
sudo service nginx restart
```

Add a DNS A record for this sever for your domain, and you should be able to access the API
at `http://your.domain.com`.

Then you can follow the steps in the `Trail on Cloud` section to get the AI and Client running.

