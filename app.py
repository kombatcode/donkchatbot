from flask import Flask, request, jsonify, Response
import telebot
import os
import json
import time

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ALLOWED_USER_ID = 1444832263
GROUP_CHAT_ID = -1001721934457

if BOT_TOKEN:
    bot = telebot.TeleBot(BOT_TOKEN)
else:
    bot = None

# Кэш для хранения последних настроек
settings_cache = {}
CACHE_TIMEOUT = 30

def get_current_group_settings(chat_id):
    """Получает актуальные настройки группы из Telegram"""
    global settings_cache
    
    cache_key = f"settings_{chat_id}"
    if cache_key in settings_cache:
        cached_data, timestamp = settings_cache[cache_key]
        if time.time() - timestamp < CACHE_TIMEOUT:
            return cached_data
    
    try:
        print(f"🔍 Getting fresh settings for chat: {chat_id}")
        
        chat = bot.get_chat(chat_id)
        print(f"📋 Chat title: {chat.title}")
        
        permissions = chat.permissions
        print(f"🔓 Permissions object: {permissions}")
        
        if permissions is None:
            print("⚠️ Permissions are None - using defaults")
            settings = {
                'can_send_messages': True,
                'can_send_media_messages': True,
                'can_send_polls': True,
                'can_change_info': False,
                'can_invite_users': True,
                'can_pin_messages': False
            }
        else:
            settings = {
                'can_send_messages': getattr(permissions, 'can_send_messages', True),
                'can_send_media_messages': getattr(permissions, 'can_send_media_messages', True),
                'can_send_polls': getattr(permissions, 'can_send_polls', True),
                'can_change_info': getattr(permissions, 'can_change_info', False),
                'can_invite_users': getattr(permissions, 'can_invite_users', True),
                'can_pin_messages': getattr(permissions, 'can_pin_messages', False)
            }
        
        print(f"✅ Current settings: {settings}")
        settings_cache[cache_key] = (settings, time.time())
        return settings
        
    except Exception as e:
        print(f"❌ Error getting settings: {str(e)}")
        return None

def check_bot_permissions(chat_id):
    """Проверяет права бота в группе"""
    try:
        bot_member = bot.get_chat_member(chat_id, bot.get_me().id)
        
        if bot_member.status == 'administrator':
            rights_info = {
                'can_manage_chat': getattr(bot_member, 'can_manage_chat', False),
                'can_change_info': getattr(bot_member, 'can_change_info', False),
                'can_delete_messages': getattr(bot_member, 'can_delete_messages', False),
                'can_restrict_members': getattr(bot_member, 'can_restrict_members', False),
                'can_invite_users': getattr(bot_member, 'can_invite_users', False),
                'can_pin_messages': getattr(bot_member, 'can_pin_messages', False),
            }
            print(f"🔐 Bot rights: {rights_info}")
            return rights_info
        return None
    except Exception as e:
        print(f"❌ Error checking bot permissions: {e}")
        return None

