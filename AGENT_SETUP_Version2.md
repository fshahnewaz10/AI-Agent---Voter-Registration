# Voter Registration Analyst Agent

## Overview
This agent extracts unstructured voter data from JSON files and stores the information in Azure Blob Storage.

## Configuration

Before deploying, update the placeholders in `voter-registration-agent.yaml`:

| Placeholder | Description | Example |
|------------|-------------|---------|
| `{{ VECTOR_STORE_ID }}` | Your Azure AI vector store ID | `vs_pGQHhCMaPY4Vw2Mg55l5qS4K` |
| `{{ AZURE_FUNCTION_ENDPOINT }}` | Your Azure Function HTTP endpoint | `https://your-app.azurewebsites.net` |
| `{{ PROJECT_CONNECTION_ID }}` | Your AI Foundry project connection ID | `/subscriptions/.../connections/openapifunc` |

## Setup

1. Install dependencies:
```bash
pip install --pre azure-ai-projects>=2.0.0b1
pip install azure-identity