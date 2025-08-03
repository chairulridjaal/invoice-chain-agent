# Google Cloud Run deployment script
gcloud run deploy invoice-chain-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars="FLASK_ENV=production,ICP_NETWORK=testnet,PORT=8080" \
  --set-secrets="OPENAI_API_KEY=openai-api-key:latest" \
  --execution-environment gen2
