import channels

def waiting(message, page):
    message.reply_channel.send({'accept': True})
    channels.Group('render_page_{}'.format(page)).add(message.reply_channel)