# ─────────────────────────────────────────────
# MSK Broker Configuration
# ─────────────────────────────────────────────
resource "aws_msk_configuration" "main" {
  name           = "${var.project_name}-kafka-config-${var.environment}"
  kafka_versions = [var.kafka_version]
  description    = "Configuracao customizada para o cluster MSK do ${var.project_name}"

  server_properties = <<-PROPERTIES
    auto.create.topics.enable=false
    default.replication.factor=2
    min.insync.replicas=1
    num.io.threads=8
    num.network.threads=5
    num.partitions=3
    num.replica.fetchers=2
    replica.lag.time.max.ms=30000
    socket.receive.buffer.bytes=102400
    socket.request.max.bytes=104857600
    socket.send.buffer.bytes=102400
    unclean.leader.election.enable=true
    log.retention.hours=168
    log.segment.bytes=1073741824
    log.retention.check.interval.ms=300000
  PROPERTIES
}

# ─────────────────────────────────────────────
# Security Group para os brokers MSK
# ─────────────────────────────────────────────
resource "aws_security_group" "msk" {
  name        = "${var.project_name}-msk-${var.environment}"
  description = "Security group para os brokers MSK do ${var.project_name}"
  vpc_id      = var.vpc_id

  # Kafka PLAINTEXT (acesso interno na VPC)
  ingress {
    description = "Kafka PLAINTEXT - acesso interno VPC"
    from_port   = 9092
    to_port     = 9092
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  # Kafka TLS (clientes com autenticacao)
  ingress {
    description = "Kafka TLS"
    from_port   = 9094
    to_port     = 9094
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  # ZooKeeper (acesso interno entre brokers)
  ingress {
    description = "ZooKeeper - acesso interno"
    from_port   = 2181
    to_port     = 2181
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-msk-${var.environment}"
  })
}

# ─────────────────────────────────────────────
# MSK Cluster
# ─────────────────────────────────────────────
resource "aws_msk_cluster" "main" {
  cluster_name           = "${var.project_name}-kafka-${var.environment}"
  kafka_version          = var.kafka_version
  number_of_broker_nodes = var.number_of_broker_nodes

  broker_node_group_info {
    instance_type   = var.broker_instance_type
    client_subnets  = var.subnet_ids
    security_groups = [aws_security_group.msk.id]

    storage_info {
      ebs_storage_info {
        volume_size = var.broker_volume_size
      }
    }
  }

  configuration_info {
    arn      = aws_msk_configuration.main.arn
    revision = aws_msk_configuration.main.latest_revision
  }

  encryption_info {
    encryption_in_transit {
      client_broker = "TLS_PLAINTEXT"
      in_cluster    = true
    }
  }

  open_monitoring {
    prometheus {
      jmx_exporter {
        enabled_in_broker = true
      }
      node_exporter {
        enabled_in_broker = true
      }
    }
  }

  tags = var.common_tags
}
