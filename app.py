from flask import Flask, request, jsonify, Response
import telebot
import os
import json

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ALLOWED_USER_ID = 1444832263
GROUP_CHAT_ID = -1001721934457

if BOT_TOKEN:
    bot = telebot.TeleBot(BOT_TOKEN)
else:
    bot = None
    print("⚠️  BOT_TOKEN not set - running in demo mode")

# Функция для получения ТЕКУЩИХ настроек группы с отладкой
def get_current_group_settings(chat_id):
    """Получает актуальные настройки группы из Telegram"""
    try:
        print(f"🔍 Attempting to get settings for chat: {chat_id}")
        
        # Получаем информацию о чате
        chat = bot.get_chat(chat_id)
        print(f"📋 Chat info received: {chat.title if hasattr(chat, 'title') else 'No title'}")
        
        # Получаем информацию о боте как участнике чата
        bot_member = bot.get_chat_member(chat_id, bot.get_me().id)
        print(f"🤖 Bot member status: {bot_member.status}")
        
        if bot_member.status != 'administrator':
            print("❌ Bot is not administrator!")
            return None
            
        print(f"✅ Bot is administrator, checking permissions...")
        
        # Получаем настройки разрешений
        permissions = chat.permissions
        print(f"🔓 Permissions object: {permissions}")
        
        if permissions:
            current_settings = {
                'can_send_messages': permissions.can_send_messages,
                'can_send_media_messages': permissions.can_send_media_messages,
                'can_send_polls': permissions.can_send_polls,
                'can_change_info': permissions.can_change_info,
                'can_invite_users': permissions.can_invite_users,
                'can_pin_messages': permissions.can_pin_messages
            }
            
            print(f"📊 Extracted settings: {current_settings}")
            return current_settings
        else:
            print("❌ No permissions object found")
            return None
            
    except Exception as e:
        print(f"❌ Error getting current settings: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        return None

# Функция для проверки прав бота
def check_bot_permissions(chat_id):
    """Проверяет права бота в группе"""
    try:
        bot_member = bot.get_chat_member(chat_id, bot.get_me().id)
        
        if bot_member.status == 'administrator':
            rights_info = {
                'can_manage_chat': bot_member.can_manage_chat,  # Управление настройками
                'can_change_info': bot_member.can_change_info,
                'can_delete_messages': bot_member.can_delete_messages,
                'can_restrict_members': bot_member.can_restrict_members,
                'can_invite_users': bot_member.can_invite_users,
                'can_pin_messages': bot_member.can_pin_messages,
                'can_manage_video_chats': bot_member.can_manage_video_chats
            }
            return rights_info
        return None
    except Exception as e:
        print(f"❌ Error checking bot permissions: {e}")
        return None

# HTML с улучшенной обработкой ошибок
def get_mini_app_html():
    """Генерирует HTML с текущими настройками группы"""
    current_settings = {}
    bot_permissions = {}
    error_message = ""
    
    if BOT_TOKEN:
        # Проверяем права бота
        bot_permissions = check_bot_permissions(GROUP_CHAT_ID)
        print(f"🔐 Bot permissions: {bot_permissions}")
        
        if bot_permissions and bot_permissions.get('can_manage_chat'):
            current_settings = get_current_group_settings(GROUP_CHAT_ID) or {}
        else:
            error_message = "❌ Бот не имеет прав 'Управление настройками группы'"
    
    # Значения по умолчанию
    default_settings = {
        'can_send_messages': True,
        'can_send_media_messages': True, 
        'can_send_polls': True,
        'can_change_info': False,
        'can_invite_users': True,
        'can_pin_messages': False
    }
    
    settings = {**default_settings, **current_settings}
    
    return f"""
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
        .status {{
            margin-top: 10px;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
        }}
        .success {{
            background: #4CAF50;
            color: white;
        }}
        .error {{
            background: #f44336;
            color: white;
        }}
        .warning {{
            background: #ff9800;
            color: white;
        }}
        .refresh-btn {{
            background: #007aff;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 8px;
            cursor: pointer;
            margin: 10px 0;
        }}
        .permissions-info {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="permissions-info">
            <h3>⚙️ Управление настройками группы</h3>
            <p><strong>ID группы:</strong> {GROUP_CHAT_ID}</p>
            {"<p class='error'>" + error_message + "</p>" if error_message else 
             "<p class='success'>✅ Бот имеет необходимые права</p>" if bot_permissions and bot_permissions.get('can_manage_chat') else 
             "<p class='warning'>⚠️ Проверка прав...</p>"}
            <button class="refresh-btn" onclick="loadCurrentSettings()">🔄 Обновить настройки</button>
        </div>
        
        <h3>📋 Разрешения участников:</h3>
        
        <div class="setting">
            <div class="setting-title">
                Отправка сообщений
                <label class="switch">
                    <input type="checkbox" id="can_send_messages" { "checked" if settings['can_send_messages'] else "" }>
                    <span class="slider"></span>
                </label>
            </div>
            <p>Участники могут отправлять текстовые сообщения</p>
        </div>

        <div class="setting">
            <div class="setting-title">
                Отправка медиа
                <label class="switch">
                    <input type="checkbox" id="can_send_media_messages" { "checked" if settings['can_send_media_messages'] else "" }>
                    <span class="slider"></span>
                </label>
            </div>
            <p>Фото, видео, музыка, файлы, голосовые сообщения</p>
        </div>

        <div class="setting">
            <div class="setting-title">
                Создание опросов
                <label class="switch">
                    <input type="checkbox" id="can_send_polls" { "checked" if settings['can_send_polls'] else "" }>
                    <span class="slider"></span>
                </label>
            </div>
            <p>Участники могут создавать опросы</p>
        </div>

        <div class="setting">
            <div class="setting-title">
                Изменение информации
                <label class="switch">
                    <input type="checkbox" id="can_change_info" { "checked" if settings['can_change_info'] else "" }>
                    <span class="slider"></span>
                </label>
            </div>
            <p>Изменение названия, фото и описания группы</p>
        </div>

        <div class="setting">
            <div class="setting-title">
                Приглашение пользователей
                <label class="switch">
                    <input type="checkbox" id="can_invite_users" { "checked" if settings['can_invite_users'] else "" }>
                    <span class="slider"></span>
                </label>
            </div>
            <p>Участники могут приглашать новых пользователей</p>
        </div>

        <div class="setting">
            <div class="setting-title">
                Закрепление сообщений
                <label class="switch">
                    <input type="checkbox" id="can_pin_messages" { "checked" if settings['can_pin_messages'] else "" }>
                    <span class="slider"></span>
                </label>
            </div>
            <p>Участники могут закреплять сообщения</p>
        </div>

        <div id="status" class="status"></div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        tg.ready();

        function loadCurrentSettings() {{
            showStatus('Загрузка текущих настроек...', 'success');
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
            
            tg.sendData(JSON.stringify({{
                action: 'update_group_settings',
                settings: settings,
                chat_id: {GROUP_CHAT_ID}
            }}));
            
            showStatus('Настройки отправлены...', 'success');
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
            setTimeout(() => {{ status.style.display = 'none'; }}, 3000);
        }}
    </script>
</body>
</html>
"""

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
        
        bot.send_message(message.chat.id, "🎛️ Панель управления настройками", reply_markup=markup)

    @bot.message_handler(commands=['check_rights'])
    def check_bot_rights(message):
        """Детальная проверка прав бота"""
        try:
            bot_permissions = check_bot_permissions(GROUP_CHAT_ID)
            
            if bot_permissions:
                rights_text = "🔐 Права бота в группе:\n\n"
                rights_mapping = {
                    'can_manage_chat': '⚙️ Управление настройками группы',
                    'can_change_info': '✏️ Изменение профиля группы',
                    'can_delete_messages': '🗑️ Удаление сообщений',
                    'can_restrict_members': '🚫 Блокировка пользователей',
                    'can_invite_users': '👥 Приглашение пользователей',
                    'can_pin_messages': '📌 Закрепление сообщений',
                    'can_manage_video_chats': '🎥 Управление видеочатами'
                }
                
                for right, description in rights_mapping.items():
                    status = "✅ ЕСТЬ" if bot_permissions.get(right) else "❌ НЕТ"
                    rights_text += f"{description}: {status}\n"
                
                bot.send_message(message.chat.id, rights_text)
            else:
                bot.send_message(message.chat.id, "❌ Бот не является администратором группы")
                
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка проверки прав: {str(e)}")

    @bot.message_handler(commands=['debug'])
    def debug_info(message):
        """Отладочная информация"""
        try:
            debug_text = "🐛 Отладочная информация:\n\n"
            
            # Информация о боте
            me = bot.get_me()
            debug_text += f"🤖 Бот: @{me.username}\n"
            
            # Права бота
            bot_permissions = check_bot_permissions(GROUP_CHAT_ID)
            debug_text += f"🔐 Права управления: {bot_permissions.get('can_manage_chat') if bot_permissions else 'NO'}\n"
            
            # Настройки группы
            settings = get_current_group_settings(GROUP_CHAT_ID)
            debug_text += f"📊 Настройки получены: {'YES' if settings else 'NO'}\n"
            
            if settings:
                debug_text += f"Сообщения: {settings['can_send_messages']}\n"
                debug_text += f"Медиа: {settings['can_send_media_messages']}\n"
            
            bot.send_message(message.chat.id, debug_text)
            
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка отладки: {str(e)}")

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
                
                # Проверяем права перед изменением
                bot_permissions = check_bot_permissions(chat_id)
                if not bot_permissions or not bot_permissions.get('can_manage_chat'):
                    bot.send_message(message.chat.id, "❌ У бота нет прав 'Управление настройками группы'")
                    return
                
                # Изменяем настройки
                from telebot.types import ChatPermissions
                permissions = ChatPermissions(
                    can_send_messages=settings.get('can_send_messages', True),
                    can_send_media_messages=settings.get('can_send_media_messages', True),
                    can_send_polls=settings.get('can_send_polls', True),
                    can_change_info=settings.get('can_change_info', False),
                    can_invite_users=settings.get('can_invite_users', True),
                    can_pin_messages=settings.get('can_pin_messages', False)
                )
                
                bot.set_chat_permissions(chat_id, permissions)
                bot.send_message(message.chat.id, "✅ Настройки обновлены!")
                
        except Exception as e:
            print(f"❌ Web app error: {e}")
            bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")

if __name__ == '__main__':
    if BOT_TOKEN:
        try:
            bot.remove_webhook()
            bot.set_webhook(url="https://donkchatbot.onrender.com/webhook")
            print("✅ Webhook set successfully")
        except Exception as e:
            print(f"⚠️ Webhook setup failed: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
