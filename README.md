# Multi-Agent Customer Service System

An multi-agent customer service system that uses SPADE (Smart Python Agent Development Environment) with intelligent processing and a web interface.

## Features

1. **Intelligent Processing**
   - Refund requests: Checks order validity, age, and eligibility
   - Product issues: Uses keyword matching to identify products and issues
   - General requests: Handles store hours and contact information queries

2. **Web Interface**
   - Responsive UI using Tailwind CSS
   - Easy form for submitting requests
   - Real-time responses from agents

3. **Database Backend**
   - SQLite database that stores:
     - Order information
     - Product issues and solutions
     - Store information

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the system:
   ```bash
   python web_interface.py
   ```

3. Access the web interface:
   - Open your browser and go to `http://localhost:8000`

## Usage Examples

1. **Refund Requests**
   - Format: Include order number with #R- prefix
   - Example: "I need a refund for order #R-98765"

2. **Product Issues**
   - Format: Mention product name and issue
   - Example: "My new toaster is not working"

3. **General Information**
   - Format: Ask about hours, contact info, etc.
   - Example: "What are your weekend hours?"

## System Architecture

The system consists of several components:

1. **Agents**
   - CustomerAgent: Handles incoming requests
   - RefundAgent: Processes refund requests
   - ProductIssueAgent: Handles product-related issues
   - GeneralRequestAgent: Manages general inquiries

2. **Database**
   - Orders table: Stores order information
   - Product issues table: Stores common issues and solutions
   - Store info table: Stores general information

3. **Web Interface**
   - FastAPI backend
   - Jinja2 templates
   - Tailwind CSS for styling

## Notes

- Using Prosody XMPP server at "172.19.104.51"
- Refund eligibility is checked against a 30-day window
- Product issues are matched using keyword recognition
- The web interface has a 10-second timeout for responses 
