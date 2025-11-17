from flask import Flask, request, jsonify, Response
import requests
import os
import json
import time

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ALLOWED_USER_ID = 1444832263
GROUP_CHAT_ID = -1001721934457

# Текущие настройки в памяти
current_settings = {
    'can_send_messages': True,
    'can_send_media_messages': True,
    'can_send_polls': True,
    'can_change_info': False,
    'can_invite_users': True,
    'can_pin_messages': False
}

def telegram_api(method, data):
    """Прямой вызов Telegram Bot API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        print(f"📡 API: {method} -> {data}")
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        print(f"📡 Response: {result}")
        return result
    except Exception as e:
        print(f"❌ API Error: {e}")
        return {'ok': False}

def apply_settings():
    """Применяет текущие настройки к группе"""
    data = {
        'chat_id': GROUP_CHAT_ID,
        'permissions': current_settings
    }
    return telegram_api('setChatPermissions', data)

def update_setting(setting_name, value):
    """Обновляет настройку и применяет её"""
    print(f"🔄 Setting {setting_name} to {value}")
    current_settings[setting_name] = value
    return apply_settings()

def get_current_settings():
    """Получает текущие настройки из Telegram"""
    result = telegram_api('getChat', {'chat_id': GROUP_CHAT_ID})
    if result.get('ok'):
        return result['result'].get('permissions', {})
    return {}

def sync_settings():
    """Синхронизирует настройки с Telegram"""
    global current_settings
    telegram_settings = get_current_settings()
    if telegram_settings:
        for key in current_settings.keys():
            if key in telegram_settings:
                current_settings[key] = telegram_settings[key]
        print(f"🔄 Synced: {current_settings}")
        return True
    return False

# Загружаем настройки при старте
sync_settings()

@app.route('/')
def home():
    return """
    <h1>🎛️ Group Settings Manager</h1>
    <p>Go to <a href="/settings">/settings</a> to manage group permissions</p>
    <p>Current settings: <pre>{}</pre></p>
    """.format(json.dumps(current_settings, indent=2))

@app.route('/settings')
def settings_page():
    """Главная страница настроек"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Group Settings</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }
            .setting {
                background: #f5f5f5;
                padding: 15px;
                margin: 10px 0;
                border-radius: 10px;
            }
            .switch {
                position: relative;
                display: inline-block;
                width: 60px;
                height: 34px;
            }
            .switch input {
                opacity: 0;
                width: 0;
                height: 0;
            }
            .slider {
                position: absolute;
                cursor: pointer;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: #ccc;
                transition: .4s;
                border-radius: 34px;
            }
            .slider:before {
                position: absolute;
                content: "";
                height: 26px;
                width: 26px;
                left: 4px;
                bottom: 4px;
                background-color: white;
                transition: .4s;
                border-radius: 50%;
            }
            input:checked + .slider {
                background-color: #2196F3;
            }
            input:checked + .slider:before {
                transform: translateX(26px);
            }
            button {
                background: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                margin: 5px;
                border-radius: 5px;
                cursor: pointer;
            }
            .status {
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                display: none;
            }
            .success { background: #d4edda; color: #155724; }
            .error { background: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <h1>⚙️ Group Settings</h1>
        
        <div>
            <button onclick="syncSettings()">🔄 Sync with Telegram</button>
            <button onclick="applyAll()">🎯 Apply All Settings</button>
            <button onclick="testDisableMessages()">🧪 Test: Disable Messages</button>
        </div>

        <div id="status" class="status"></div>

        <div class="setting">
            <h3>💬 Send Messages: <span id="messages_status">ON</span></h3>
            <label class="switch">
                <input type="checkbox" id="messages" onchange="toggleSetting('can_send_messages', this.checked, 'messages_status')">
                <span class="slider"></span>
            </label>
            <p>Allow members to send text messages</p>
        </div>

        <div class="setting">
            <h3>🖼️ Send Media: <span id="media_status">ON</span></h3>
            <label class="switch">
                <input type="checkbox" id="media" onchange="toggleSetting('can_send_media_messages', this.checked, 'media_status')">
                <span class="slider"></span>
            </label>
            <p>Allow members to send photos, videos, etc.</p>
        </div>

        <div class="setting">
            <h3>📊 Send Polls: <span id="polls_status">ON</span></h3>
            <label class="switch">
                <input type="checkbox" id="polls" onchange="toggleSetting('can_send_polls', this.checked, 'polls_status')">
                <span class="slider"></span>
            </label>
            <p>Allow members to create polls</p>
        </div>

        <div class="setting">
            <h3>✏️ Change Info: <span id="info_status">OFF</span></h3>
            <label class="switch">
                <input type="checkbox" id="info" onchange="toggleSetting('can_change_info', this.checked, 'info_status')">
                <span class="slider"></span>
            </label>
            <p>Allow members to change group info</p>
        </div>

        <div class="setting">
            <h3>👥 Invite Users: <span id="invite_status">ON</span></h3>
            <label class="switch">
                <input type="checkbox" id="invite" onchange="toggleSetting('can_invite_users', this.checked, 'invite_status')">
                <span class="slider"></span>
            </label>
            <p>Allow members to invite users</p>
        </div>

        <div class="setting">
            <h3>📌 Pin Messages: <span id="pin_status">OFF</span></h3>
            <label class="switch">
                <input type="checkbox" id="pin" onchange="toggleSetting('can_pin_messages', this.checked, 'pin_status')">
                <span class="slider"></span>
            </label>
            <p>Allow members to pin messages</p>
        </div>

        <script>
            // Загружаем текущие настройки при загрузке страницы
            fetch('/api/settings')
                .then(r => r.json())
                .then(settings => {
                    updateUI(settings);
                });

            function updateUI(settings) {
                document.getElementById('messages').checked = settings.can_send_messages;
                document.getElementById('media').checked = settings.can_send_media_messages;
                document.getElementById('polls').checked = settings.can_send_polls;
                document.getElementById('info').checked = settings.can_change_info;
                document.getElementById('invite').checked = settings.can_invite_users;
                document.getElementById('pin').checked = settings.can_pin_messages;
                
                document.getElementById('messages_status').textContent = settings.can_send_messages ? 'ON' : 'OFF';
                document.getElementById('media_status').textContent = settings.can_send_media_messages ? 'ON' : 'OFF';
                document.getElementById('polls_status').textContent = settings.can_send_polls ? 'ON' : 'OFF';
                document.getElementById('info_status').textContent = settings.can_change_info ? 'ON' : 'OFF';
                document.getElementById('invite_status').textContent = settings.can_invite_users ? 'ON' : 'OFF';
                document.getElementById('pin_status').textContent = settings.can_pin_messages ? 'ON' : 'OFF';
            }

            function toggleSetting(setting, value, statusElement) {
                fetch('/api/update', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({setting: setting, value: value})
                })
                .then(r => r.json())
                .then(result => {
                    if (result.success) {
                        showStatus('✅ Setting updated successfully!', 'success');
                        document.getElementById(statusElement).textContent = value ? 'ON' : 'OFF';
                    } else {
                        showStatus('❌ Error: ' + result.error, 'error');
                        // Возвращаем переключатель в предыдущее состояние
                        document.getElementById(setting.split('_').pop()).checked = !value;
                    }
                })
                .catch(error => {
                    showStatus('❌ Network error', 'error');
                    document.getElementById(setting.split('_').pop()).checked = !value;
                });
            }

            function syncSettings() {
                showStatus('🔄 Syncing with Telegram...', 'success');
                fetch('/api/sync')
                    .then(r => r.json())
                    .then(result => {
                        if (result.success) {
                            updateUI(result.settings);
                            showStatus('✅ Settings synced!', 'success');
                        } else {
                            showStatus('❌ Sync failed', 'error');
                        }
                    });
            }

            function applyAll() {
                showStatus('🎯 Applying all settings...', 'success');
                fetch('/api/apply')
                    .then(r => r.json())
                    .then(result => {
                        if (result.success) {
                            showStatus('✅ All settings applied!', 'success');
                        } else {
                            showStatus('❌ Apply failed', 'error');
                        }
                    });
            }

            function testDisableMessages() {
                fetch('/api/update', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({setting: 'can_send_messages', value: false})
                })
                .then(r => r.json())
                .then(result => {
                    if (result.success) {
                        updateUI(result.settings);
                        showStatus('🧪 Messages disabled for testing!', 'success');
                    } else {
                        showStatus('❌ Test failed: ' + result.error, 'error');
                    }
                });
            }

            function showStatus(message, type) {
                const status = document.getElementById('status');
                status.textContent = message;
                status.className = 'status ' + type;
                status.style.display = 'block';
                setTimeout(() => status.style.display = 'none', 3000);
            }
        </script>
    </body>
    </html>
    """
    return html

# API endpoints
@app.route('/api/settings')
def api_get_settings():
    """Возвращает текущие настройки"""
    return jsonify(current_settings)

@app.route('/api/update', methods=['POST'])
def api_update_setting():
    """Обновляет одну настройку"""
    try:
        data = request.get_json()
        setting = data.get('setting')
        value = data.get('value')
        
        if setting not in current_settings:
            return jsonify({'success': False, 'error': 'Invalid setting'})
        
        result = update_setting(setting, value)
        
        if result.get('ok'):
            return jsonify({
                'success': True, 
                'settings': current_settings,
                'message': f'{setting} set to {value}'
            })
        else:
            return jsonify({
                'success': False, 
                'error': 'Telegram API error',
                'settings': current_settings
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/sync')
def api_sync_settings():
    """Синхронизирует настройки с Telegram"""
    try:
        success = sync_settings()
        return jsonify({
            'success': success,
            'settings': current_settings,
            'message': 'Settings synced' if success else 'Sync failed'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/apply')
def api_apply_settings():
    """Применяет все текущие настройки"""
    try:
        result = apply_settings()
        return jsonify({
            'success': result.get('ok', False),
            'settings': current_settings,
            'message': 'Settings applied' if result.get('ok') else 'Apply failed'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Простой бот для команды /settings
@app.route('/bot', methods=['POST'])
def bot_webhook():
    """Webhook для бота"""
    if not BOT_TOKEN:
        return 'OK'
    
    data = request.get_json()
    
    # Обрабатываем команду /settings
    if 'message' in data and 'text' in data['message']:
        text = data['message']['text']
        chat_id = data['message']['chat']['id']
        user_id = data['message']['from']['id']
        
        if user_id != ALLOWED_USER_ID:
            telegram_api('sendMessage', {
                'chat_id': chat_id,
                'text': '🚫 Access denied'
            })
            return 'OK'
        
        if text == '/start' or text == '/settings':
            # Отправляем ссылку на настройки
            webapp_url = f"https://{request.host}/settings"
            telegram_api('sendMessage', {
                'chat_id': chat_id,
                'text': f'🎛️ Group Settings Manager\n\nOpen settings: {webapp_url}',
                'reply_markup': {
                    'inline_keyboard': [[{
                        'text': '⚙️ Open Settings',
                        'web_app': {'url': webapp_url}
                    }]]
                }
            })
    
    return 'OK'

if __name__ == '__main__':
    print("🚀 Starting Group Settings Manager")
    print(f"🎯 Group: {GROUP_CHAT_ID}")
    print(f"📊 Initial settings: {current_settings}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