def update_group_permissions(chat_id, new_settings):
    """Изменяет настройки группы с детальной диагностикой"""
    try:
        from telebot.types import ChatPermissions
        
        print(f"🔄 ATTEMPTING TO UPDATE SETTINGS:")
        print(f"   Chat ID: {chat_id}")
        print(f"   New settings: {new_settings}")
        
        # Получаем текущие настройки ДО изменения
        old_settings = get_current_group_settings(chat_id)
        print(f"   Old settings: {old_settings}")
        
        permissions = ChatPermissions(
            can_send_messages=new_settings.get('can_send_messages', True),
            can_send_media_messages=new_settings.get('can_send_media_messages', True),
            can_send_polls=new_settings.get('can_send_polls', True),
            can_change_info=new_settings.get('can_change_info', False),
            can_invite_users=new_settings.get('can_invite_users', True),
            can_pin_messages=new_settings.get('can_pin_messages', False)
        )
        
        print(f"   Permissions object: {permissions}")
        
        # Пытаемся установить настройки
        result = bot.set_chat_permissions(chat_id, permissions)
        print(f"   set_chat_permissions result: {result}")
        
        # Очищаем кэш
        cache_key = f"settings_{chat_id}"
        if cache_key in settings_cache:
            del settings_cache[cache_key]
        
        # Ждем и проверяем
        print("   ⏳ Waiting for changes to apply...")
        time.sleep(3)
        
        verified_settings = get_current_group_settings(chat_id)
        print(f"   Verified settings after update: {verified_settings}")
        
        if verified_settings:
            # Проверяем, что настройки изменились
            changes_applied = all(
                verified_settings.get(key) == new_settings.get(key, True) 
                for key in new_settings.keys()
            )
            
            if changes_applied:
                print("   ✅ SUCCESS: Settings applied correctly!")
                return True, verified_settings
            else:
                print("   ⚠️ WARNING: Settings were set but not verified")
                print(f"   Requested: {new_settings}")
                print(f"   Actual: {verified_settings}")
                return False, verified_settings
        else:
            print("   ❌ ERROR: Could not verify settings after update")
            return False, None
        
    except Exception as e:
        print(f"❌ ERROR in update_group_permissions: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        
        # Очищаем кэш при ошибке
        cache_key = f"settings_{chat_id}"
        if cache_key in settings_cache:
            del settings_cache[cache_key]
        return False, None

def get_mini_app_html():
    """Генерирует HTML с текущими настройками группы"""
    current_settings = {}
    bot_permissions = {}
    error_message = ""
    
    if BOT_TOKEN:
        bot_permissions = check_bot_permissions(GROUP_CHAT_ID)
        
        if bot_permissions and bot_permissions.get('can_manage_chat'):
            current_settings = get_current_group_settings(GROUP_CHAT_ID)
            if not current_settings:
                error_message = "❌ Не удалось загрузить текущие настройки"
        else:
            error_message = "❌ Бот не имеет прав 'Управление настройками группы'"
    
    settings = current_settings if current_settings else {
        'can_send_messages': True,
        'can_send_media_messages': True, 
        'can_send_polls': True,
        'can_change_info': False,
        'can_invite_users': True,
        'can_pin_messages': False
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
    </style>
</head>
<body>
    <div class="container">
        <div class="permissions-info">
            <h3>⚙️ Управление настройками Donk Chat</h3>
            <p><strong>ID группы:</strong> {GROUP_CHAT_ID}</p>
            {"<p class='error'>" + error_message + "</p>" if error_message else 
             "<p class='success'>✅ Бот имеет права управления</p>"}
            <button class="refresh-btn" onclick="loadCurrentSettings()">🔄 Обновить настройки</button>
        </div>

        <div class="debug-info">
            🔍 Режим отладки включен. Проверяйте логи в Render.
        </div>
        
        <h3>📋 Разрешения участников:</h3>
        
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
            <p>Фото, видео, музыка, файлы, голосовые сообщения</p>
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

        function updateSetting(setting, value) {{
            const settings = {{
                can_send_messages: document.getElementById('can_send_messages').checked,
                can_send_media_messages: document.getElementById('can_send_media_messages').checked,
                can_send_polls: document.getElementById('can_send_polls').checked,
                can_change_info: document.getElementById('can_change_info').checked,
                can_invite_users: document.getElementById('can_invite_users').checked,
                can_pin_messages: document.getElementById('can_pin_messages').checked
            }};
            
            console.log('📤 Sending settings to bot:', settings);
            
            tg.sendData(JSON.stringify({{
                action: 'update_group_settings',
                settings: settings,
                chat_id: {GROUP_CHAT_ID},
                timestamp: Date.now()
            }}));
            
            showStatus('✅ Настройки отправлены...', 'success');
        }}

        document.addEventListener('DOMContentLoaded', function() {{
            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(checkbox => {{
                checkbox.addEventListener('change', function() {{
                    updateSetting(this.id, this.checked);
                }});
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
            showStatus('👋 Готов к работе! Измените настройки', 'success');
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

@app.route('/webhook', methods=['POST'])
def webhook():
    if not BOT_TOKEN:
        return 'Bot token not set', 400
        
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'Error', 403

def check_user_access(user_id):
    return user_id == ALLOWED_USER_ID

# Обработчики бота
if BOT_TOKEN:
    @bot.message_handler(commands=['start', 'settings'])
    def handle_settings(message):
        if not check_user_access(message.from_user.id):
            bot.send_message(message.chat.id, "🚫 Access Denied")
            return
        
        from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
        markup = InlineKeyboardMarkup()
        web_app_button = InlineKeyboardButton(
            "⚙️ Настройки группы", 
            web_app=telebot.types.WebAppInfo(url="https://donkchatbot.onrender.com/group_settings.html")
        )
        markup.add(web_app_button)
        
        bot.send_message(message.chat.id, "🎛️ Панель управления настройками Donk Chat", reply_markup=markup)

    @bot.message_handler(commands=['test_permissions'])
    def test_permissions_command(message):
        """Тестовая команда для проверки изменения настроек"""
        try:
            # Пробуем выключить отправку сообщений
            from telebot.types import ChatPermissions
            
            test_permissions = ChatPermissions(
                can_send_messages=False,  # ВЫКЛЮЧАЕМ сообщения
                can_send_media_messages=True,
                can_send_polls=True,
                can_change_info=False,
                can_invite_users=True,
                can_pin_messages=False
            )
            
            print(f"🧪 TEST: Setting permissions to {test_permissions}")
            result = bot.set_chat_permissions(GROUP_CHAT_ID, test_permissions)
            print(f"🧪 TEST: set_chat_permissions result: {result}")
            
            bot.send_message(message.chat.id, "🧪 Тестовые настройки применены. Проверьте чат!")
            
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Тестовая ошибка: {str(e)}")

    @bot.message_handler(content_types=['web_app_data'])
    def handle_web_app_data(message):
        if not check_user_access(message.from_user.id):
            bot.send_message(message.chat.id, "🚫 Access Denied")
            return
            
        try:
            data = json.loads(message.web_app_data.data)
            print(f"📨 Received web app data: {data}")
            
            if data.get('action') == 'update_group_settings':
                settings = data.get('settings', {})
                chat_id = data.get('chat_id', GROUP_CHAT_ID)
                
                print(f"🔄 Processing settings update: {settings}")
                
                # Проверяем права
                bot_permissions = check_bot_permissions(chat_id)
                if not bot_permissions or not bot_permissions.get('can_manage_chat'):
                    bot.send_message(message.chat.id, "❌ У бота нет прав 'Управление настройками группы'")
                    return
                
                # Изменяем настройки
                success, verified_settings = update_group_permissions(chat_id, settings)
                
                if success:
                    settings_text = "✅ Настройки Donk Chat обновлены!\n\n"
                    setting_names = {
                        'can_send_messages': '📝 Сообщения',
                        'can_send_media_messages': '🖼️ Медиа',
                        'can_send_polls': '📊 Опроcы',
                        'can_change_info': '✏️ Изменение инфо',
                        'can_invite_users': '👥 Приглашения',
                        'can_pin_messages': '📌 Закрепление'
                    }
                    
                    for setting, value in verified_settings.items():
                        setting_name = setting_names.get(setting, setting)
                        status = "✅ ВКЛ" if value else "❌ ВЫКЛ"
                        settings_text += f"{setting_name}: {status}\n"
                    
                    bot.send_message(message.chat.id, settings_text)
                else:
                    bot.send_message(message.chat.id, 
                        "❌ Не удалось применить настройки.\n"
                        "Проверьте логи в Render для деталей."
                    )
                
        except Exception as e:
            print(f"❌ Web app error: {e}")
            bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")

if __name__ == '__main__':
    if BOT_TOKEN:
        try:
            bot.remove_webhook()
            bot.set_webhook(url="https://donkchatbot.onrender.com/webhook")
            print("✅ Webhook set successfully")
            print(f"🎯 Target chat: {GROUP_CHAT_ID}")
        except Exception as e:
            print(f"⚠️ Webhook setup failed: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
