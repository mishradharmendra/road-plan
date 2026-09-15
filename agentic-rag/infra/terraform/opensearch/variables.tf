variable "name" {
  description = "Domain name. Becomes the DNS label, so keep it short and lowercase."
  type        = string
  default     = "rag-chunks"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,27}$", var.name))
    error_message = "Domain names must be lowercase, start with a letter, 3-28 chars."
  }
}

variable "environment" {
  type = string
}

variable "engine_version" {
  description = "2.17 is the floor: binary quantization (mode/compression_level) and query-time rescore land there."
  type        = string
  default     = "OpenSearch_2.17"
}

# ---------------------------------------------------------------------------
# Sizing
#
# Defaults are calculated for ~200M chunks at 1024 dimensions with 32x binary
# quantization (ADR-001):
#
#   vectors  200M x 128 B                 =  25.6 GB
#   HNSW graph, M=32, ~256 B/node         =  51.2 GB
#   ------------------------------------------------
#   resident kNN footprint                 ~ 77 GB
#
# k-NN graphs live in off-heap native memory, NOT the JVM heap. On r6gd.4xlarge
# (128 GB RAM) the heap is capped at ~32 GB, leaving ~96 GB off-heap, of which
# knn.memory.circuit_breaker.limit (50%) makes ~48 GB usable per node.
#
#   6 nodes x 48 GB = 288 GB available vs. 77 GB needed -> ~3.7x headroom.
#
# Headroom is deliberate: segment merges transiently double graph memory, and
# crossing the circuit breaker evicts graphs and collapses p99 latency.
# ---------------------------------------------------------------------------

variable "data_instance_type" {
  description = "Instance-store (d-suffix) types keep full-precision rescore vectors on local NVMe."
  type        = string
  default     = "r6gd.4xlarge.search"
}

variable "data_instance_count" {
  type    = number
  default = 6

  validation {
    condition     = var.data_instance_count % 3 == 0
    error_message = "Use a multiple of 3 so shards distribute evenly across 3 AZs."
  }
}

variable "master_instance_type" {
  type    = string
  default = "m6g.large.search"
}

variable "ebs_enabled" {
  description = "Set true only for instance types without local NVMe."
  type        = bool
  default     = false
}

variable "ebs_volume_gb" {
  type    = number
  default = 1024
}

variable "availability_zone_count" {
  type    = number
  default = 3
}

variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  description = "Private subnets, one per AZ. Must match availability_zone_count."
  type        = list(string)
}

variable "ingress_security_group_ids" {
  description = "Security groups permitted to reach the domain on 443 (the ECS service SGs)."
  type        = list(string)
}

variable "allowed_principal_arns" {
  description = "IAM principals in the domain access policy. Keep this tight; fine-grained access control authorises on top of it, it does not replace it."
  type        = list(string)
}

variable "master_user_arn" {
  description = "IAM role that owns the OpenSearch security config. Internal user database stays disabled - no passwords."
  type        = string
}

variable "kms_key_arn" {
  description = "Customer managed key for encryption at rest. Null provisions an AWS managed key."
  type        = string
  default     = null
}

variable "log_retention_days" {
  type    = number
  default = 30
}

variable "slow_query_threshold_ms" {
  description = "Search slow log warn threshold. Set below the p95 budget so regressions surface before users report them."
  type        = number
  default     = 200
}

variable "alarm_sns_topic_arns" {
  type    = list(string)
  default = []
}

variable "tags" {
  type    = map(string)
  default = {}
}
