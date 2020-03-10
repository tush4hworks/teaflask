import pytz
import datetime
from collections import defaultdict
fmt = '%Y-%m-%d %H:%M:%S %Z%z'
tea_list = {'TajMahal':'Good',
			'TataPremium':'Best',
			'RedLabel':'Poor',
			'BaghBakri':'Average'}

ambigous_time = datetime.datetime.now()

def reverse_dict(tdict):
	rdict = {}
	for key in tdict.keys():
		try:
			pytz.country_timezones(key)
		except KeyError:
			continue
		rdict[tdict[key]] = key
	return rdict

def get_current_time(common_timezone):
	tz = pytz.timezone(common_timezone)
	utc_dt = datetime.datetime.now(tz = pytz.utc)
	return utc_dt.astimezone(tz).strftime(fmt)

def get_timeinfo_for_all_timezones():
	return sorted([(tz, get_current_time(tz)) for tz in pytz.common_timezones], 
		key = lambda x: pytz.timezone(x[0]).utcoffset(ambigous_time).total_seconds())

def get_timeinfo_for_all_countries():
	country_codes = reverse_dict(pytz.country_names)
	return sorted([(country, get_current_time(timezone)) for country in country_codes.keys() for 
		timezone in pytz.country_timezones(country_codes[country])], 
		key=lambda x: x[0])