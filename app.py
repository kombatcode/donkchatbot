from flask import Flask, request, jsonify, Response
import requests
import os
import json
import time
import traceback

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ALLOWED_USER_ID = 1444832263
GROUP_CHAT_ID = -1001721934457

# Прямые API вызовы к Telegram
def telegram_api(method, data):
    """Прямой вызов Telegram Bot API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        print(f"📡 API {method}: {result.get('ok', False)}")
        if not result.get('ok'):
            print(f"❌ API Error: {result}")
        return result
    except Exception as e:
        print(f"❌ API Request failed: {e}")
        return {'ok': False, 'error': str(e)}

def get_chat_info(chat_id):
    """Получает информацию о чате"""
    return telegram_api('getChat', {'chat_id': chat_id})

def get_chat_permissions(chat_id):
    """Получает текущие разрешения чата"""
    chat_info = get_chat_info(chat_id)
    if chat_info.get('ok'):
        return chat_info['result'].get('permissions', {})
    return {}

def set_chat_permissions_direct(chat_id, permissions):
    """Устанавливает разрешения чата напрямую через API"""
    data = {
        'chat_id': chat_id,
        'permissions': permissions
    }
    return telegram_api('setChatPermissions', data)

def set_single_permission(chat_id, permission_name, value):
    """Устанавливает одно разрешение, сохраняя остальные"""
    try:
        # Получаем текущие разрешения
        current_permissions = get_chat_permissions(chat_id)
        print(f"🔍 Current permissions: {current_permissions}")
        
        if not current_permissions:
            # Если не удалось получить, используем дефолтные
            current_permissions = {
                'can_send_messages': True,
                'can_send_media_messages': True,
                'can_send_polls': True,
                'can_change_info': False,
                'can_invite_users': True,
                'can_pin_messages': False
            }
        
        # Обновляем только нужное разрешение
        current_permissions[permission_name] = value
        print(f"🔄 New permissions: {current_permissions}")
        
        # Устанавливаем обновленные разрешения
        result = set_chat_permissions_direct(chat_id, current_permissions)
        
        if result.get('ok'):
            print(f"✅ Successfully set {permission_name} to {value}")
            return True
        else:
            print(f"❌ Failed to set {permission_name}: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error in set_single_permission: {e}")
        return False

def test_permission(permission_name, value):
    """Тестирует установку конкретного разрешения"""
    print(f"🧪 Testing {permission_name} = {value}")
    return set_single_permission(GROUP_CHAT_ID, permission_name, value)

def get_mini_app_html():
    """Генерирует HTML с текущими настройками группы"""
    current_permissions = {}
    
    if BOT_TOKEN:
        current_permissions = get_chat_permissions(GROUP_CHAT_ID)
        print(f"📊 Current permissions for HTML: {current_permissions}")
    
    # Значения по умолчанию
    settings = {
        'can_send_messages': current_permissions.get('can_send_messages', True),
        'can_send_media_messages': current_permissions.get('can_send_media_messages', True),
        'can_send_polls': current_permissions.get('can_send_polls', True),
        'can_change_info': current_permissions.get('can_change_info', False),
        'can_invite_users': current_permissions.get('can_invite_users', True),
        'can_pin_messages': current_permissions.get('can_pin_messages', False)
    }
    
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Group Settings</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: var(--tg-theme-bg-color, #ffffff);
            color: var(--tg-theme-text-color, #000000);
            padding-bottom: 80px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
        }}
        .setting {{
            background: var(--tg-theme-secondary-bg-color, #f0f0f0);
            margin: 15px 0;
            padding: 15px;
            border-radius: 12px;
        }}
        .setting-title {{
            font-weight: 600;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .switch {{
            position: relative;
            display: inline-block;
            width: 50px;
            height: 24px;
        }}
        .switch input {{
            opacity: 0;
            width: 0;
            height: 0;
        }}
        .slider {{
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 24px;
        }}
        .slider:before {{
            position: absolute;
            content: "";
            height: 16px;
            width: 16px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }}
        input:checked + .slider {{
            background-color: #007aff;
        }}
        input:checked + .slider:before {{
            transform: translateX(26px);
        }}
        /* ФИКСИРОВАННЫЙ СТАТУС */
        .status {{
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            max-width: 500px;
            padding: 15px 20px;
            border-radius: 12px;
            text-align: center;
            font-weight: 600;
            z-index: 1000;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            display: none;
            animation: slideUp 0.3s ease-out;
            backdrop-filter: blur(10px);
        }}
        @keyframes slideUp {{
            from {{
                opacity: 0;
                transform: translateX(-50%) translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateX(-50%) translateY(0);
            }}
        }}
        .success {{
            background: rgba(76, 175, 80, 0.95);
            color: white;
            border: 2px solid #4CAF50;
        }}
        .error {{
            background: rgba(244, 67, 54, 0.95);
            color: white;
            border: 2px solid #f44336;
        }}
        .warning {{
            background: rgba(255, 152, 0, 0.95);
            color: white;
            border: 2px solid #ff9800;
        }}
        .refresh-btn {{
            background: #007aff;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 10px;
            cursor: pointer;
            margin: 10px 0;
            font-size: 16px;
            font-weight: 600;
        }}
        .permissions-info {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .debug-info {{
            background: #fff3cd;
            padding: 10px;
            border-radius: 8px;
            margin: 10px 0;
            font-size: 12px;
            color: #856404;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 700;
            margin: 25px 0 15px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #007aff;
        }}
        .test-buttons {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin: 15px 0;
        }}
        .test-btn {{
            background: #28a745;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="permissions-info">
            <h3>⚙️ Управление настройками Donk Chat</h3>
            <p><strong>ID группы:</strong> {GROUP_CHAT_ID}</p>
            <p><strong>Метод:</strong> Прямые API вызовы</p>
            <button class="refresh-btn" onclick="loadCurrentSettings()">🔄 Обновить настройки</button>
        </div>

        <div class="debug-info">
            🚀 <strong>ПРЯМЫЕ API ВЫЗОВЫ</strong> - обход pyTelegramBotAPI
        </div>

        <div class="test-buttons">
            <button class="test-btn" onclick="testPermission('can_send_messages', false)">🧪 Выкл сообщения</button>
            <button class="test-btn" onclick="testPermission('can_send_media_messages', false)">🧪 Выкл медиа</button>
            <button class="test-btn" onclick="testPermission('can_send_polls', false)">🧪 Выкл опросы</button>
            <button class="test-btn" onclick="testAllPermissions()">🧪 Тест всех</button>
        </div>
        
        <div class="section-title">💬 Основные разрешения</div>
        
        <div class="setting">
            <div class="setting-title">
                Отправка сообщений
                <label class="switch">
                    <input type="checkbox" id="can_send_messages" {"checked" if settings["can_send_messages"] else ""}>
                    <span class="slider"></span>
                </label>
            </div>
            <p>Участники могут отправлять текстовые сообщения</p>
        </div>

        <div class="setting">
            <div class="setting-title">
                Отправка медиа
                <label class="switch">
                    <input type="checkbox" id="can_send_media_messages" {"checked" if settings["can_send_media_messages"] else ""}>
                    <span class="slider"></span>
                </label>
            </div>
            <p>Фото, видео, стикеры, голосовые сообщения</p>
        </div>

        <div class="setting">
            <div class="setting-title">
                Создание опросов
                <label class="switch">
                    <input type="checkbox" id="can_send_polls" {"checked" if settings["can_send_polls"] else ""}>
                    <span class="slider"></span>
                </label>
            </div>
            <p>Участники могут создавать опросы</p>
        </div>

        <div class="section-title">👥 Управление группой</div>

        <div class="setting">
            <div class="setting-title">
                Изменение информации
                <label class="switch">
                    <input type="checkbox" id="can_change_info" {"checked" if settings["can_change_info"] else ""}>
                    <span class="slider"></span>
                </label>
            </div>
            <p>Изменение названия, фото и описания группы</p>
        </div>

        <div class="setting">
            <div class="setting-title">
                Приглашение пользователей
                <label class="switch">
                    <input type="checkbox" id="can_invite_users" {"checked" if settings["can_invite_users"] else ""}>
                    <span class="slider"></span>
                </label>
            </div>
            <p>Участники могут приглашать новых пользователей</p>
        </div>

        <div class="setting">
            <div class="setting-title">
                Закрепление сообщений
                <label class="switch">
                    <input type="checkbox" id="can_pin_messages" {"checked" if settings["can_pin_messages"] else ""}>
                    <span class="slider"></span>
                </label>
            </div>
            <p>Участники могут закреплять сообщения</p>
        </div>
    </div>

    <!-- СТАТУСНОЕ СООБЩЕНИЕ -->
    <div id="status" class="status"></div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        tg.ready();

        function loadCurrentSettings() {{
            showStatus('🔄 Загрузка текущих настроек...', 'success');
            setTimeout(() => location.reload(), 1000);
        }}

        // ОТДЕЛЬНЫЕ ФУНКЦИИ ДЛЯ КАЖДОГО ПЕРЕКЛЮЧАТЕЛЯ
        function updateSendMessages(enabled) {{
            sendSettingUpdate('can_send_messages', enabled, '💬 Сообщения');
        }}

        function updateSendMedia(enabled) {{
            sendSettingUpdate('can_send_media_messages', enabled, '🖼️ Медиа');
        }}

        function updateSendPolls(enabled) {{
            sendSettingUpdate('can_send_polls', enabled, '📊 Опроcы');
        }}

        function updateChangeInfo(enabled) {{
            sendSettingUpdate('can_change_info', enabled, '✏️ Изменение информации');
        }}

        function updateInviteUsers(enabled) {{
            sendSettingUpdate('can_invite_users', enabled, '👥 Приглашения');
        }}

        function updatePinMessages(enabled) {{
            sendSettingUpdate('can_pin_messages', enabled, '📌 Закрепление');
        }}

        // ТЕСТОВЫЕ ФУНКЦИИ
        function testPermission(permission, value) {{
            sendSettingUpdate(permission, value, `🧪 Тест ${{permission}}`);
        }}

        function testAllPermissions() {{
            const tests = [
                ['can_send_messages', false, '💬 Сообщения'],
                ['can_send_media_messages', false, '🖼️ Медиа'],
                ['can_send_polls', false, '📊 Опроcы']
            ];
            
            showStatus('🧪 Запуск тестов...', 'warning');
            
            tests.forEach(([permission, value, name], index) => {{
                setTimeout(() => {{
                    sendSettingUpdate(permission, value, name);
                }}, index * 2000);
            }});
        }}

        function sendSettingUpdate(setting, value, name) {{
            console.log(`📤 Setting ${{setting}} to ${{value}}`);
            
            const data = {{
                action: 'update_single_setting',
                setting: setting,
                value: value,
                chat_id: {GROUP_CHAT_ID},
                timestamp: Date.now(),
                test_name: name
            }};
            
            try {{
                tg.sendData(JSON.stringify(data));
                showStatus(`✅ ${{name}} ${{value ? 'включены' : 'выключены'}}`, 'success');
            }} catch (error) {{
                console.error('❌ Error sending data:', error);
                showStatus('❌ Ошибка отправки данных', 'error');
            }}
        }}

        document.addEventListener('DOMContentLoaded', function() {{
            // Назначаем обработчики для каждого переключателя
            document.getElementById('can_send_messages').addEventListener('change', function() {{
                updateSendMessages(this.checked);
            }});
            
            document.getElementById('can_send_media_messages').addEventListener('change', function() {{
                updateSendMedia(this.checked);
            }});
            
            document.getElementById('can_send_polls').addEventListener('change', function() {{
                updateSendPolls(this.checked);
            }});
            
            document.getElementById('can_change_info').addEventListener('change', function() {{
                updateChangeInfo(this.checked);
            }});
            
            document.getElementById('can_invite_users').addEventListener('change', function() {{
                updateInviteUsers(this.checked);
            }});
            
            document.getElementById('can_pin_messages').addEventListener('change', function() {{
                updatePinMessages(this.checked);
            }});
        }});

        function showStatus(message, type) {{
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + type;
            status.style.display = 'block';
            
            setTimeout(() => {{
                status.style.display = 'none';
            }}, 4000);
        }}

        setTimeout(() => {{
            showStatus('🚀 Прямые API вызовы активны!', 'success');
        }}, 1000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    if BOT_TOKEN:
        return "✅ Telegram MiniApp Server is running! BOT_TOKEN is set."
    else:
        return "⚠️ Telegram MiniApp Server is running in demo mode. Set BOT_TOKEN environment variable."

@app.route('/group_settings.html')
def group_settings():
    return Response(get_mini_app_html(), mimetype='text/html')

# Простой вебхук для обработки данных от MiniApp
@app.route('/webhook', methods=['POST'])
def webhook():
    if not BOT_TOKEN:
        return jsonify({'ok': False, 'error': 'Bot token not set'}), 400
        
    try:
        data = request.get_json()
        print(f"📨 Received webhook data: {data}")
        
        if data.get('action') == 'update_single_setting':
            setting = data.get('setting')
            value = data.get('value')
            chat_id = data.get('chat_id', GROUP_CHAT_ID)
            test_name = data.get('test_name', 'Настройка')
            
            print(f"🔄 Processing: {setting} = {value} for chat {chat_id}")
            
            # Используем прямые API вызовы
            success = set_single_permission(chat_id, setting, value)
            
            if success:
                response = {
                    'ok': True,
                    'message': f'{test_name} {"включены" if value else "выключены"}'
                }
            else:
                response = {
                    'ok': False,
                    'error': f'Не удалось изменить {test_name}'
                }
            
            return jsonify(response)
        
        return jsonify({'ok': False, 'error': 'Unknown action'})
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

# Простая проверка прав
def check_user_access(user_id):
    return user_id == ALLOWED_USER_ID

# Тестовый endpoint для проверки API
@app.route('/api/test_permission', methods=['POST'])
def api_test_permission():
    """API endpoint для тестирования разрешений"""
    try:
        data = request.get_json()
        permission = data.get('permission')
        value = data.get('value', False)
        
        if not permission:
            return jsonify({'ok': False, 'error': 'Permission required'})
        
        success = test_permission(permission, value)
        
        return jsonify({
            'ok': success,
            'permission': permission,
            'value': value,
            'message': f'Set {permission} to {value}'
        })
        
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})

if __name__ == '__main__':
    print("🚀 Starting server with DIRECT API CALLS")
    print(f"🎯 Target chat: {GROUP_CHAT_ID}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
