from flask import Flask, request, jsonify, Response
import telebot
import os
import json
import time
import traceback

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
        permissions = chat.permissions
        
        if permissions is None:
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
        return bot_member.status == 'administrator'
    except Exception as e:
        print(f"❌ Error checking bot permissions: {e}")
        return False

# ОТДЕЛЬНЫЕ ФУНКЦИИ ДЛЯ КАЖДОГО ПЕРЕКЛЮЧАТЕЛЯ
def set_send_messages(chat_id, enabled):
    """Устанавливает разрешение на отправку сообщений"""
    try:
        from telebot.types import ChatPermissions
        
        # Получаем текущие настройки
        current = get_current_group_settings(chat_id) or {}
        
        permissions = ChatPermissions(
            can_send_messages=enabled,
            can_send_media_messages=current.get('can_send_media_messages', True),
            can_send_polls=current.get('can_send_polls', True),
            can_change_info=current.get('can_change_info', False),
            can_invite_users=current.get('can_invite_users', True),
            can_pin_messages=current.get('can_pin_messages', False)
        )
        
        result = bot.set_chat_permissions(chat_id, permissions)
        print(f"✅ Set send_messages to {enabled}: {result}")
        return True
    except Exception as e:
        print(f"❌ Error setting send_messages: {e}")
        return False

def set_send_media(chat_id, enabled):
    """Устанавливает разрешение на отправку медиа"""
    try:
        from telebot.types import ChatPermissions
        
        current = get_current_group_settings(chat_id) or {}
        
        permissions = ChatPermissions(
            can_send_messages=current.get('can_send_messages', True),
            can_send_media_messages=enabled,
            can_send_polls=current.get('can_send_polls', True),
            can_change_info=current.get('can_change_info', False),
            can_invite_users=current.get('can_invite_users', True),
            can_pin_messages=current.get('can_pin_messages', False)
        )
        
        result = bot.set_chat_permissions(chat_id, permissions)
        print(f"✅ Set send_media to {enabled}: {result}")
        return True
    except Exception as e:
        print(f"❌ Error setting send_media: {e}")
        return False

def set_send_polls(chat_id, enabled):
    """Устанавливает разрешение на создание опросов"""
    try:
        from telebot.types import ChatPermissions
        
        current = get_current_group_settings(chat_id) or {}
        
        permissions = ChatPermissions(
            can_send_messages=current.get('can_send_messages', True),
            can_send_media_messages=current.get('can_send_media_messages', True),
            can_send_polls=enabled,
            can_change_info=current.get('can_change_info', False),
            can_invite_users=current.get('can_invite_users', True),
            can_pin_messages=current.get('can_pin_messages', False)
        )
        
        result = bot.set_chat_permissions(chat_id, permissions)
        print(f"✅ Set send_polls to {enabled}: {result}")
        return True
    except Exception as e:
        print(f"❌ Error setting send_polls: {e}")
        return False

def set_change_info(chat_id, enabled):
    """Устанавливает разрешение на изменение информации"""
    try:
        from telebot.types import ChatPermissions
        
        current = get_current_group_settings(chat_id) or {}
        
        permissions = ChatPermissions(
            can_send_messages=current.get('can_send_messages', True),
            can_send_media_messages=current.get('can_send_media_messages', True),
            can_send_polls=current.get('can_send_polls', True),
            can_change_info=enabled,
            can_invite_users=current.get('can_invite_users', True),
            can_pin_messages=current.get('can_pin_messages', False)
        )
        
        result = bot.set_chat_permissions(chat_id, permissions)
        print(f"✅ Set change_info to {enabled}: {result}")
        return True
    except Exception as e:
        print(f"❌ Error setting change_info: {e}")
        return False

def set_invite_users(chat_id, enabled):
    """Устанавливает разрешение на приглашение пользователей"""
    try:
        from telebot.types import ChatPermissions
        
        current = get_current_group_settings(chat_id) or {}
        
        permissions = ChatPermissions(
            can_send_messages=current.get('can_send_messages', True),
            can_send_media_messages=current.get('can_send_media_messages', True),
            can_send_polls=current.get('can_send_polls', True),
            can_change_info=current.get('can_change_info', False),
            can_invite_users=enabled,
            can_pin_messages=current.get('can_pin_messages', False)
        )
        
        result = bot.set_chat_permissions(chat_id, permissions)
        print(f"✅ Set invite_users to {enabled}: {result}")
        return True
    except Exception as e:
        print(f"❌ Error setting invite_users: {e}")
        return False

def set_pin_messages(chat_id, enabled):
    """Устанавливает разрешение на закрепление сообщений"""
    try:
        from telebot.types import ChatPermissions
        
        current = get_current_group_settings(chat_id) or {}
        
        permissions = ChatPermissions(
            can_send_messages=current.get('can_send_messages', True),
            can_send_media_messages=current.get('can_send_media_messages', True),
            can_send_polls=current.get('can_send_polls', True),
            can_change_info=current.get('can_change_info', False),
            can_invite_users=current.get('can_invite_users', True),
            can_pin_messages=enabled
        )
        
        result = bot.set_chat_permissions(chat_id, permissions)
        print(f"✅ Set pin_messages to {enabled}: {result}")
        return True
    except Exception as e:
        print(f"❌ Error setting pin_messages: {e}")
        return False

