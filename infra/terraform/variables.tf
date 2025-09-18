variable "resource_group_name" {
  description = "The name of the resource group."
  default     = "ai-powered-reliability-rg"
}

variable "location" {
  description = "The location of the resources."
  default     = "East US"
}

variable "cluster_name" {
  description = "The name of the AKS cluster."
  default     = "ai-powered-reliability-aks"
}

variable "dns_prefix" {
  description = "The DNS prefix for the AKS cluster."
  default     = "ai-powered-reliability"
}

variable "node_count" {
  description = "The number of nodes in the AKS cluster."
  default     = 2
}

variable "vm_size" {
  description = "The size of the virtual machines in the AKS cluster."
  default     = "Standard_DS2_v2"
}
