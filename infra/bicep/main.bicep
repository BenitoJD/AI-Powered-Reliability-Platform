targetScope = 'subscription'

param location string = 'East US'
param resourceGroupName string = 'ai-powered-reliability-rg'
param clusterName string = 'ai-powered-reliability-aks'
param dnsPrefix string = 'ai-powered-reliability'
param nodeCount int = 2
param vmSize string = 'Standard_DS2_v2'

resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: resourceGroupName
  location: location
}

module law 'log-analytics.bicep' = {
  name: 'log-analytics-deployment'
  scope: rg
  params: {
    workspaceName: '${clusterName}-law'
    location: location
  }
}

module kv 'key-vault.bicep' = {
  name: 'key-vault-deployment'
  scope: rg
  params: {
    keyVaultName: '${clusterName}-kv'
    location: location
  }
}

resource aks 'Microsoft.ContainerService/managedClusters@2022-03-01' = {
  name: clusterName
  location: location
  resourceGroup: rg.name
  properties: {
    dnsPrefix: dnsPrefix
    agentPoolProfiles: [
      {
        name: 'agentpool'
        count: nodeCount
        vmSize: vmSize
        mode: 'System'
      }
    ]
    addonProfiles: {
      omsagent: {
        enabled: true
        config: {
          logAnalyticsWorkspaceResourceID: law.outputs.workspaceId
        }
      }
    }
  }
  identity: {
    type: 'SystemAssigned'
  }
}

