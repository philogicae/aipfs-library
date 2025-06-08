echo "Setting ipfs config"
ipfs config --json API.HTTPHeaders.Access-Control-Allow-Origin '["*"]'
ipfs config --json API.HTTPHeaders.Access-Control-Allow-Methods '["PUT", "POST"]'
ipfs config --json Routing.AcceleratedDHTClient true
ipfs config --json Swarm.RelayClient.Enabled true
ipfs config --json Swarm.EnableHolePunching true
ipfs config --json Experimental.FilestoreEnabled true
ipfs config --json Experimental.Libp2pStreamMounting true
ipfs config --json Experimental.P2pHttpProxy true