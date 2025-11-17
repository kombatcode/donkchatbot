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
    'can_send_photos': True,
    'can_send_videos': True,
    'can_send_video_notes': True,
    'can_send_voice_notes': True,
    'can_send_stickers': True,
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
        'permissions': {
            'can_send_messages': current_settings['can_send_messages'],
            'can_send_media_messages': current_settings['can_send_media_messages'],
            'can_send_photos': current_settings['can_send_photos'],
            'can_send_videos': current_settings['can_send_videos'],
            'can_send_video_notes': current_settings['can_send_video_notes'],
            'can_send_voice_notes': current_settings['can_send_voice_notes'],
            'can_send_stickers': current_settings['can_send_stickers'],
            'can_send_polls': current_settings['can_send_polls'],
            'can_change_info': current_settings['can_change_info'],
            'can_invite_users': current_settings['can_invite_users'],
            'can_pin_messages': current_settings['can_pin_messages']
        }
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
    """Главная страница - только для Telegram"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Group Settings</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
            }
            .container {
                background: rgba(255,255,255,0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            h1 {
                font-size: 24px;
                margin-bottom: 10px;
            }
            p {
                opacity: 0.8;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎛️ Donk Chat Settings</h1>
            <p>Этот интерфейс работает только через Telegram</p>
            <p>Откройте через бота командой /settings</p>
        </div>
    </body>
    </html>
    """