# Функции для быстрого тестирования каждого параметра
def test_all_permissions():
    """Тестирует все разрешения по очереди"""
    tests = [
        ("💬 Сообщения", set_send_messages, False),
        ("🖼️ Медиа", set_send_media, False),
        ("📊 Опроcы", set_send_polls, False),
        ("✏️ Изменение инфо", set_change_info, True),
        ("👥 Приглашения", set_invite_users, True),
        ("📌 Закрепление", set_pin_messages, True)
    ]
    
    results = []
    for name, func, default_value in tests:
        try:
            success = func(GROUP_CHAT_ID, default_value)
            results.append(f"{name}: {'✅' if success else '❌'}")
            time.sleep(2)  # Ждем между запросами
        except Exception as e:
            results.append(f"{name}: ❌ ({str(e)})")
    
    return results

def get_mini_app_html():
    """Генерирует HTML с текущими настройками группы"""
    current_settings = {}
    bot_has_access = False
    
    if BOT_TOKEN:
        bot_has_access = check_bot_permissions(GROUP_CHAT_ID)
        if bot_has_access:
            current_settings = get_current_group_settings(GROUP_CHAT_ID)
    
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
        .section-title {{
            font-size: 18px;
            font-weight: 700;
            margin: 25px 0 15px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #007aff;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="permissions-info">
            <h3>⚙️ Управление настройками Donk Chat</h3>
            <p><strong>ID группы:</strong> {GROUP_CHAT_ID}</p>
            {"<p class='success'>✅ Бот имеет права управления</p>" if bot_has_access else "<p class='error'>❌ Бот не имеет прав</p>"}
            <button class="refresh-btn" onclick="loadCurrentSettings()">🔄 Обновить настройки</button>
        </div>

        <div class="debug-info">
            🎯 <strong>Индивидуальные функции</strong> - каждый ползунок работает отдельно
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

        function sendSettingUpdate(setting, value, name) {{
            console.log(`📤 Setting ${{setting}} to ${{value}}`);
            
            const data = {{
                action: 'update_single_setting',
                setting: setting,
                value: value,
                chat_id: {GROUP_CHAT_ID},
                timestamp: Date.now()
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

    @bot.message_handler(commands=['test_individual'])
    def test_individual_permissions(message):
        """Тестирует все разрешения по отдельности"""
        try:
            bot.send_message(message.chat.id, "🧪 Тестирую все разрешения...")
            
            results = test_all_permissions()
            result_text = "🧪 Результаты тестирования:\n\n" + "\n".join(results)
            
            bot.send_message(message.chat.id, result_text)
            
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка тестирования: {str(e)}")

    @bot.message_handler(content_types=['web_app_data'])
    def handle_web_app_data(message):
        if not check_user_access(message.from_user.id):
            bot.send_message(message.chat.id, "🚫 Access Denied")
            return
            
        try:
            data = json.loads(message.web_app_data.data)
            print(f"📨 Received data: {data}")
            
            if data.get('action') == 'update_single_setting':
                setting = data.get('setting')
                value = data.get('value')
                chat_id = data.get('chat_id', GROUP_CHAT_ID)
                
                print(f"🔄 Processing single setting: {setting} = {value}")
                
                # Проверяем права
                if not check_bot_permissions(chat_id):
                    bot.send_message(message.chat.id, "❌ У бота нет прав")
                    return
                
                # ВЫЗЫВАЕМ ОТДЕЛЬНУЮ ФУНКЦИЮ ДЛЯ КАЖДОЙ НАСТРОЙКИ
                success = False
                setting_names = {
                    'can_send_messages': ('💬 Сообщения', set_send_messages),
                    'can_send_media_messages': ('🖼️ Медиа', set_send_media),
                    'can_send_polls': ('📊 Опроcы', set_send_polls),
                    'can_change_info': ('✏️ Изменение инфо', set_change_info),
                    'can_invite_users': ('👥 Приглашения', set_invite_users),
                    'can_pin_messages': ('📌 Закрепление', set_pin_messages)
                }
                
                if setting in setting_names:
                    name, func = setting_names[setting]
                    success = func(chat_id, value)
                    
                    if success:
                        status = "включены" if value else "выключены"
                        bot.send_message(message.chat.id, f"✅ {name} {status}")
                    else:
                        bot.send_message(message.chat.id, f"❌ Не удалось изменить {name}")
                else:
                    bot.send_message(message.chat.id, f"❌ Неизвестная настройка: {setting}")
                
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
            print("🔧 INDIVIDUAL FUNCTIONS MODE - каждый ползунок работает отдельно")
        except Exception as e:
            print(f"⚠️ Webhook setup failed: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
