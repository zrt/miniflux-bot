import miniflux
import config

client = miniflux.Client(config.miniflux_url, config.miniflux_user, config.miniflux_pass)

feeds = client.get_feeds()


def get_entries(after_entry_id):
	if after_entry_id == None:
		return []
	entries =  client.get_entries(status = "unread", limit = 10, order='id', direction = 'asc', after_entry_id=after_entry_id)
	return entries['entries']
