# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class FightmatrixPipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        record = adapter.get('ufcrecord')
        if record:
            adapter['ufcrecord'] = record.strip()

        return item