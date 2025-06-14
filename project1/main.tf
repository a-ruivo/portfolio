provider "aws" {
  region = "sa-east-1"
}

resource "aws_instance" "example" {
  ami           = "ami-0923cbda828605357"
  instance_type = "t2.micro"
}