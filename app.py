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

# Функция для получения ТЕКУЩИХ настроек группы
def get_current_group_settings(chat_id):
    """Получает актуальные настройки группы из Telegram"""
    try:
        chat = bot.get_chat(chat_id)
        permissions = chat.permissions
        
        current_settings = {
            'can_send_messages': permissions.can_send_messages if permissions else True,
            'can_send_media_messages': permissions.can_send_media_messages if permissions else True,
            'can_send_polls': permissions.can_send_polls if permissions else True,
            'can_change_info': permissions.can_change_info if permissions else False,
            'can_invite_users': permissions.can_invite_users if permissions else True,
            'can_pin_messages': permissions.can_pin_messages if permissions else False
        }
        
        print(f"📊 Current settings for chat {chat_id}: {current_settings}")
        return current_settings
    except Exception as e:
        print(f"❌ Error getting current settings: {e}")
        return None

# Функция для обновления настроек
def update_group_permissions(chat_id, new_settings):
    """Изменяет настройки группы и проверяет результат"""
    try:
        from telebot.types import ChatPermissions
        
        permissions = ChatPermissions(
            can_send_messages=new_settings.get('can_send_messages', True),
            can_send_media_messages=new_settings.get('can_send_media_messages', True),
            can_send_polls=new_settings.get('can_send_polls', True),
            can_change_info=new_settings.get('can_change_info', False),
            can_invite_users=new_settings.get('can_invite_users', True),
            can_pin_messages=new_settings.get('can_pin_messages', False)
        )
        
        # Устанавливаем новые настройки
        bot.set_chat_permissions(chat_id, permissions)
        
        # ПРОВЕРЯЕМ, что настройки применились
        import time
        time.sleep(2)  # Ждем применения
        
        verified_settings = get_current_group_settings(chat_id)
        
        # Сравниваем запрошенные и фактические настройки
        if verified_settings:
            success = all(
                verified_settings.get(key) == new_settings.get(key, True) 
                for key in new_settings.keys()
            )
            return success, verified_settings
        return False, None
        
    except Exception as e:
        print(f"❌ Error updating permissions: {e}")
        return False, None

# HTML с динамической загрузкой текущих настроек
def get_mini_app_html():
    """Генерирует HTML с текущими настройками группы"""
    current_settings = {}
    
    if BOT_TOKEN:
        current_settings = get_current_group_settings(GROUP_CHAT_ID) or {}
    
    # Значения по умолчанию, если не удалось получить настройки
    default_settings = {
        'can_send_messages': True,
        'can_send_media_messages': True, 
        'can_send_polls': True,
        'can_change_info': False,
        'can_invite_users': True,
        'can_pin_messages': False
    }
    
    # Объединяем с текущими настройками
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
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
            display: none;
        }}
        .success {{
            background: #4CAF50;
            color: white;
        }}
        .error {{
            background: #f44336;
            color: white;
        }}
        .current-settings {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .refresh-btn {{
            background: #007aff;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 8px;
            cursor: pointer;
            margin-bottom: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="current-settings">
            <h3>⚙️ Текущие настройки группы</h3>
            <p><small>Group ID: {GROUP_CHAT_ID}</small></p>
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

        // Загрузка текущих настроек
        function loadCurrentSettings() {{
            showStatus('Загрузка текущих настроек...', 'success');
            // Перезагружаем страницу для обновления настроек
            setTimeout(() => location.reload(), 1000);
        }}

        // Обновление настроек
        function updateSetting(setting, value) {{
            const settings = {{
                can_send_messages: document.getElementById('can_send_messages').checked,
                can_send_media_messages: document.getElementById('can_send_media_messages').checked,
                can_send_polls: document.getElementById('can_send_polls').checked,
                can_change_info: document.getElementById('can_change_info').checked,
                can_invite_users: document.getElementById('can_invite_users').checked,
                can_pin_messages: document.getElementById('can_pin_messages').checked
            }};
            
            console.log('Sending settings:', settings);
            
            // Отправка данных боту
            tg.sendData(JSON.stringify({{
                action: 'update_group_settings',
                settings: settings,
                chat_id: {GROUP_CHAT_ID}
            }}));
            
            showStatus('Настройки отправлены на обновление...', 'success');
        }}

        // Добавляем обработчики изменений
        document.addEventListener('DOMContentLoaded', function() {{
            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(checkbox => {{
                checkbox.addEventListener('change', function() {{
                    updateSetting(this.id, this.checked);
                }});
            }});
        }});

        // Показать статус
        function showStatus(message, type) {{
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + type;
            status.style.display = 'block';
            
            setTimeout(() => {{
                status.style.display = 'none';
            }}, 3000);
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
        
        bot.send_message(
            message.chat.id,
            "🎛️ Панель управления настройками группы\n\nНажмите кнопку ниже чтобы изменить разрешения:",
            reply_markup=markup
        )

    @bot.message_handler(content_types=['web_app_data'])
    def handle_web_app_data(message):
        if not check_user_access(message.from_user.id):
            bot.send_message(message.chat.id, "🚫 Access Denied")
            return
            
        try:
            data = json.loads(message.web_app_data.data)
            print(f"📨 Received data: {data}")
            
            if data.get('action') == 'update_group_settings':
                settings = data.get('settings', {})
                chat_id = data.get('chat_id', GROUP_CHAT_ID)
                
                print(f"🔄 Updating settings: {settings}")
                
                # ОБНОВЛЯЕМ И ПРОВЕРЯЕМ настройки
                success, verified_settings = update_group_permissions(chat_id, settings)
                
                if success:
                    settings_text = "✅ Настройки обновлены и проверены:\n\n"
                    setting_names = {
                        'can_send_messages': '📝 Отправка сообщений',
                        'can_send_media_messages': '🖼️ Отправка медиа',
                        'can_send_polls': '📊 Создание опросов', 
                        'can_change_info': '✏️ Изменение информации',
                        'can_invite_users': '👥 Приглашение пользователей',
                        'can_pin_messages': '📌 Закрепление сообщений'
                    }
                    
                    for setting, value in verified_settings.items():
                        setting_name = setting_names.get(setting, setting)
                        status = "✅ Включено" if value else "❌ Выключено"
                        settings_text += f"• {setting_name}: {status}\n"
                    
                    bot.send_message(message.chat.id, f"{settings_text}⚡ Изменения применены!")
                else:
                    bot.send_message(message.chat.id, "❌ Не удалось обновить настройки. Проверьте права бота.")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")

    # Команда для проверки текущих настроек
    @bot.message_handler(commands=['check_settings'])
    def check_current_settings(message):
        """Показывает текущие настройки группы"""
        settings = get_current_group_settings(GROUP_CHAT_ID)
        
        if settings:
            settings_text = "📊 Текущие настройки группы:\n\n"
            setting_names = {
                'can_send_messages': '📝 Отправка сообщений',
                'can_send_media_messages': '🖼️ Отправка медиа', 
                'can_send_polls': '📊 Создание опросов',
                'can_change_info': '✏️ Изменение информации',
                'can_invite_users': '👥 Приглашение пользователей',
                'can_pin_messages': '📌 Закрепление сообщений'
            }
            
            for setting, value in settings.items():
                setting_name = setting_names.get(setting, setting)
                status = "✅ ВКЛ" if value else "❌ ВЫКЛ"
                settings_text += f"• {setting_name}: {status}\n"
            
            bot.send_message(message.chat.id, settings_text)
        else:
            bot.send_message(message.chat.id, "❌ Не удалось получить настройки")

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
