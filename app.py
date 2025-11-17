from flask import Flask, request, jsonify, Response
import requests
import os
import json
import time
import traceback

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ALLOWED_USER_ID = 1444832263
GROUP_CHAT_ID = -1001721934457  # Ваш чат Donk Chat

# ПЕРЕМЕННЫЕ-ФЛАГИ ДЛЯ КАЖДОГО ПОЛЗУНКА
current_settings = {
    'can_send_messages': True,
    'can_send_media_messages': True,
    'can_send_polls': True,
    'can_change_info': False,
    'can_invite_users': True,
    'can_pin_messages': False
}

# Прямые API вызовы к Telegram
def telegram_api(method, data):
    """Прямой вызов Telegram Bot API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        print(f"📡 Calling API: {method} with data: {data}")
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        print(f"📡 API Response: {result}")
        return result
    except Exception as e:
        print(f"❌ API Request failed: {e}")
        return {'ok': False, 'error': str(e)}

def get_chat_info(chat_id):
    """Получает информацию о чате"""
    return telegram_api('getChat', {'chat_id': chat_id})

def apply_all_permissions():
    """Применяет ВСЕ текущие настройки из переменных"""
    try:
        print(f"🎯 APPLYING ALL SETTINGS: {current_settings}")
        
        data = {
            'chat_id': GROUP_CHAT_ID,
            'permissions': current_settings
        }
        
        result = telegram_api('setChatPermissions', data)
        
        if result.get('ok'):
            print("✅ ALL SETTINGS APPLIED SUCCESSFULLY!")
            return True
        else:
            print(f"❌ FAILED TO APPLY SETTINGS: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error in apply_all_permissions: {e}")
        return False

def update_setting(setting_name, new_value):
    """Обновляет одну настройку и сразу применяет ВСЕ настройки"""
    try:
        print(f"🔄 UPDATING SETTING: {setting_name} -> {new_value}")
        
        # Обновляем переменную
        current_settings[setting_name] = new_value
        print(f"📊 CURRENT SETTINGS AFTER UPDATE: {current_settings}")
        
        # Применяем ВСЕ настройки
        success = apply_all_permissions()
        
        if success:
            print(f"✅ SUCCESS: {setting_name} set to {new_value}")
            return True
        else:
            print(f"❌ FAILED: Could not set {setting_name}")
            return False
            
    except Exception as e:
        print(f"❌ Error in update_setting: {e}")
        return False

def load_current_settings_from_telegram():
    """Загружает текущие настройки из Telegram и обновляет переменные"""
    try:
        print("🔍 Loading current settings from Telegram...")
        chat_info = get_chat_info(GROUP_CHAT_ID)
        
        if chat_info.get('ok'):
            permissions = chat_info['result'].get('permissions', {})
            print(f"📋 Loaded permissions from Telegram: {permissions}")
            
            # Обновляем наши переменные
            for key in current_settings.keys():
                if key in permissions:
                    current_settings[key] = permissions[key]
            
            print(f"🔄 Updated current_settings: {current_settings}")
            return True
        else:
            print("❌ Failed to load settings from Telegram")
            return False
            
    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        return False

def test_specific_setting(setting_name, value):
    """Тестирует конкретную настройку"""
    print(f"🧪 TESTING: {setting_name} = {value}")
    return update_setting(setting_name, value)

def test_all_settings():
    """Тестирует все настройки по очереди"""
    tests = [
        ('can_send_messages', False, '💬 Сообщения'),
        ('can_send_media_messages', False, '🖼️ Медиа'),
        ('can_send_polls', False, '📊 Опроcы'),
        ('can_change_info', True, '✏️ Изменение инфо'),
        ('can_invite_users', False, '👥 Приглашения'),
        ('can_pin_messages', True, '📌 Закрепление')
    ]
    
    results = []
    for setting, value, name in tests:
        success = test_specific_setting(setting, value)
        results.append(f"{name}: {'✅' if success else '❌'}")
        time.sleep(1)  # Небольшая пауза между запросами
    
    return results

def get_mini_app_html():
    """Генерирует HTML с текущими настройками из переменных"""
    print(f"🎨 Generating HTML with settings: {current_settings}")
    
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
        .vars-display {{
            background: #e9ecef;
            padding: 10px;
            border-radius: 8px;
            margin: 10px 0;
            font-family: monospace;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="permissions-info">
            <h3>⚙️ Управление настройками Donk Chat</h3>
            <p><strong>ID группы:</strong> {GROUP_CHAT_ID}</p>
            <p><strong>Метод:</strong> Переменные-флаги + API</p>
            <button class="refresh-btn" onclick="loadCurrentSettings()">🔄 Загрузить из Telegram</button>
            <button class="refresh-btn" onclick="applyAllSettings()">🎯 Применить все настройки</button>
        </div>

        <div class="debug-info">
            🎯 <strong>СИСТЕМА ПЕРЕМЕННЫХ</strong> - каждый ползунок меняет переменную
        </div>

        <div class="vars-display">
            <strong>Текущие переменные:</strong><br>
            {json.dumps(current_settings, indent=2, ensure_ascii=False)}
        </div>

        <div class="test-buttons">
            <button class="test-btn" onclick="testSetting('can_send_messages', false)">🧪 Выкл сообщения</button>
            <button class="test-btn" onclick="testSetting('can_send_media_messages', false)">🧪 Выкл медиа</button>
            <button class="test-btn" onclick="testSetting('can_send_polls', false)">🧪 Выкл опросы</button>
            <button class="test-btn" onclick="testAllSettings()">🧪 Тест всех</button>
        </div>
        
        <div class="section-title">💬 Основные разрешения</div>
        
        <div class="setting">
            <div class="setting-title">
                Отправка сообщений
                <label class="switch">
                    <input type="checkbox" id="can_send_messages" {"checked" if current_settings["can_send_messages"] else ""}>
                    <span class="slider"></span>
                </label>
            </div>
            <p>Участники могут отправлять текстовые сообщения</p>
        </div>

        <div class="setting">
            <div class="setting-title">
                Отправка медиа
                <label class="switch">
                    <input type="checkbox" id="can_send_media_messages" {"checked" if current_settings["can_send_media_messages"] else ""}>
                    <span class="slider"></span>
                </label>
            </div>
            <p>Фото, видео, стикеры, голосовые сообщения</p>
        </div>

        <div class="setting">
            <div class="setting-title">
                Создание опросов
                <label class="switch">
                    <input type="checkbox" id="can_send_polls" {"checked" if current_settings["can_send_polls"] else ""}>
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
                    <input type="checkbox" id="can_change_info" {"checked" if current_settings["can_change_info"] else ""}>
                    <span class="slider"></span>
                </label>
            </div>
            <p>Изменение названия, фото и описания группы</p>
        </div>

        <div class="setting">
            <div class="setting-title">
                Приглашение пользователей
                <label class="switch">
                    <input type="checkbox" id="can_invite_users" {"checked" if current_settings["can_invite_users"] else ""}>
                    <span class="slider"></span>
                </label>
            </div>
            <p>Участники могут приглашать новых пользователей</p>
        </div>

        <div class="setting">
            <div class="setting-title">
                Закрепление сообщений
                <label class="switch">
                    <input type="checkbox" id="can_pin_messages" {"checked" if current_settings["can_pin_messages"] else ""}>
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
            showStatus('🔄 Загрузка настроек из Telegram...', 'warning');
            // Отправляем запрос на загрузку настроек
            sendAction('load_settings');
        }}

        function applyAllSettings() {{
            showStatus('🎯 Применение всех настроек...', 'warning');
            sendAction('apply_all_settings');
        }}

        function testSetting(setting, value) {{
            updateSetting(setting, value, `🧪 Тест ${{setting}}`);
        }}

        function testAllSettings() {{
            showStatus('🧪 Запуск тестов всех настроек...', 'warning');
            sendAction('test_all_settings');
        }}

        // ОСНОВНЫЕ ФУНКЦИИ ДЛЯ ПОЛЗУНКОВ
        function updateSendMessages(enabled) {{
            updateSetting('can_send_messages', enabled, '💬 Сообщения');
        }}

        function updateSendMedia(enabled) {{
            updateSetting('can_send_media_messages', enabled, '🖼️ Медиа');
        }}

        function updateSendPolls(enabled) {{
            updateSetting('can_send_polls', enabled, '📊 Опроcы');
        }}

        function updateChangeInfo(enabled) {{
            updateSetting('can_change_info', enabled, '✏️ Изменение информации');
        }}

        function updateInviteUsers(enabled) {{
            updateSetting('can_invite_users', enabled, '👥 Приглашения');
        }}

        function updatePinMessages(enabled) {{
            updateSetting('can_pin_messages', enabled, '📌 Закрепление');
        }}

        function updateSetting(setting, value, name) {{
            console.log(`🔄 Updating ${{setting}} to ${{value}}`);
            
            const data = {{
                action: 'update_setting',
                setting: setting,
                value: value,
                chat_id: {GROUP_CHAT_ID},
                setting_name: name,
                timestamp: Date.now()
            }};
            
            sendDataToServer(data);
            showStatus(`🔄 ${{name}}: ${{value ? 'ВКЛ' : 'ВЫКЛ'}}`, 'warning');
        }}

        function sendAction(action) {{
            const data = {{
                action: action,
                chat_id: {GROUP_CHAT_ID},
                timestamp: Date.now()
            }};
            sendDataToServer(data);
        }}

        function sendDataToServer(data) {{
            try {{
                tg.sendData(JSON.stringify(data));
                console.log('📤 Data sent:', data);
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
            showStatus('🎯 Система переменных активна!', 'success');
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

# Вебхук для обработки всех действий
@app.route('/webhook', methods=['POST'])
def webhook():
    if not BOT_TOKEN:
        return jsonify({'ok': False, 'error': 'Bot token not set'}), 400
        
    try:
        data = request.get_json()
        print(f"📨 Received webhook data: {data}")
        
        action = data.get('action')
        chat_id = data.get('chat_id', GROUP_CHAT_ID)
        
        if action == 'update_setting':
            # ОБНОВЛЯЕМ ПЕРЕМЕННУЮ И ПРИМЕНЯЕМ НАСТРОЙКИ
            setting = data.get('setting')
            value = data.get('value')
            setting_name = data.get('setting_name', 'Настройка')
            
            print(f"🔄 UPDATE SETTING: {setting} = {value}")
            
            success = update_setting(setting, value)
            
            if success:
                response = {
                    'ok': True,
                    'message': f'{setting_name} установлены в {value}',
                    'current_settings': current_settings
                }
            else:
                response = {
                    'ok': False,
                    'error': f'Не удалось установить {setting_name}',
                    'current_settings': current_settings
                }
            
            return jsonify(response)
            
        elif action == 'load_settings':
            # ЗАГРУЖАЕМ НАСТРОЙКИ ИЗ TELEGRAM
            success = load_current_settings_from_telegram()
            
            if success:
                response = {
                    'ok': True,
                    'message': 'Настройки загружены из Telegram',
                    'current_settings': current_settings
                }
            else:
                response = {
                    'ok': False,
                    'error': 'Не удалось загрузить настройки',
                    'current_settings': current_settings
                }
            
            return jsonify(response)
            
        elif action == 'apply_all_settings':
            # ПРИМЕНЯЕМ ВСЕ ТЕКУЩИЕ НАСТРОЙКИ
            success = apply_all_permissions()
            
            if success:
                response = {
                    'ok': True,
                    'message': 'Все настройки применены',
                    'current_settings': current_settings
                }
            else:
                response = {
                    'ok': False,
                    'error': 'Не удалось применить настройки',
                    'current_settings': current_settings
                }
            
            return jsonify(response)
            
        elif action == 'test_all_settings':
            # ТЕСТИРУЕМ ВСЕ НАСТРОЙКИ
            results = test_all_settings()
            
            response = {
                'ok': True,
                'message': 'Тестирование завершено',
                'results': results,
                'current_settings': current_settings
            }
            
            return jsonify(response)
        
        return jsonify({'ok': False, 'error': 'Unknown action'})
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

# Простая проверка прав
def check_user_access(user_id):
    return user_id == ALLOWED_USER_ID

if __name__ == '__main__':
    print("🚀 Starting server with VARIABLE-BASED SYSTEM")
    print(f"🎯 Target chat: {GROUP_CHAT_ID}")
    print(f"📊 Initial settings: {current_settings}")
    
    # Загружаем текущие настройки при старте
    load_current_settings_from_telegram()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
