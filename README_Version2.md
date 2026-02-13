# AI-Agent---Voter-Registration

An intelligent extraction agent powered by Microsoft Foundry that reads unstructured voter registration JSON data, extracts exactly five fields, and stores them in Azure Blob Storage via an Azure Function.

##  Project Overview

This project consists of two main components:

1. **Azure Function App** - Processes and validates voter registration data
2. **AI Extraction Agent** - Uses AI to intelligently extract data from unstructured JSON and interact with users

### Key Features

 Extracts 5 fields from unstructured JSON:
- First Name
- Last Name
- Date of Birth (DOB)
- Address
- Status
- Registration ID

 Handles multiple JSON formats (objects and arrays)
 Stores validated records in Azure Blob Storage
 Interactive chat interface via Microsoft Foundry Agent
 Automatic summarization of batch processing results

---


