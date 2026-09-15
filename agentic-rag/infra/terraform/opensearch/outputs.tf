output "endpoint" {
  description = "Set as OPENSEARCH_ENDPOINT / provider.endpoint in the ragkit config."
  value       = "https://${aws_opensearch_domain.this.endpoint}"
}

output "domain_arn" {
  value = aws_opensearch_domain.this.arn
}

output "domain_name" {
  value = aws_opensearch_domain.this.domain_name
}

output "security_group_id" {
  value = aws_security_group.domain.id
}

output "dashboards_endpoint" {
  value = "https://${aws_opensearch_domain.this.dashboard_endpoint}"
}

output "knn_capacity_note" {
  description = "Off-heap memory available for k-NN graphs, versus the ~77 GB needed at 200M binary-quantized vectors."
  value       = "${var.data_instance_count} data nodes; verify KNNGraphMemoryUsage stays under 85% after each backfill."
}
