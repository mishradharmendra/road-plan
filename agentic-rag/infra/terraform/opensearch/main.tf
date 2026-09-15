data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  domain_arn = "arn:aws:es:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:domain/${var.name}"

  tags = merge(var.tags, {
    Name        = var.name
    Environment = var.environment
    Component   = "agentic-rag-retrieval"
    ManagedBy   = "terraform"
  })
}

# ---------------------------------------------------------------------------
# Network
# ---------------------------------------------------------------------------

resource "aws_security_group" "domain" {
  name        = "${var.name}-opensearch"
  description = "OpenSearch domain ${var.name}"
  vpc_id      = var.vpc_id
  tags        = local.tags

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_vpc_security_group_ingress_rule" "https" {
  for_each = toset(var.ingress_security_group_ids)

  security_group_id            = aws_security_group.domain.id
  referenced_security_group_id = each.value
  from_port                    = 443
  to_port                      = 443
  ip_protocol                  = "tcp"
  description                  = "HTTPS from ${each.value}"
}

# The domain's ENIs need to reach AWS APIs (KMS, CloudWatch) for encryption and logging.
resource "aws_vpc_security_group_egress_rule" "all" {
  security_group_id = aws_security_group.domain.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
  description       = "Domain egress"
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

locals {
  log_types = {
    application = "ES_APPLICATION_LOGS"
    search_slow = "SEARCH_SLOW_LOGS"
    index_slow  = "INDEX_SLOW_LOGS"
  }
}

resource "aws_cloudwatch_log_group" "domain" {
  for_each = local.log_types

  name              = "/aws/opensearch/${var.name}/${each.key}"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.kms_key_arn
  tags              = local.tags
}

data "aws_iam_policy_document" "logs" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["es.amazonaws.com"]
    }

    actions = [
      "logs:PutLogEvents",
      "logs:CreateLogStream",
    ]

    resources = [for lg in aws_cloudwatch_log_group.domain : "${lg.arn}:*"]

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }

    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = [local.domain_arn]
    }
  }
}

resource "aws_cloudwatch_log_resource_policy" "domain" {
  policy_name     = "${var.name}-opensearch-logs"
  policy_document = data.aws_iam_policy_document.logs.json
}

# ---------------------------------------------------------------------------
# Access policy
#
# Restricted to named principals even though fine-grained access control is on.
# FGAC authorises within the domain; this is the perimeter, and "AWS": "*" here
# is the single most common way managed OpenSearch domains get exposed.
# ---------------------------------------------------------------------------

data "aws_iam_policy_document" "access" {
  statement {
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = var.allowed_principal_arns
    }

    actions   = ["es:ESHttpGet", "es:ESHttpPost", "es:ESHttpPut", "es:ESHttpHead", "es:ESHttpDelete"]
    resources = ["${local.domain_arn}/*"]
  }
}

# ---------------------------------------------------------------------------
# Domain
# ---------------------------------------------------------------------------

