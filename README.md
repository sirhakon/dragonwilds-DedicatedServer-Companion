# Dragonwilds Dedicated Server Companion

A lightweight companion API for RuneScape: Dragonwilds Dedicated Servers.

Designed for Homepage dashboards, homelabs and self-hosted game servers.

## Screenshot

![Homepage](images/Dragonwilds3.png)
Open the webdashboard:

```text
http://YOUR_DOCKER_HOST_IP:9876
```
![Homepage](images/Dragonwilds.png)
![Homepage](images/Dragonwilds2.png)

## Features

- Live player count
- Live player names
- Server uptime
- Last save detection using save-file modification time
- World name detection
- CPU and RAM usage
- Homepage dashboard integration
- REST API endpoint


## API Output

```json
{
  "status": "online",
  "server": "Dragonwilds",
  "players_online": 1,
  "max_players": 6,
  "players_text": "xdrushxd",
  "uptime": "16h 15m",
  "last_save": "4m ago",
  "memory": "1.7GiB",
  "cpu": "6.5%"
}
```
# Docker Installation (Recommended)

```Docker Compose
services:
  dragonwilds-companion:
    container_name: dragonwilds-companion
    restart: unless-stopped
    image: bulkmass/runescape-companion:latest
   environment:
      TZ: "Your Timezone"
      CONTAINER: "Name of your dragonwilds container"
      SAVE_PATH: /savegames
      PORT: "9876"
      MAX_PLAYERS: 6
      MYSQL_HOST: dragonwilds-mysql
      MYSQL_PORT: "3306"
      MYSQL_DATABASE: dragonwilds
      MYSQL_USER: dragonwilds
      MYSQL_PASSWORD: "Password from dragonwilds-mysql"
    depends_on:
      - runescape-mysql
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /docker/runescape/RSDragonwilds/Saved/SaveGames:/savegames:ro
    ports:
      - "9876:9876"
    restart: unless-stopped

  dragonwilds-mysql:
    container_name: dragonwilds-mysql
    image: mariadb:11
    environment:
      MYSQL_ROOT_PASSWORD: changeme
      MYSQL_DATABASE: dragonwilds
      MYSQL_USER: dragonwilds
      MYSQL_PASSWORD: "Set a password"
    volumes:
      - /docker/runescape-mysql:/var/lib/mysql
    restart: unless-stopped
```

Start the companion:

```bash
docker compose up -d
```

Verify that it is running:

```bash
docker ps
```

Open the API:

```text
http://YOUR_DOCKER_HOST_IP:9876/status
```

---

## Homepage Integration

Example widget:

```yaml
- Dragonwilds:
    icon: runescape
    description: RuneScape Dragonwilds
    server: docker
    container: runescape-dragonwilds
    showstats: true
    widget:
      type: customapi
      url: http://YOUR_DOCKER_HOST_IP:9876/status
      mappings:
        - field: players_online
          label: Players
        - field: players_text
          label: Names
        - field: uptime
          label: Uptime
        - field: last_save
          label: Save
```

## Requirements

- Docker
- RuneScape: Dragonwilds dedicated server running in Docker

## Roadmap

- [x] Player monitoring
- [x] Homepage widget
- [x] Save detection
- [x] Docker stats
- [ ] Discord webhook
- [ ] Web dashboard
- [X] Docker image
- [ ] Backup monitoring
- [ ] Steam update checker

## License

MIT
