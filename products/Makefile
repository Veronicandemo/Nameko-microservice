build-image:
		docker build -t nameko/nameko-project-products:$(TAG) .;

docker-tag:
		docker tag nameko/nameko-project-products:$(FROM_TAG) \
		nameko-project-products:$(TAG)

push-image:
		docker push nameko/nameko-project-products:$(TAG)