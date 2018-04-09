from urllib.parse import unquote_plus

def get_path_key(path):
   path = unquote_plus(path)
   key = 'render_page_{}'.format(path.split('?')[0].strip('/').replace('/', '_').replace('&', '_'))
   return key