resource "aws_opensearch_domain" "this" {
  domain_name    = var.name
  engine_version = var.engine_version
  tags           = local.tags

  cluster_config {
    instance_type  = var.data_instance_type
    instance_count = var.data_instance_count

    # Dedicated masters keep cluster-state work off the nodes serving a 2 s p95.
    dedicated_master_enabled = true
    dedicated_master_type    = var.master_instance_type
    dedicated_master_count   = 3

    zone_awareness_enabled = true
    zone_awareness_config {
      availability_zone_count = var.availability_zone_count
    }
  }

  ebs_options {
    ebs_enabled = var.ebs_enabled
    volume_type = var.ebs_enabled ? "gp3" : null
    volume_size = var.ebs_enabled ? var.ebs_volume_gb : null
    throughput  = var.ebs_enabled ? 500 : null
    iops        = var.ebs_enabled ? 6000 : null
  }

  vpc_options {
    subnet_ids         = var.subnet_ids
    security_group_ids = [aws_security_group.domain.id]
  }

  encrypt_at_rest {
    enabled    = true
    kms_key_id = var.kms_key_arn
  }

  node_to_node_encryption {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-PFS-2023-10"
  }

  advanced_security_options {
    enabled                        = true
    anonymous_auth_enabled         = false
    internal_user_database_enabled = false

    master_user_options {
      master_user_arn = var.master_user_arn
    }
  }

  advanced_options = {
    # Hybrid queries over many filter terms blow through the default clause limit.
    "indices.query.bool.max_clause_count"    = "4096"
    "rest.action.multi.allow_explicit_index" = "true"
  }

  auto_tune_options {
    desired_state       = "ENABLED"
    rollback_on_disable = "NO_ROLLBACK"
  }

  off_peak_window_options {
    enabled = true
    off_peak_window {
      window_start_time {
        hours   = 8 # UTC; 01:00 America/Los_Angeles
        minutes = 0
      }
    }
  }

  software_update_options {
    auto_software_update_enabled = true
  }

  dynamic "log_publishing_options" {
    for_each = local.log_types

    content {
      log_type                 = log_publishing_options.value
      cloudwatch_log_group_arn = aws_cloudwatch_log_group.domain[log_publishing_options.key].arn
      enabled                  = true
    }
  }

  access_policies = data.aws_iam_policy_document.access.json

  depends_on = [aws_cloudwatch_log_resource_policy.domain]

  lifecycle {
    # Blue/green index swaps must never be expressed as a domain replacement.
    prevent_destroy = true
  }
}

# ---------------------------------------------------------------------------
# Alarms
#
# KNNGraphMemoryUsage is the one people forget. When graphs are evicted the
# cluster stays green, no errors are logged, and p99 latency quietly triples.
# ---------------------------------------------------------------------------

locals {
  alarms = {
    cluster_red = {
      metric    = "ClusterStatus.red"
      statistic = "Maximum"
      threshold = 1
      period    = 60
      operator  = "GreaterThanOrEqualToThreshold"
    }
    cluster_yellow = {
      metric    = "ClusterStatus.yellow"
      statistic = "Maximum"
      threshold = 1
      period    = 300
      operator  = "GreaterThanOrEqualToThreshold"
    }
    jvm_pressure = {
      metric    = "JVMMemoryPressure"
      statistic = "Maximum"
      threshold = 80
      period    = 300
      operator  = "GreaterThanThreshold"
    }
    knn_graph_memory = {
      metric    = "KNNGraphMemoryUsage"
      statistic = "Maximum"
      threshold = 85
      period    = 300
      operator  = "GreaterThanThreshold"
    }
    search_latency = {
      metric    = "SearchLatency"
      statistic = "p99"
      threshold = 300
      period    = 300
      operator  = "GreaterThanThreshold"
    }
    free_storage = {
      metric    = "FreeStorageSpace"
      statistic = "Minimum"
      threshold = 51200 # MB
      period    = 300
      operator  = "LessThanThreshold"
    }
    threadpool_search_rejected = {
      metric    = "ThreadpoolSearchRejected"
      statistic = "Maximum"
      threshold = 1
      period    = 60
      operator  = "GreaterThanThreshold"
    }
  }
}

resource "aws_cloudwatch_metric_alarm" "domain" {
  for_each = local.alarms

  alarm_name          = "${var.name}-${each.key}"
  namespace           = "AWS/ES"
  metric_name         = each.value.metric
  statistic           = contains(["p99", "p90"], each.value.statistic) ? null : each.value.statistic
  extended_statistic  = contains(["p99", "p90"], each.value.statistic) ? each.value.statistic : null
  comparison_operator = each.value.operator
  threshold           = each.value.threshold
  period              = each.value.period
  evaluation_periods  = 2
  treat_missing_data  = "notBreaching"

  dimensions = {
    DomainName = aws_opensearch_domain.this.domain_name
    ClientId   = data.aws_caller_identity.current.account_id
  }

  alarm_actions = var.alarm_sns_topic_arns
  ok_actions    = var.alarm_sns_topic_arns
  tags          = local.tags
}
