# Building a standalone docker image for powerwall3mqtt

This folder contains a Dockerfile that builds a stand alone docker image that can be used to run powerwall3mqtt as a 
stand alone docker image.  If you are running Home Assistant Core, you are probably already familiar with running
multiple docker images for the various addons that you want to run.  This image build process allows you to do that.

# Usage

From the main repo path, execute the following command:

```
sudo docker build -t powerwall3mqtt-hacore -f hacore/Dockerfile .
```

This will instruct docker to build an image called 'powerwall3mqtt-hacore' and place the image in your local docker image
repository.  After the image is built, you can then use docker-compose to bring up the image and run the application.

You'll want to configure the compose file and set the proper environment variables for your GW ip, password, mqtt
settings, etc prior to running the docker-compose.  You'll find a sample to customize in the hacore directory.

Once you've customized the docker-compose.yaml, you can bring up the docker image with this command executed from the hacore directory:

```
cd hacore
docker-compose up -d
```
