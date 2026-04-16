output "bootstrap_brokers_tls" {
  description = "Endpoints TLS dos brokers MSK (para clientes em producao)"
  value       = aws_msk_cluster.main.bootstrap_brokers_tls
}

output "bootstrap_brokers" {
  description = "Endpoints PLAINTEXT dos brokers MSK (para clientes na VPC sem TLS)"
  value       = aws_msk_cluster.main.bootstrap_brokers
}

output "cluster_arn" {
  description = "ARN do cluster MSK"
  value       = aws_msk_cluster.main.arn
}

output "cluster_name" {
  description = "Nome do cluster MSK"
  value       = aws_msk_cluster.main.cluster_name
}

output "zookeeper_connect_string" {
  description = "String de conexao ZooKeeper do cluster MSK"
  value       = aws_msk_cluster.main.zookeeper_connect_string
}

output "security_group_id" {
  description = "ID do security group do cluster MSK"
  value       = aws_security_group.msk.id
}
