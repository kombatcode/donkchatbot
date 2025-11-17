from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ALLOWED_USER_IDS = [1444832263, 848736128]
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
    result = telegram_api('setChatPermissions', data)
    print(f"🎯 Apply settings result: {result}")
    return result

def update_setting(setting_name, value):
    """Обновляет настройку и применяет её"""
    print(f"🔄 Setting {setting_name} to {value}")
    current_settings[setting_name] = value
    return apply_settings()

def get_current_settings():
    """Получает текущие настройки из Telegram"""
    result = telegram_api('getChat', {'chat_id': GROUP_CHAT_ID})
    if result.get('ok'):
        permissions = result['result'].get('permissions', {})
        print(f"📋 Current Telegram settings: {permissions}")
        return permissions
    print("❌ Failed to get current settings from Telegram")
    return {}

def sync_settings():
    """Синхронизирует настройки с Telegram"""
    global current_settings
    telegram_settings = get_current_settings()
    if telegram_settings:
        # Обновляем только существующие ключи
        for key in list(current_settings.keys()):
            if key in telegram_settings:
                current_settings[key] = telegram_settings[key]
        print(f"🔄 Synced settings: {current_settings}")
        return True
    return False

# Загружаем настройки при старте
print("🚀 Starting application...")
sync_settings()

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Group Settings</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
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
            a {
                color: white;
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎛️ Donk Chat Settings</h1>
            <p>Этот интерфейс работает только через Telegram</p>
            <p>Откройте через бота командой /settings</p>
            <p><a href="/settings">Перейти к настройкам</a></p>
        </div>
    </body>
    </html>
    """

@app.route('/settings')
def settings_page():
    """Главная страница настроек"""
    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Настройки приложения</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            }}

            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 10px;
                display: flex;
                justify-content: center;
                align-items: flex-start;
            }}

            .container {{
                width: 100%;
                max-width: 500px;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                overflow: hidden;
                margin: 10px 0;
            }}

            .header {{
                background: linear-gradient(90deg, #4f6df5, #3a56e8);
                color: white;
                padding: 20px;
                text-align: center;
            }}

            .header h1 {{
                font-size: 22px;
                font-weight: 600;
                margin-bottom: 5px;
            }}

            .header p {{
                opacity: 0.9;
                font-size: 14px;
            }}

            .settings-container {{
                padding: 20px 15px;
            }}

            .section {{
                margin-bottom: 25px;
            }}

            .section-title {{
                font-size: 16px;
                font-weight: 600;
                color: #333;
                margin-bottom: 15px;
                padding-bottom: 8px;
                border-bottom: 2px solid #4f6df5;
                display: flex;
                align-items: center;
                gap: 8px;
            }}

            .setting-item {{
                margin-bottom: 15px;
                padding: 12px;
                background: #f8f9fa;
                border-radius: 10px;
                transition: all 0.3s ease;
            }}

            .setting-item:hover {{
                transform: translateY(-1px);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}

            .setting-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 6px;
            }}

            .setting-title {{
                font-weight: 600;
                color: #333;
                font-size: 14px;
                display: flex;
                align-items: center;
                gap: 8px;
            }}

            .setting-value {{
                font-weight: 600;
                color: #4f6df5;
                font-size: 13px;
            }}

            .setting-description {{
                color: #666;
                font-size: 12px;
                margin-top: 4px;
                line-height: 1.3;
            }}

            .slider-container {{
                position: relative;
                height: 28px;
                display: flex;
                align-items: center;
            }}

            .buttons {{
                display: flex;
                gap: 10px;
                margin-top: 25px;
                flex-wrap: wrap;
            }}

            .btn {{
                flex: 1;
                min-width: 140px;
                padding: 12px 15px;
                border: none;
                border-radius: 10px;
                font-weight: 600;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.3s;
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 6px;
            }}

            .btn-primary {{
                background: linear-gradient(90deg, #4f6df5, #3a56e8);
                color: white;
                box-shadow: 0 3px 8px rgba(79, 109, 245, 0.3);
            }}

            .btn-primary:hover {{
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(79, 109, 245, 0.4);
            }}

            .btn-secondary {{
                background: #f5f5f5;
                color: #666;
            }}

            .btn-secondary:hover {{
                background: #e9e9e9;
            }}

            .status {{
                text-align: center;
                margin-top: 15px;
                padding: 10px;
                border-radius: 8px;
                font-size: 13px;
                display: none;
            }}

            .status.success {{
                background: #e8f5e9;
                color: #2e7d32;
                display: block;
            }}

            .status.error {{
                background: #ffebee;
                color: #c62828;
                display: block;
            }}

            .status.info {{
                background: #e3f2fd;
                color: #1565c0;
                display: block;
            }}

            .icon {{
                width: 16px;
                height: 16px;
            }}

            /* Switch styles */
            .switch {{
                position: relative;
                display: inline-block;
                width: 50px;
                height: 28px;
            }}

            .switch input {{
                opacity: 0;
                width: 0;
                height: 0;
            }}

            .switch-slider {{
                position: absolute;
                cursor: pointer;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: #ccc;
                transition: .4s;
                border-radius: 28px;
            }}

            .switch-slider:before {{
                position: absolute;
                content: "";
                height: 22px;
                width: 22px;
                left: 3px;
                bottom: 3px;
                background-color: white;
                transition: .4s;
                border-radius: 50%;
            }}

            input:checked + .switch-slider {{
                background-color: #4f6df5;
            }}

            input:checked + .switch-slider:before {{
                transform: translateX(22px);
            }}

            .emoji {{
                font-size: 16px;
            }}

            @media (max-width: 480px) {{
                .container {{
                    margin: 5px;
                    border-radius: 15px;
                }}
                
                .header {{
                    padding: 15px;
                }}
                
                .settings-container {{
                    padding: 15px 10px;
                }}
                
                .btn {{
                    min-width: 120px;
                    font-size: 13px;
                    padding: 10px 12px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Настройки группы</h1>
                <p>Управление разрешениями чата</p>
            </div>
            
            <div class="settings-container">
                <!-- Основные разрешения -->
                <div class="section">
                    <div class="section-title">
                        <span class="emoji">💬</span>
                        Основные разрешения
                    </div>
                    
                    <div class="setting-item">
                        <div class="setting-header">
                            <div class="setting-title">
                                <span class="emoji">💬</span>
                                Отправка сообщений
                            </div>
                            <span class="setting-value" id="messages_status">ON</span>
                        </div>
                        <div class="slider-container">
                            <label class="switch">
                                <input type="checkbox" id="can_send_messages" onchange="toggleSetting('can_send_messages', this.checked, 'messages_status')">
                                <span class="switch-slider"></span>
                            </label>
                        </div>
                        <div class="setting-description">Участники могут отправлять текстовые сообщения</div>
                    </div>

                    <div class="setting-item">
                        <div class="setting-header">
                            <div class="setting-title">
                                <span class="emoji">📊</span>
                                Создание опросов
                            </div>
                            <span class="setting-value" id="polls_status">ON</span>
                        </div>
                        <div class="slider-container">
                            <label class="switch">
                                <input type="checkbox" id="can_send_polls" onchange="toggleSetting('can_send_polls', this.checked, 'polls_status')">
                                <span class="switch-slider"></span>
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

                    <div class="setting-item">
                        <div class="setting-header">
                            <div class="setting-title">
                                <span class="emoji">🖼️</span>
                                Все медиафайлы
                            </div>
                            <span class="setting-value" id="media_status">ON</span>
                        </div>
                        <div class="slider-container">
                            <label class="switch">
                                <input type="checkbox" id="can_send_media_messages" onchange="toggleSetting('can_send_media_messages', this.checked, 'media_status')">
                                <span class="switch-slider"></span>
                            </label>
                        </div>
                        <div class="setting-description">Все типы медиафайлов (общая настройка)</div>
                    </div>

                    <div class="setting-item">
                        <div class="setting-header">
                            <div class="setting-title">
                                <span class="emoji">📸</span>
                                Фотографии
                            </div>
                            <span class="setting-value" id="photos_status">ON</span>
                        </div>
                        <div class="slider-container">
                            <label class="switch">
                                <input type="checkbox" id="can_send_photos" onchange="toggleSetting('can_send_photos', this.checked, 'photos_status')">
                                <span class="switch-slider"></span>
                            </label>
                        </div>
                        <div class="setting-description">Отправка изображений и фотографий</div>
                    </div>

                    <div class="setting-item">
                        <div class="setting-header">
                            <div class="setting-title">
                                <span class="emoji">🎥</span>
                                Видео
                            </div>
                            <span class="setting-value" id="videos_status">ON</span>
                        </div>
                        <div class="slider-container">
                            <label class="switch">
                                <input type="checkbox" id="can_send_videos" onchange="toggleSetting('can_send_videos', this.checked, 'videos_status')">
                                <span class="switch-slider"></span>
                            </label>
                        </div>
                        <div class="setting-description">Отправка видеофайлов</div>
                    </div>

                    <div class="setting-item">
                        <div class="setting-header">
                            <div class="setting-title">
                                <span class="emoji">📹</span>
                                Видеосообщения
                            </div>
                            <span class="setting-value" id="video_notes_status">ON</span>
                        </div>
                        <div class="slider-container">
                            <label class="switch">
                                <input type="checkbox" id="can_send_video_notes" onchange="toggleSetting('can_send_video_notes', this.checked, 'video_notes_status')">
                                <span class="switch-slider"></span>
                            </label>
                        </div>
                        <div class="setting-description">Круглые видео-сообщения (video notes)</div>
                    </div>

                    <div class="setting-item">
                        <div class="setting-header">
                            <div class="setting-title">
                                <span class="emoji">🎤</span>
                                Голосовые сообщения
                            </div>
                            <span class="setting-value" id="voice_notes_status">ON</span>
                        </div>
                        <div class="slider-container">
                            <label class="switch">
                                <input type="checkbox" id="can_send_voice_notes" onchange="toggleSetting('can_send_voice_notes', this.checked, 'voice_notes_status')">
                                <span class="switch-slider"></span>
                            </label>
                        </div>
                        <div class="setting-description">Отправка голосовых сообщений (войсы)</div>
                    </div>

                    <div class="setting-item">
                        <div class="setting-header">
                            <div class="setting-title">
                                <span class="emoji">🩷</span>
                                Стикеры и GIF
                            </div>
                            <span class="setting-value" id="stickers_status">ON</span>
                        </div>
                        <div class="slider-container">
                            <label class="switch">
                                <input type="checkbox" id="can_send_stickers" onchange="toggleSetting('can_send_stickers', this.checked, 'stickers_status')">
                                <span class="switch-slider"></span>
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

                    <div class="setting-item">
                        <div class="setting-header">
                            <div class="setting-title">
                                <span class="emoji">✏️</span>
                                Изменение информации
                            </div>
                            <span class="setting-value" id="info_status">OFF</span>
                        </div>
                        <div class="slider-container">
                            <label class="switch">
                                <input type="checkbox" id="can_change_info" onchange="toggleSetting('can_change_info', this.checked, 'info_status')">
                                <span class="switch-slider"></span>
                            </label>
                        </div>
                        <div class="setting-description">Изменение названия, фото и описания группы</div>
                    </div>

                    <div class="setting-item">
                        <div class="setting-header">
                            <div class="setting-title">
                                <span class="emoji">👥</span>
                                Приглашение пользователей
                            </div>
                            <span class="setting-value" id="invite_status">ON</span>
                        </div>
                        <div class="slider-container">
                            <label class="switch">
                                <input type="checkbox" id="can_invite_users" onchange="toggleSetting('can_invite_users', this.checked, 'invite_status')">
                                <span class="switch-slider"></span>
                            </label>
                        </div>
                        <div class="setting-description">Участники могут приглашать новых пользователей</div>
                    </div>

                    <div class="setting-item">
                        <div class="setting-header">
                            <div class="setting-title">
                                <span class="emoji">📌</span>
                                Закрепление сообщений
                            </div>
                            <span class="setting-value" id="pin_status">OFF</span>
                        </div>
                        <div class="slider-container">
                            <label class="switch">
                                <input type="checkbox" id="can_pin_messages" onchange="toggleSetting('can_pin_messages', this.checked, 'pin_status')">
                                <span class="switch-slider"></span>
                            </label>
                        </div>
                        <div class="setting-description">Участники могут закреплять сообщения</div>
                    </div>
                </div>
                
                <div class="buttons">
                    <button class="btn btn-secondary" onclick="syncSettings()">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M4 4V5H4.58152M19.9381 11C19.446 7.05369 16.0796 4 12 4C8.64262 4 5.76829 6.06817 4.58152 9M4.58152 9H4M4.58152 9H6M20 20V19H19.4185M19.4185 19C18.2317 21.9318 15.3574 24 12 24C7.92038 24 4.55399 20.9463 4.06189 17M19.4185 19H18M19.4185 19H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        Синхронизировать
                    </button>
                    <button class="btn btn-primary" onclick="applyAllSettings()">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M5 13L9 17L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        Применить все
                    </button>
                </div>

                <div id="status" class="status"></div>
            </div>
        </div>

        <script>
            // Текущие настройки
            let currentSettings = {json.dumps(current_settings)};

            // Загружаем настройки при загрузке страницы
            document.addEventListener('DOMContentLoaded', function() {{
                console.log('Initial settings:', currentSettings);
                updateUI(currentSettings);
                showStatus('✅ Настройки загружены', 'success');
            }});

            function updateUI(settings) {{
                console.log('Updating UI with settings:', settings);
                
                // Основные разрешения
                document.getElementById('can_send_messages').checked = settings.can_send_messages || false;
                document.getElementById('can_send_polls').checked = settings.can_send_polls || false;
                
                // Медиафайлы
                document.getElementById('can_send_media_messages').checked = settings.can_send_media_messages || false;
                document.getElementById('can_send_photos').checked = settings.can_send_photos || false;
                document.getElementById('can_send_videos').checked = settings.can_send_videos || false;
                document.getElementById('can_send_video_notes').checked = settings.can_send_video_notes || false;
                document.getElementById('can_send_voice_notes').checked = settings.can_send_voice_notes || false;
                document.getElementById('can_send_stickers').checked = settings.can_send_stickers || false;
                
                // Управление группой
                document.getElementById('can_change_info').checked = settings.can_change_info || false;
                document.getElementById('can_invite_users').checked = settings.can_invite_users || false;
                document.getElementById('can_pin_messages').checked = settings.can_pin_messages || false;
                
                // Обновляем статусы
                document.getElementById('messages_status').textContent = settings.can_send_messages ? 'ON' : 'OFF';
                document.getElementById('polls_status').textContent = settings.can_send_polls ? 'ON' : 'OFF';
                document.getElementById('media_status').textContent = settings.can_send_media_messages ? 'ON' : 'OFF';
                document.getElementById('photos_status').textContent = settings.can_send_photos ? 'ON' : 'OFF';
                document.getElementById('videos_status').textContent = settings.can_send_videos ? 'ON' : 'OFF';
                document.getElementById('video_notes_status').textContent = settings.can_send_video_notes ? 'ON' : 'OFF';
                document.getElementById('voice_notes_status').textContent = settings.can_send_voice_notes ? 'ON' : 'OFF';
                document.getElementById('stickers_status').textContent = settings.can_send_stickers ? 'ON' : 'OFF';
                document.getElementById('info_status').textContent = settings.can_change_info ? 'ON' : 'OFF';
                document.getElementById('invite_status').textContent = settings.can_invite_users ? 'ON' : 'OFF';
                document.getElementById('pin_status').textContent = settings.can_pin_messages ? 'ON' : 'OFF';
            }}

            function toggleSetting(setting, value, statusElement) {{
                console.log('Toggling setting:', setting, 'to:', value);
                showStatus('🔄 Изменение настроек...', 'info');
                
                fetch('/api/update', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        setting: setting,
                        value: value
                    }})
                }})
                .then(response => {{
                    if (!response.ok) {{
                        throw new Error('Network response was not ok: ' + response.status);
                    }}
                    return response.json();
                }})
                .then(result => {{
                    console.log('Update result:', result);
                    if (result.success) {{
                        currentSettings = result.settings;
                        updateUI(currentSettings);
                        showStatus('✅ Настройка применена!', 'success');
                    }} else {{
                        showStatus('❌ Ошибка: ' + result.error, 'error');
                        // Возвращаем переключатель в предыдущее состояние
                        document.getElementById(setting).checked = !value;
                        document.getElementById(statusElement).textContent = !value ? 'ON' : 'OFF';
                    }}
                }})
                .catch(error => {{
                    console.error('Error updating setting:', error);
                    showStatus('❌ Ошибка сети: ' + error.message, 'error');
                    // Возвращаем переключатель в предыдущее состояние
                    document.getElementById(setting).checked = !value;
                    document.getElementById(statusElement).textContent = !value ? 'ON' : 'OFF';
                }});
            }}

            function syncSettings() {{
                showStatus('🔄 Синхронизация с Telegram...', 'info');
                
                fetch('/api/sync')
                    .then(response => {{
                        if (!response.ok) {{
                            throw new Error('Network response was not ok: ' + response.status);
                        }}
                        return response.json();
                    }})
                    .then(result => {{
                        console.log('Sync result:', result);
                        if (result.success) {{
                            currentSettings = result.settings;
                            updateUI(currentSettings);
                            showStatus('✅ Настройки синхронизированы!', 'success');
                        }} else {{
                            showStatus('❌ Ошибка синхронизации: ' + result.message, 'error');
                        }}
                    }})
                    .catch(error => {{
                        console.error('Error syncing settings:', error);
                        showStatus('❌ Ошибка сети при синхронизации: ' + error.message, 'error');
                    }});
            }}

            function applyAllSettings() {{
                showStatus('🎯 Применение всех настроек...', 'info');
                
                fetch('/api/apply')
                    .then(response => {{
                        if (!response.ok) {{
                            throw new Error('Network response was not ok: ' + response.status);
                        }}
                        return response.json();
                    }})
                    .then(result => {{
                        console.log('Apply result:', result);
                        if (result.success) {{
                            showStatus('✅ Все настройки применены!', 'success');
                        }} else {{
                            showStatus('❌ Ошибка применения настроек: ' + result.message, 'error');
                        }}
                    }})
                    .catch(error => {{
                        console.error('Error applying settings:', error);
                        showStatus('❌ Ошибка сети: ' + error.message, 'error');
                    }});
            }}

            function showStatus(message, type) {{
                const status = document.getElementById('status');
                status.textContent = message;
                status.className = 'status ' + type;
                status.style.display = 'block';
                
                setTimeout(() => {{
                    status.style.display = 'none';
                }}, 3000);
            }}

            // Инициализация Telegram Web App
            if (typeof Telegram !== 'undefined' && Telegram.WebApp) {{
                Telegram.WebApp.ready();
                Telegram.WebApp.expand();
            }}
        </script>
    </body>
    </html>
    """

# API endpoints
@app.route('/api/settings')
def api_get_settings():
    """Возвращает текущие настройки"""
    print(f"📊 API: Getting current settings: {current_settings}")
    return jsonify(current_settings)

@app.route('/api/update', methods=['POST'])
def api_update_setting():
    """Обновляет одну настройку"""
    try:
        data = request.get_json()
        setting = data.get('setting')
        value = bool(data.get('value'))
        
        print(f"🔄 API: Updating {setting} to {value}")
        
        if setting not in current_settings:
            print(f"❌ API: Invalid setting: {setting}")
            return jsonify({'success': False, 'error': 'Invalid setting'})
        
        result = update_setting(setting, value)
        
        if result.get('ok'):
            print(f"✅ API: Successfully updated {setting}")
            return jsonify({
                'success': True, 
                'settings': current_settings,
                'message': f'{setting} set to {value}'
            })
        else:
            print(f"❌ API: Telegram API error for {setting}")
            return jsonify({
                'success': False, 
                'error': 'Telegram API error: ' + str(result.get('description', 'Unknown error')),
                'settings': current_settings
            })
            
    except Exception as e:
        print(f"❌ API: Exception: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/sync')
def api_sync_settings():
    """Синхронизирует настройки с Telegram"""
    try:
        print("🔄 API: Syncing settings with Telegram")
        success = sync_settings()
        return jsonify({
            'success': success,
            'settings': current_settings,
            'message': 'Settings synced' if success else 'Sync failed'
        })
    except Exception as e:
        print(f"❌ API: Sync exception: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/apply')
def api_apply_settings():
    """Применяет все текущие настройки"""
    try:
        print("🎯 API: Applying all settings")
        result = apply_settings()
        return jsonify({
            'success': result.get('ok', False),
            'settings': current_settings,
            'message': 'Settings applied' if result.get('ok') else 'Apply failed: ' + str(result.get('description', 'Unknown error'))
        })
    except Exception as e:
        print(f"❌ API: Apply exception: {e}")
        return jsonify({'success': False, 'error': str(e)})

# Webhook для обработки команд бота
@app.route('/webhook', methods=['POST'])
def bot_webhook():
    """Обработчик вебхука от Telegram"""
    if not BOT_TOKEN:
        return 'OK'
    
    try:
        data = request.get_json()
        print(f"🤖 Webhook received: {data}")
        
        # Обрабатываем сообщения
        if 'message' in data:
            message = data['message']
            user_id = message['from']['id']
            chat_id = message['chat']['id']
            
            # Проверяем доступ
            if user_id not in ALLOWED_USER_IDS:
                telegram_api('sendMessage', {
                    'chat_id': chat_id,
                    'text': '🚫 У вас нет доступа к настройкам группы'
                })
                return 'OK'
            
            # Обрабатываем команды
            if 'text' in message:
                text = message['text']
                
                if text == '/start' or text == '/settings':
                    webapp_url = f"https://{request.host}/settings"
                    
                    telegram_api('sendMessage', {
                        'chat_id': chat_id,
                        'text': '🎛️ *Donk Chat Settings*\n\nУправление настройками группы',
                        'parse_mode': 'Markdown',
                        'reply_markup': {
                            'inline_keyboard': [[
                                {
                                    'text': '⚙️ Открыть настройки',
                                    'web_app': {'url': webapp_url}
                                }
                            ]]
                        }
                    })
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
    
    return 'OK'

# Установка вебхука
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Установка вебхука для бота"""
    if not BOT_TOKEN:
        return 'BOT_TOKEN not set'
    
    webhook_url = f"https://{request.host}/webhook"
    result = telegram_api('setWebhook', {'url': webhook_url})
    
    return jsonify({
        'success': result.get('ok', False),
        'webhook_url': webhook_url,
        'result': result
    })

# Удаление вебхука
@app.route('/delete_webhook', methods=['GET'])
def delete_webhook():
    """Удаление вебхука"""
    if not BOT_TOKEN:
        return 'BOT_TOKEN not set'
    
    result = telegram_api('deleteWebhook', {})
    return jsonify({
        'success': result.get('ok', False),
        'result': result
    })

if __name__ == '__main__':
    print("🚀 Starting Group Settings Manager")
    print(f"🎯 Group: {GROUP_CHAT_ID}")
    print(f"👥 Allowed users: {ALLOWED_USER_IDS}")
    print(f"📊 Initial settings: {current_settings}")
    print(f"🔑 BOT_TOKEN: {'Set' if BOT_TOKEN else 'Not set!'}")
    
    # Автоматически устанавливаем вебхук при запуске
    if BOT_TOKEN:
        webhook_url = f"https://{os.environ.get('HOST', 'your-host.com
