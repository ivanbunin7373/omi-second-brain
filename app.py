from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/process-conversation', methods=['POST'])
def process_omi_conversation():
    try:
        data = request.json
        print(f"Received Omi webhook: {data}")
        
        conversation_id = data.get('id') or data.get('conversation_id')
        title = data.get('title', 'Untitled Conversation')
        
        claude_response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": CLAUDE_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 8192,
                "messages": [{
                    "role": "user",
                    "content": f"""
Using the Omi MCP server, read conversation ID: {conversation_id}

Analyze and save it to the correct folder in my Google Drive Second Brain:
- Pareto Talent → /Second Brain/03-Active-Projects/Pareto-Talent/
- Content/YouTube → /Second Brain/02-Knowledge-Base/Content-Ideas/
- Personal → /Second Brain/02-Knowledge-Base/Personal/
- Business → /Second Brain/02-Knowledge-Base/Business/

Create a markdown file with summary, key points, action items, and full transcript.
File name: {datetime.now().strftime('%Y-%m-%d-%H%M')}-{title.lower().replace(' ', '-')}.md
"""
                }]
            },
            timeout=120
        )
        
        claude_result = claude_response.json()
        
        if claude_response.status_code == 200:
            assistant_message = claude_result.get('content', [{}])[0].get('text', '')
            return jsonify({'status': 'success', 'message': 'Processed', 'conversation_id': conversation_id})
        else:
            return jsonify({'status': 'error', 'error': claude_result}), 500
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Your Claude API key (we'll set this as environment variable)
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY')

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/process-conversation', methods=['POST'])
def process_omi_conversation():
    """
    Webhook endpoint that Omi calls when a conversation ends.
    This triggers Claude to process and organize the conversation.
    """
    try:
        # Get data from Omi webhook
        data = request.json
        print(f"Received Omi webhook: {data}")
        
        # Extract conversation details
        conversation_id = data.get('id') or data.get('conversation_id')
        title = data.get('title', 'Untitled Conversation')
        
        # Call Claude API to process this conversation
        claude_response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": CLAUDE_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 8192,
                "messages": [{
                    "role": "user",
                    "content": f"""
You have access to my Omi conversations via the Omi MCP server and my Google Drive via the Google Drive MCP server.

TASK: Process and organize this Omi conversation.

Conversation ID: {conversation_id}
Title: {title}

STEP 1: Use the Omi MCP to read the full conversation transcript.

STEP 2: Analyze the conversation and determine the main topic:
- Is it about Pareto Talent (business operations, hiring, clients)?
- Is it about Slavpreneur/YouTube content (video ideas, content strategy)?
- Is it about personal life or Uruguay relocation?
- Is it a general business insight or learning?

STEP 3: Create a well-formatted markdown document with:
---
# {title}
**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Conversation ID:** {conversation_id}

## Summary
[2-3 sentence summary of the conversation]

## Key Points
- [Main points discussed]

## Decisions Made
- [Any decisions or conclusions]

## Action Items
- [ ] [Specific tasks that came up]

## Ideas & Insights
- [Interesting ideas or realizations]

## Full Transcript
[The actual conversation transcript]
---

STEP 4: Save this document to the appropriate folder in my Google Drive using the Google Drive MCP:

- Pareto Talent topics → /Second Brain/03-Active-Projects/Pareto-Talent/conversations/
- Content/Slavpreneur topics → /Second Brain/02-Knowledge-Base/Content-Ideas/
- Personal topics → /Second Brain/02-Knowledge-Base/Personal/
- Business insights → /Second Brain/02-Knowledge-Base/Business/
- Unclear/General → /Second Brain/01-Captures/Voice-Notes/processed/

File name format: YYYY-MM-DD-HHmm-topic-keywords.md

STEP 5: Respond with a JSON object:
{{
  "status": "success",
  "folder": "[which folder you saved it to]",
  "filename": "[the filename you created]",
  "summary": "[1 sentence about what the conversation was about]"
}}
"""
                }]
            },
            timeout=120  # Give Claude 2 minutes to process
        )
        
        # Parse Claude's response
        claude_result = claude_response.json()
        
        # Extract the result from Claude's response
        if claude_response.status_code == 200:
            assistant_message = claude_result.get('content', [{}])[0].get('text', '')
            
            return jsonify({
                'status': 'success',
                'message': 'Conversation processed and saved to Second Brain',
                'claude_response': assistant_message,
                'conversation_id': conversation_id
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Claude API error',
                'error': claude_result
            }), 500
            
    except Exception as e:
        print(f"Error processing conversation: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/test', methods=['POST'])
def test_endpoint():
    """Test endpoint to manually trigger processing"""
    return jsonify({
        'status': 'test_received',
        'your_api_key_set': CLAUDE_API_KEY is not None,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

