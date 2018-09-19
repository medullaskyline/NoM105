import scrapy
from selenium import webdriver

import json
import re

'''
usage: $ scrapy runspider orunited.py -o event_data.json
'''


# item class included here 
class EventItem(scrapy.Item):
	# define the fields for your item here like:
	link = scrapy.Field()
	query_param_organization = scrapy.Field()
	event_name = scrapy.Field()
	event_start = scrapy.Field()
	event_end = scrapy.Field()
	location_name = scrapy.Field()
	location_addr = scrapy.Field()
	location_lat = scrapy.Field()
	location_lon = scrapy.Field()
	description = scrapy.Field()


class EventSpider(scrapy.spiders.Spider):
	name = 'eventspider'
	start_urls = [f'https://secure.everyaction.com/p/8tLg4VQurUON83E_o1ntGA2?pn={i}' for i in range(1,8)]

	def __init__(self):
		self.driver = webdriver.Chrome()

	def parse(self, response):
		self.logger.info(f'response.url {response.url}')
		for event_url in response.css('.oa-event-result-signup-link ::attr(href)').extract():

			if event_url is not None:
				next_page = f'https://secure.everyaction.com/v1/Forms/{event_url.split("/").pop()}'
				yield response.follow(next_page, self.parse_event_page)


	def parse_event_page(self, response):

		item = EventItem()

		json_body = json.loads(response.body)
		short_code = json_body.get('shortCode')
		additional_info = next(filter(lambda x: x['name'] == 'AdditionalInformation', json_body.get('form_elements')), {})
		organization_info = next(filter(lambda x: x.get('title') == 'What organization recruited you?', additional_info.get('children', [])), [])
		event_info = json_body.get('metadata', {}).get('event_info', {})

		item["link"] = f'https://secure.everyaction.com/{short_code}'
		item["query_param_organization"] = (organization_info or {}).get('queryString')
		item["event_name"] = event_info.get('eventName')

		# change start and end -- not calibrated for PDT and PST
		item["event_start"] = event_info.get('start').replace('-04:00', '-07:00').replace('-05:00', '-08:00')
		item["event_end"] = event_info.get('end').replace('-04:00', '-07:00').replace('-05:00', '-08:00')

		# get markup as a scrapy HtmlResponse
		first_form_element = next(filter(lambda x: x.get('name') == 'HeaderHtml', json_body.get('form_elements', [])), None)
		markup = (first_form_element or {}).get('markup', '')
		resp_markup = scrapy.http.HtmlResponse(url='dummy url', body=markup, encoding='utf-8')

		try:
			# get location info
			data_map_locations = resp_markup.css('.at-event-map-container ::attr(data-map-locations)').extract_first()
			data_map_location = json.loads(data_map_locations).pop(0)  # assuming always one and only one location
			item["location_name"] = data_map_location.get('Title')
			item["location_addr"] = data_map_location.get('Description')
			item["location_lat"] = data_map_location.get('Longitude')
			item["location_lon"] = data_map_location.get('Latitude')
		except (IndexError, TypeError):

			map_marker_selector_list = resp_markup.css('.glyphicons-map-marker')
			if map_marker_selector_list:
				location = map_marker_selector_list[0].root.getparent().text_content()
				item["location_name"] = location.split(',').pop(0)
				item["location_addr"] = ','.join(location.split(',')[1:]).strip()

		try:
			# get description, assuming description is the last <p> tag
			description = resp_markup.css('p::text').pop(-1).extract()
			item["description"] = re.compile(r'\r|\n').sub('', description)
		except (IndexError, TypeError):
			pass

		yield item
		
		

