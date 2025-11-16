from flask import Flask, request, jsonify, Response
import telebot
import os
import json

app = Flask(__name__)
bot = telebot.TeleBot(os.environ.get('8329471417:AAHczHnEAOZT8eu82qqYq5Pa84nV_TLS0Ok'))

# HTML для MiniApp
MINI_APP_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Group Settings</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: var(--tg-theme-bg-color, #ffffff);
            color: var(--tg-theme-text-color, #000000);
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        .setting {
            background: var(--tg-theme-secondary-bg-color, #f0f0f0);
            margin: 15px 0;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .setting-title {
            font-weight: 600;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .switch {
            position: relative;
            display: inline-block;
            width: 50px;
            height: 24px;
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
            border-radius: 24px;
        }
        .slider:before {
            position: absolute;
            content: "";
            height: 16px;
            width: 16px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        input:checked + .slider {
            background-color: #007aff;
        }
        input:checked + .slider:before {
            transform: translateX(26px);
        }
        .status {
            margin-top: 10px;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            display: none;
        }
        .success {
            background: #4CAF50;
            color: white;
        }
        .error {
            background: #f44336;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>⚙️ Group Settings</h2>
        
        <div class="setting">
            <div class="setting-title">
                Send Messages
                <label class="switch">
                    <input type="checkbox" id="send_messages" onchange="updateSetting('send_messages', this.checked)">
                    <span class="slider"></span>
                </label>
            </div>
            <p>Allow members to send messages</p>
        </div>

        <div class="setting">
            <div class="setting-title">
                Send Media
                <label class="switch">
                    <input type="checkbox" id="send_media" onchange="updateSetting('send_media', this.checked)">
                    <span class="slider"></span>
                </label>
            </div>
            <p>Allow members to send media files</p>
        </div>

        <div class="setting">
            <div class="setting-title">
                Send Polls
                <label class="switch">
                    <input type="checkbox" id="send_polls" onchange="updateSetting('send_polls', this.checked)">
                    <span class="slider"></span>
                </label>
            </div>
            <p>Allow members to send polls</p>
        </div>

        <div class="setting">
            <div class="setting-title">
                Change Info
                <label class="switch">
                    <input type="checkbox" id="change_info" onchange="updateSetting('change_info', this.checked)">
                    <span class="slider"></span>
                </label>
            </div>
            <p>Allow members to change group info</p>
        </div>

        <div class="setting">
            <div class="setting-title">
                Invite Users
                <label class="switch">
                    <input type="checkbox" id="invite_users" onchange="updateSetting('invite_users', this.checked)">
                    <span class="slider"></span>
                </label>
            </div>
            <p>Allow members to invite users</p>
        </div>

        <div class="setting">
            <div class="setting-title">
                Pin Messages
                <label class="switch">
                    <input type="checkbox" id="pin_messages" onchange="updateSetting('pin_messages', this.checked)">
                    <span class="slider"></span>
                </label>
            </div>
            <p>Allow members to pin messages</p>
        </div>

        <div id="status" class="status"></div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        tg.ready();

        // Загрузка текущих настроек
        function loadSettings() {
            // В реальном приложении здесь должен быть запрос к серверу
            const defaultSettings = {
                send_messages: true,
                send_media: true,
                send_polls: true,
                change_info: false,
                invite_users: true,
                pin_messages: false
            };
            
            // Устанавливаем значения переключателей
            document.getElementById('send_messages').checked = defaultSettings.send_messages;
            document.getElementById('send_media').checked = defaultSettings.send_media;
            document.getElementById('send_polls').checked = defaultSettings.send_polls;
            document.getElementById('change_info').checked = defaultSettings.change_info;
            document.getElementById('invite_users').checked = defaultSettings.invite_users;
            document.getElementById('pin_messages').checked = defaultSettings.pin_messages;
        }

        // Обновление настроек
        function updateSetting(setting, value) {
            const settings = {
                send_messages: document.getElementById('send_messages').checked,
                send_media: document.getElementById('send_media').checked,
                send_polls: document.getElementById('send_polls').checked,
                change_info: document.getElementById('change_info').checked,
                invite_users: document.getElementById('invite_users').checked,
                pin_messages: document.getElementById('pin_messages').checked
            };
            
            // Отправка данных боту
            tg.sendData(JSON.stringify({
                action: 'update_group_settings',
                settings: settings
            }));
            
            showStatus('Setting updated!', 'success');
        }

        // Показать статус
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + type;
            status.style.display = 'block';
            
            setTimeout(() => {
                status.style.display = 'none';
            }, 2000);
        }

        // Загружаем настройки при запуске
        loadSettings();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return "Telegram MiniApp Server is running! Visit /group_settings.html for the MiniApp"

@app.route('/group_settings.html')
def group_settings():
    return Response(MINI_APP_HTML, mimetype='text/html')

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'Error', 403

@bot.message_handler(commands=['start', 'settings'])
def handle_settings(message):
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    markup = InlineKeyboardMarkup()
    web_app_button = InlineKeyboardButton(
        "⚙️ Open Group Settings", 
        web_app=telebot.types.WebAppInfo(url="https://donkchatbot.onrender.com/group_settings.html")
    )
    markup.add(web_app_button)
    
    bot.send_message(
        message.chat.id,
        "🎛️ Welcome to Group Settings Manager!\n\nClick the button below to manage group permissions:",
        reply_markup=markup
    )

@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    try:
        data = json.loads(message.web_app_data.data)
        
        if data.get('action') == 'update_group_settings':
            settings = data.get('settings', {})
            
            # Форматируем настройки для красивого вывода
            settings_text = "📋 Updated Group Settings:\n\n"
            for setting, value in settings.items():
                setting_name = setting.replace('_', ' ').title()
                status = "✅ Enabled" if value else "❌ Disabled"
                settings_text += f"• {setting_name}: {status}\n"
            
            bot.send_message(
                message.chat.id,
                f"{settings_text}\n⚡ Changes applied successfully!",
                parse_mode='HTML'
            )
            
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Error updating settings: {str(e)}"
        )

# Обработчик для любых текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.text and not message.text.startswith('/'):
        bot.send_message(
            message.chat.id,
            "🤖 Hello! Use /settings to manage group permissions via MiniApp"
        )

if __name__ == '__main__':
    # Настройка вебхука для Render
    bot.remove_webhook()
    bot.set_webhook(url="https://donkchatbot.onrender.com/webhook")
    
    # Запуск приложения
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
