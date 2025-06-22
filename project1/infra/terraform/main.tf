provider "aws" {
  region  = "sa-east-1"
  profile = "default"
}

resource "tls_private_key" "ec2_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "local_file" "private_key_pem" {
  content              = tls_private_key.ec2_key.private_key_pem
  filename             = pathexpand("~/.ssh/ec2-key.pem")
  file_permission      = "0600"
  directory_permission = "0700"
}

resource "aws_key_pair" "default" {
  key_name   = "ec2-key"
  public_key = tls_private_key.ec2_key.public_key_openssh
}

resource "aws_security_group" "allow_ssh" {
  name        = "allow_ssh"
  description = "Permite acesso SSH"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "free_tier_ec2" {
  ami                    = "ami-080a223be3de0c3b8" # Amazon Linux 2 para sa-east-1
  instance_type          = "t2.micro"
  key_name               = aws_key_pair.default.key_name
  security_groups        = [aws_security_group.allow_ssh.name]
  associate_public_ip_address = true

  provisioner "remote-exec" {
    inline = [
      "sudo yum update -y",
      "sudo amazon-linux-extras enable postgresql14",
      "sudo yum install -y postgresql-server postgresql",
      "sudo /usr/bin/postgresql-setup initdb",
      "sudo systemctl enable postgresql",
      "sudo systemctl start postgresql",
      "CREATE ROLE ruivo WITH LOGIN PASSWORD '123456' SUPERUSER CREATEDB CREATEROLE;",
      "sudo -u postgres psql -c \"CREATE DATABASE ibge -- Name of the database to be created.
     WITH OWNER = ruivo -- Server user who will be the owner of the database.
          TEMPLATE = template1 -- Database that will be used as a template for creating the new database.
          ENCODING = ‘UTF8’ -- Type of encoding for the data that will be stored in the database.
          TABLESPACE = pg_default -- Tablespace where the database will be physically created.
          CONNECTION LIMIT = 100; -- Maximum number of simultaneous connections allowed in the database.\"",
      "sudo -u postgres psql -d ibge -c \"CREATE SCHEMA silver;\"",
      "sudo -u postgres psql -d ibge -c \"CREATE SCHEMA gold;\""
    ]

    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = tls_private_key.ec2_key.private_key_pem
      host        = aws_instance.free_tier_ec2.public_ip
    }
  }

  tags = {
    Name = "FreeTierPostgres"
  }
}

output "ec2_public_ip" {
  value = aws_instance.free_tier_ec2.public_ip
}