@app.route('/settings')
def settings_page():
    """Страница настроек ТОЛЬКО для Telegram WebApp"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Donk Chat Settings</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            :root {{
                --primary: #007aff;
                --success: #34c759;
                --danger: #ff3b30;
                --bg: var(--tg-theme-bg-color, #ffffff);
                --card-bg: var(--tg-theme-secondary-bg-color, #f2f2f7);
                --text: var(--tg-theme-text-color, #000000);
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: var(--bg);
                color: var(--text);
                line-height: 1.6;
                padding: 20px;
                max-width: 600px;
                margin: 0 auto;
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding: 20px 0;
            }}
            
            .header h1 {{
                font-size: 28px;
                font-weight: 700;
                margin-bottom: 8px;
            }}
            
            .header p {{
                opacity: 0.7;
                font-size: 16px;
            }}
            
            .control-panel {{
                background: var(--card-bg);
                padding: 20px;
                border-radius: 16px;
                margin-bottom: 25px;
                text-align: center;
            }}
            
            .btn {{
                background: var(--primary);
                color: white;
                border: none;
                padding: 12px 20px;
                margin: 5px;
                border-radius: 10px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                transition: all 0.2s;
            }}
            
            .btn:hover {{
                opacity: 0.9;
                transform: translateY(-1px);
            }}
            
            .btn-test {{
                background: #ff9500;
            }}
            
            .section {{
                margin-bottom: 30px;
            }}
            
            .section-title {{
                font-size: 20px;
                font-weight: 700;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid var(--primary);
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .setting {{
                background: var(--card-bg);
                padding: 20px;
                margin: 15px 0;
                border-radius: 14px;
                transition: all 0.3s ease;
            }}
            
            .setting:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            
            .setting-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
            }}
            
            .setting-title {{
                font-weight: 600;
                font-size: 17px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .setting-description {{
                opacity: 0.7;
                font-size: 14px;
                margin-top: 5px;
            }}
            
            /* Switch styles */
            .switch {{
                position: relative;
                display: inline-block;
                width: 54px;
                height: 32px;
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
                border-radius: 32px;
            }}
            
            .slider:before {{
                position: absolute;
                content: "";
                height: 26px;
                width: 26px;
                left: 3px;
                bottom: 3px;
                background-color: white;
                transition: .4s;
                border-radius: 50%;
            }}
            
            input:checked + .slider {{
                background-color: var(--success);
            }}
            
            input:checked + .slider:before {{
                transform: translateX(22px);
            }}
            
            /* Status message */
            .status {{
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                width: 90%;
                max-width: 500px;
                padding: 16px 20px;
                border-radius: 12px;
                text-align: center;
                font-weight: 600;
                z-index: 1000;
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
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
            
            .status.success {{
                background: rgba(52, 199, 89, 0.95);
                color: white;
            }}
            
            .status.error {{
                background: rgba(255, 59, 48, 0.95);
                color: white;
            }}
            
            .status.warning {{
                background: rgba(255, 149, 0, 0.95);
                color: white;
            }}
            
            .status.info {{
                background: rgba(0, 122, 255, 0.95);
                color: white;
            }}
            
            .emoji {{
                font-size: 20px;
            }}
            
            .access-denied {{
                text-align: center;
                padding: 40px 20px;
                color: #ff3b30;
            }}
        </style>
    </head>
    <body>
        <div id="app-content">
            <div class="header">
                <h1>⚙️ Donk Chat Settings</h1>
                <p>Управление разрешениями группы</p>
            </div>
            
            <div class="control-panel">
                <button class="btn" onclick="syncSettings()">🔄 Синхронизировать</button>
                <button class="btn" onclick="applyAllSettings()">🎯 Применить все</button>
                <button class="btn btn-test" onclick="testDisableMessages()">🧪 Тест: Выкл сообщения</button>
            </div>

            <div id="status" class="status"></div>

            <!-- Основные разрешения -->
            <div class="section">
                <div class="section-title">
                    <span class="emoji">💬</span>
                    Основные разрешения
                </div>
                
                <div class="setting">
                    <div class="setting-header">
                        <div class="setting-title">
                            <span class="emoji">💬</span>
                            Отправка сообщений
                        </div>
                        <label class="switch">
                            <input type="checkbox" id="can_send_messages" onchange="toggleSetting('can_send_messages', this.checked)">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="setting-description">Участники могут отправлять текстовые сообщения</div>
                </div>

                <div class="setting">
                    <div class="setting-header">
                        <div class="setting-title">
                            <span class="emoji">📊</span>
                            Создание опросов
                        </div>
                        <label class="switch">
                            <input type="checkbox" id="can_send_polls" onchange="toggleSetting('can_send_polls', this.checked)">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="setting-description">Участники могут создавать опросы и викторины</div>
                </div>
            </div>

            <!-- Медиафайлы -->
            <div class="section">
                <div class="section-title">
                    <span class="emoji">🖼️</span>
                    Медиафайлы
                </div>
                
                <div class="setting">
                    <div class="setting-header">
                        <div class="setting-title">
                            <span class="emoji">🖼️</span>
                            Все медиа
                        </div>
                        <label class="switch">
                            <input type="checkbox" id="can_send_media_messages" onchange="toggleSetting('can_send_media_messages', this.checked)">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="setting-description">Все типы медиафайлов (общая настройка)</div>
                </div>

                <div class="setting">
                    <div class="setting-header">
                        <div class="setting-title">
                            <span class="emoji">📸</span>
                            Фотографии
                        </div>
                        <label class="switch">
                            <input type="checkbox" id="can_send_photos" onchange="toggleSetting('can_send_photos', this.checked)">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="setting-description">Отправка изображений и фотографий</div>
                </div>

                <div class="setting">
                    <div class="setting-header">
                        <div class="setting-title">
                            <span class="emoji">🎥</span>
                            Видео
                        </div>
                        <label class="switch">
                            <input type="checkbox" id="can_send_videos" onchange="toggleSetting('can_send_videos', this.checked)">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="setting-description">Отправка видеофайлов</div>
                </div>

                <div class="setting">
                    <div class="setting-header">
                        <div class="setting-title">
                            <span class="emoji">📹</span>
                            Видеосообщения
                        </div>
                        <label class="switch">
                            <input type="checkbox" id="can_send_video_notes" onchange="toggleSetting('can_send_video_notes', this.checked)">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="setting-description">Круглые видео-сообщения (video notes)</div>
                </div>

                <div class="setting">
                    <div class="setting-header">
                        <div class="setting-title">
                            <span class="emoji">🎤</span>
                            Голосовые сообщения
                        </div>
                        <label class="switch">
                            <input type="checkbox" id="can_send_voice_notes" onchange="toggleSetting('can_send_voice_notes', this.checked)">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="setting-description">Отправка голосовых сообщений (войсы)</div>
                </div>

                <div class="setting">
                    <div class="setting-header">
                        <div class="setting-title">
                            <span class="emoji">🩷</span>
                            Стикеры и GIF
                        </div>
                        <label class="switch">
                            <input type="checkbox" id="can_send_stickers" onchange="toggleSetting('can_send_stickers', this.checked)">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="setting-description">Отправка стикеров и анимированных GIF</div>
                </div>
            </div>

            <!-- Управление группой -->
            <div class="section">
                <div class="section-title">
                    <span class="emoji">👥</span>
                    Управление группой
                </div>
                
                <div class="setting">
                    <div class="setting-header">
                        <div class="setting-title">
                            <span class="emoji">✏️</span>
                            Изменение информации
                        </div>
                        <label class="switch">
                            <input type="checkbox" id="can_change_info" onchange="toggleSetting('can_change_info', this.checked)">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="setting-description">Изменение названия, фото и описания группы</div>
                </div>

                <div class="setting">
                    <div class="setting-header">
                        <div class="setting-title">
                            <span class="emoji">👥</span>
                            Приглашение пользователей
                        </div>
                        <label class="switch">
                            <input type="checkbox" id="can_invite_users" onchange="toggleSetting('can_invite_users', this.checked)">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="setting-description">Участники могут приглашать новых пользователей</div>
                </div>

                <div class="setting">
                    <div class="setting-header">
                        <div class="setting-title">
                            <span class="emoji">📌</span>
                            Закрепление сообщений
                        </div>
                        <label class="switch">
                            <input type="checkbox" id="can_pin_messages" onchange="toggleSetting('can_pin_messages', this.checked)">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="setting-description">Участники могут закреплять сообщения</div>
                </div>
            </div>
        </div>

        <div id="access-denied" class="access-denied" style="display: none;">
            <h2>🚫 Доступ запрещен</h2>
            <p>Этот интерфейс работает только через Telegram</p>
            <p>Откройте через бота командой /settings</p>
        </div>

        <script>
            let tg = window.Telegram.WebApp;
            
            // Проверяем, открыто ли в Telegram WebApp
            function checkTelegramEnvironment() {{
                if (typeof tg === 'undefined' || !tg.initData) {{
                    document.getElementById('app-content').style.display = 'none';
                    document.getElementById('access-denied').style.display = 'block';
                    return false;
                }}
                
                // Расширяем на весь экран
                tg.expand();
                tg.ready();
                return true;
            }}
            
            // Инициализация
            if (checkTelegramEnvironment()) {{
                loadSettings();
                showStatus('🎯 Donk Chat Settings загружены!', 'info');
            }}

            function loadSettings() {{
                // Используем WebApp Data для загрузки настроек
                const data = {{
                    action: 'get_settings',
                    chat_id: {GROUP_CHAT_ID},
                    timestamp: Date.now()
                }};
                
                tg.sendData(JSON.stringify(data));
            }}

            function updateUI(settings) {{
                // Основные разрешения
                document.getElementById('can_send_messages').checked = settings.can_send_messages;
                document.getElementById('can_send_polls').checked = settings.can_send_polls;
                
                // Медиафайлы
                document.getElementById('can_send_media_messages').checked = settings.can_send_media_messages;
                document.getElementById('can_send_photos').checked = settings.can_send_photos;
                document.getElementById('can_send_videos').checked = settings.can_send_videos;
                document.getElementById('can_send_video_notes').checked = settings.can_send_video_notes;
                document.getElementById('can_send_voice_notes').checked = settings.can_send_voice_notes;
                document.getElementById('can_send_stickers').checked = settings.can_send_stickers;
                
                // Управление группой
                document.getElementById('can_change_info').checked = settings.can_change_info;
                document.getElementById('can_invite_users').checked = settings.can_invite_users;
                document.getElementById('can_pin_messages').checked = settings.can_pin_messages;
            }}

            function toggleSetting(setting, value) {{
                showStatus('🔄 Изменение настроек...', 'info');
                
                const data = {{
                    action: 'update_setting',
                    setting: setting,
                    value: value,
                    chat_id: {GROUP_CHAT_ID},
                    timestamp: Date.now()
                }};
                
                tg.sendData(JSON.stringify(data));
            }}

            function syncSettings() {{
                showStatus('🔄 Синхронизация с Telegram...', 'info');
                const data = {{
                    action: 'sync_settings',
                    chat_id: {GROUP_CHAT_ID},
                    timestamp: Date.now()
                }};
                tg.sendData(JSON.stringify(data));
            }}

            function applyAllSettings() {{
                showStatus('🎯 Применение всех настроек...', 'info');
                const data = {{
                    action: 'apply_settings',
                    chat_id: {GROUP_CHAT_ID},
                    timestamp: Date.now()
                }};
                tg.sendData(JSON.stringify(data));
            }}

            function testDisableMessages() {{
                showStatus('🧪 Тестирование: отключение сообщений...', 'warning');
                const data = {{
                    action: 'update_setting',
                    setting: 'can_send_messages',
                    value: false,
                    chat_id: {GROUP_CHAT_ID},
                    timestamp: Date.now()
                }};
                tg.sendData(JSON.stringify(data));
            }}

            function showStatus(message, type) {{
                const status = document.getElementById('status');
                status.textContent = message;
                status.className = 'status ' + type;
                status.style.display = 'block';
                
                setTimeout(() => {{
                    status.style.display = 'none';
                }}, 4000);
            }}

            // Обработчик сообщений от бота
            tg.onEvent('viewportChanged', function() {{
                tg.expand();
            }});
        </script>
    </body>
    </html>
    """
    return html

