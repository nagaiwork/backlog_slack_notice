import json
import urllib3

http = urllib3.PoolManager()

def lambda_handler(event, context):
    # Slack通知時にメンション付与の為、SlackIDとbacklogの氏名をマッピング
    # key:SlackID, Value:backlogでの氏名
    mention_list = {
        "U074D9X38FM": "永井 伸明",
        "U074D9X38F2": "永井 太郎"
    }
    
    # 受け取ったJSONデータをパース
    data = json.loads(event['body'])
    print({"data": data})
    
    notice_type = data['type']
    print({"notice_type": notice_type})

    created_user = data['createdUser']['name']
    
    # このサンプルでは課題の作成者に対してのメンションを作成
    mention_targets = get_keys_from_value(mention_list, created_user)
    print({"mention_targets": mention_targets})
    
    # メンション文字列を作成
    mention_string = ' '.join([f"<@{user_id}>" for user_id in mention_targets])
    print({"mention_string": mention_string})
    
    # JSONデータから必要なフィールドを取得
    project_name = data['project']['name']
    project_key = data['project']['projectKey']
    issue_summary = data['content'].get('summary', 'No summary provided')
    issue_description = data['content'].get('description', 'No description provided')
    issue_status = data['content']['status']['name']
    issue_comment = ""
    if 'content' in data and 'comment' in data['content'] and data['content']['comment'] is not None:
        issue_comment = data['content']['comment']['content']

    # 通知メッセージを作成
    # see: https://api.slack.com/reference/messaging/attachments
    message = {
        "attachments": [
            {
                "mrkdwn_in": ["text"],
                "color": "#6495ed",
                "pretext": f"{mention_string}",
                "title": f"{project_name}",
                "title_link": f"https://<自身のBacklogの組織名>.backlog.com/projects/{project_key}",
                "text": f"{issue_summary}",
                "fields": [
                    {
                        "title": "issue_description",
                        "value": f"{issue_description}",
                        "short": True
                    },
                    {
                        "title": "issue_status",
                        "value": f"{issue_status}",
                        "short": True
                    },
                    {
                        "title": "comment",
                        "value": f"{issue_comment}",
                        "short": False
                    }
                ]
            }
        ]
    }
    
    # Slack Incoming WebhookのURL
    webhook_url = '<incoming webhook>'
    
    # Slackに送信
    response = http.request(
        'POST',
        webhook_url,
        body=json.dumps(message).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    # 結果をログに出力
    print({
        "status_code": response.status,
        "response": response.data.decode('utf-8')
    })
    
    return {
        'statusCode': response.status,
        'body': json.dumps('Notification sent successfully!')
    }

# 辞書型オブジェクトのValueからKeyのリストを取得する
def get_keys_from_value(d, val):
    return [k for k, v in d.items() if v == val]
