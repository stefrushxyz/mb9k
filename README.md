# mb9k

A web service which accepts authorized RTMP video streams and processes them through a mask detection algorithm. Mask/no-mask results are stored alongside detection times and images in a persistent database. This data can then be visualized through a graphical frontend.

## Required Tools

[Docker](https://docs.docker.com/get-docker/), [Docker Compose](https://docs.docker.com/compose/install/), git, and a text editor

## Relevant Commands

### For Development

#### Start development server

    docker-compose up --build

A development server will now be listening at <http://localhost:8000> and <rtmp://localhost:1935>.

If you haven't updated any docker config files (`docker-compose.yml`, `Dockerfile`) you can omit the `--build` flag for faster startup in development.

Login at <http://localhost:8000/admin> with username `dev` and password `mb9k`.

Streams can be broadcast to <rtmp://localhost/live/ABCDE01234> where `ABCDE01234` is a valid stream key in the active database. For convenience the key `ABCDE01234` is loaded by default in development.

*Try it* with [OBS Studio](https://obsproject.com/download). In `Settings > Stream` use service `Custom...`, server `rtmp://localhost/live`, and stream key `ABCDE01234`. Then click `OK` and `Start Streaming`. Now navigate to <http://localhost:8000/admin/app/stream/> and behold: the stream `dev:localhost` is *LIVE*!

To use the more limited admin site as a Data Scientist use the following credentials: username `sci`, password `mb9kmb9k`, and stream key `01234ABCDE`. Data Scientists can view their own streams and all detections.

#### Fully remove development server

    docker-compose down -v --remove-orphans

### For Staging/Production

#### Install required tools (example for Amazon Linux)

    sudo yum update
    sudo yum install -y docker git vim
    sudo service docker start
    sudo usermod -aG docker ec2-user
    sudo chkconfig docker on
    sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    sudo reboot

#### Clone this repo

    git clone https://github.com/CSCI-3308-CU-Boulder/F20-Team-Won.git
    cd F20-Team-Won/mb9k
    git checkout dev

#### Copy .env production files

    cp .env.app.prod.example .env.app.prod
    cp .env.postgres.prod.example .env.postgres.prod

### Important: Change `SECRET_KEY`, `SQL_PASSWORD` in `.env.app.prod` and `POSTGRES_PASSWORD` in `.env.postgres.prod`

#### Start production server

    docker-compose -f docker-compose.prod.yml up -d --build

#### Run database migrations

    docker-compose -f docker-compose.prod.yml exec app python manage.py migrate

#### Collect static files

    docker-compose -f docker-compose.prod.yml exec app python manage.py collectstatic

#### Create initial user

    docker-compose -f docker-compose.prod.yml exec app python manage.py createsuperuser

A production server will now be listening at <http://localhost:80> and <rtmp://localhost:1935>.

#### Upgrade app to latest on dev branch

    cd F20-Team-Won/mb9k/app
    git checkout dev
    git pull origin dev
    docker cp . mb9k_app_1:/mb9k
    docker restart mb9k_app_1

## Key Files & Folders

`docker-compose.yml` - development docker configuration;

`docker-compose.prod.yml` - staging/production docker configuration;

`.env*` - environment variable files used by docker-compose;

`app/` - django application; currently just admin for streams, detections, users, and groups; same code is used by `worker` in docker config to run StreamWorker in separate container;

`app/app/api/` - backend api used by rtmp server in staging/production; + full stream and detection JSON apis in development;

`rtmp/` - nginx rtmp server configured to work with backend api;

`proxy/` - nginx reverse-proxy for app in staging/production; also serves static and media files;

`app/app/models.py` - django model declarations;

`app/template/admin/base_site.html` - frontend django admin customization; automatic page reloading; css overrides;

`app/app/admin.py` - django admin configuration;

`app/app/workers.py` - contains StreamWorker which is where the video processing goes down; could integrate categorizer here;

`app/app/clients.py` - contains TimeSeriesClient which acts as an interface between the app and redis database; much todo here;

`app/app/signals.py` - post-save signal methods for app models;

`app/app/views.py` - simple development homepage with todos, links, and sources;

`app/template/app/index.html` - template for homepage `/` index view;

`app/mb9k/settings.py` - django project master settings;
