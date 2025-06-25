

@celery_app.task
def delete_message_task(chat_id, message_id):
    bot.delete_message(chat_id, message_id)