# Webhook для обработки данных от WebApp
@app.route('/webhook', methods=['POST'])
def webhook():
    if not BOT_TOKEN:
        return 'OK'
    
    try:
        data = request.get_json()
        print(f"📨 Received: {data}")
        
        # Обрабатываем сообщения от бота
        if 'message' in data:
            message = data['message']
            
            # Проверяем доступ
            if message['from']['id'] != ALLOWED_USER_ID:
                telegram_api('sendMessage', {
                    'chat_id': message['chat']['id'],
                    'text': '🚫 Access denied'
                })
                return 'OK'
            
            # Обрабатываем команды
            if 'text' in message:
                text = message['text']
                
                if text == '/start' or text == '/settings':
                    webapp_url = f"https://{request.host}/settings"
                    telegram_api('sendMessage', {
                        'chat_id': message['chat']['id'],
                        'text': '🎛️ Donk Chat Settings',
                        'reply_markup': {
                            'inline_keyboard': [[{
                                'text': '⚙️ Open Settings',
                                'web_app': {'url': webapp_url}
                            }]]
                        }
                    })
        
        # Обрабатываем данные от WebApp
        elif 'web_app_data' in data:
            web_app_data = data['web_app_data']
            user_id = data['from']['id']
            
            if user_id != ALLOWED_USER_ID:
                return 'OK'
            
            try:
                app_data = json.loads(web_app_data['data'])
                action = app_data.get('action')
                chat_id = app_data.get('chat_id', GROUP_CHAT_ID)
                
                print(f"🔄 WebApp Action: {action}")
                
                if action == 'get_settings':
                    # Отправляем текущие настройки
                    telegram_api('sendMessage', {
                        'chat_id': user_id,
                        'text': f'📊 Current Settings:\\n\\n{json.dumps(current_settings, indent=2)}'
                    })
                    
                elif action == 'update_setting':
                    setting = app_data.get('setting')
                    value = app_data.get('value')
                    
                    if setting in current_settings:
                        result = update_setting(setting, value)
                        status = '✅ Успешно' if result.get('ok') else '❌ Ошибка'
                        telegram_api('sendMessage', {
                            'chat_id': user_id,
                            'text': f'{status}: {setting} = {value}'
                        })
                        
                elif action == 'sync_settings':
                    success = sync_settings()
                    status = '✅ Синхронизировано' if success else '❌ Ошибка синхронизации'
                    telegram_api('sendMessage', {
                        'chat_id': user_id,
                        'text': status
                    })
                    
                elif action == 'apply_settings':
                    result = apply_settings()
                    status = '✅ Настройки применены' if result.get('ok') else '❌ Ошибка применения'
                    telegram_api('sendMessage', {
                        'chat_id': user_id,
                        'text': status
                    })
                    
            except Exception as e:
                print(f"❌ WebApp data error: {e}")
                telegram_api('sendMessage', {
                    'chat_id': user_id,
                    'text': f'❌ Ошибка: {str(e)}'
                })
    
    except Exception as e:
        print(f"❌ Webhook error: {e}")
    
    return 'OK'

if __name__ == '__main__':
    print("🚀 Starting Telegram-Only Settings Manager")
    print(f"🎯 Group: {GROUP_CHAT_ID}")
    print("🔒 RESTRICTED: Only works through Telegram WebApp")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
