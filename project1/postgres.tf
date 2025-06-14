resource "docker_image" "postgres" {
  name = "postgres:latest"
}

resource "docker_container" "db" {
  image = docker_image.postgres.image_id
  name  = "postgres_container"
  ports {
    internal = 5432
    external = 5432
  }
  env = [
    "POSTGRES_USER=admin",
    "POSTGRES_PASSWORD=admin",
    "POSTGRES_DB=data_db"
  ]
}
