
def get_path_key(path):
   key = 'render_page_{}'.format(path.split('?')[0].strip('/').replace('/', '_').replace('&', '_'))
   return key