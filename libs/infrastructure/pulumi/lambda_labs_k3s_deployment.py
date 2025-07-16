"""Qdrant vector database"""
    
    # Lambda Labs cluster configuration
    cluster_config = K3sClusterConfig(
        name="sophia-ai-fortress",
        nodes=[
            "192.222.58.232",  # Primary Lambda Labs node
            "104.171.202.103", # Secondary node
            "104.171.202.117"  # MCP node
        ],
        gpu_nodes=[
            "192.222.58.232",  # GPU node 1
            "104.171.202.103"  # GPU node 2
        ],
        master_node="192.222.58.232",
        kubeconfig_path="~/.kube/config",
        namespace="sophia-ai"
    )
    
    deployment = SophiaAIDeployment(cluster_config)
    await deployment.deploy_fortress()
    
    print("\n🎉 Sophia AI Lambda Labs K3s Fortress deployed!")
    print("🔗 Access your fortress at: https://sophia-ai.lambda-labs.com")
    print("📊 Monitoring: https://grafana.sophia-ai.lambda-labs.com")
    print("🎯 Ready for 10M events/day with <150ms response times!")

if __name__ == "__main__":
    asyncio.run(main()) 