module "example" {
  source = "localhost.localdomain:8080/examplecorp/examplemodule/aws"
  version = "1.0.0"
}

output "main" {
  value = "${module.example.example}"
}