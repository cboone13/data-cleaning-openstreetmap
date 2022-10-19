#!/usr/bin/python
########################################################################
# Name: audit
#
# Description:  This script provides a class to audit the data from
#               an .osm file. It will display the records that need to
#               be modified.
#
# History:
# 05/22/2019    Christopher P. Boone          Genisis.
########################################################################
# Imports
from collections import defaultdict
import codecs
import csv
from csv import DictWriter
import json
import pprint
import re
import xml.etree.ElementTree as ET
import datetime
import sys
sys.path.append("../DataWrangling")


class AuditClean:
    """
    Class to audit and load a designated .osm file.
    """

    def __init__(self, config_data):
        assert config_data, "Configuration data not provided!"

        # Sample run variable?
        self.sample_run = config_data['SAMPLE']['SAMPLE_RUN']
        self.sample_osm = config_data['SAMPLE']['SAMPLE_OSM']

        # OSM variables.
        self.app_data = config_data['APP_DATA']
        self.osm_file = config_data['OSM_DATA']['OSM_FILE']
        self.osm_path = config_data['OSM_DATA']['OSM_PATH']

        # CSV file file paths.
        self.nodes_path = config_data['DATA']['NODES_PATH']
        self.node_tags_path = config_data['DATA']['NODE_TAGS_PATH']
        self.ways_path = config_data['DATA']['WAYS_PATH']
        self.way_nodes_path = config_data['DATA']['WAY_NODES_PATH']

        # CSV file fields.
        self.node_fields = json.loads(config_data['DATA']['NODE_FIELDS'])
        self.node_tag_fields = json.loads(
                                        config_data['DATA']['NODE_TAG_FIELDS']
                                         )
        self.way_fields = json.loads(config_data['DATA']['WAY_FIELDS'])
        self.way_nodes_fields = json.loads(
                                        config_data['DATA']['WAY_NODES_FIELDS']
                                          )

        self.street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
        self.street_types = defaultdict(set)

        # Expected list of approved street endings.
        self.expected = [
                    "Street", "Avenue", "Boulevard", "Drive", "Court", "Place",
                    "Road", "Way", "Circle", "Trail", "Mall", "Square",
                    "Creek", "I-95"
                        ]

        self.mapping = {
                        "St": "Street",
                        "St.": "Street",
                        "Rd": "Road",
                        "Ave": "Avenue",
                        "Ft.": "Fort"
                      }
        return

    def audit_street_type(self, street_name):
        # Add street name to street array.
        # street_name = 'Ft. Bragg rd'
        m = self.street_type_re.search(street_name)
        if m:
            street_type = m.group()
            if street_type not in self.expected:
                self.street_types[street_type].add(street_name)

    def audit(self):
        """
        Open OSM file and find all abnormal street names, postal codes,
        and cities. Print the results.
        """

        osm_file = open(self.osm_file, 'r', encoding='utf-8')
        # self.element = ET.parse('interpreter.osm')
        # self.elem = self.element.getroot()
        # for stuff in self.elem.findall('node'):
        for event, elem in ET.iterparse(osm_file, events=("start",)):
            try:
                if elem.tag == 'way' or elem.tag == 'node':
                    for tag in elem.iter("tag"):
                        if tag.attrib['k'] == "addr:street":
                            self.audit_street_type(tag.attrib['v'])
            except:
                pass

        return (self.street_types)

    def retrieve_element(self, tags=('node', 'way', 'relation')):
        """
        Returns generator that iterates once over each
        element for retrieval.
        """
        open_file = open(self.osm_file, "r", encoding="utf8")

        context = ET.iterparse(open_file, events=('start', 'end'))
        context = iter(context)
        _, root = context.__next__()
        for event, elem in context:
            if event == 'end' and elem.tag in tags:
                yield elem
                root.clear()

    def shape_element(self, element, default_tag='regular'):
        """
        Shapes and cleans node before storing in a dictionary to prepare
        the record to be inserted into a .csv.
        """

        street_types = self.audit()
        for street_types, ways in street_types.items():
            for name in ways:
                self.update_name(name)

        way_attr = {}
        node_attr = {}
        way_nodes = []
        tags = []

        if element.tag == 'node':
            for obj in self.node_fields:
                node_attr[obj] = element.attrib[obj]

            for tag_two in element.iter('tag'):
                tag_elements = {}
                tag_elements['id'] = element.attrib['id']
                tag_elements['value'] = tag_two.attrib['v']

                tag_elements['type'] = default_tag
                tag_elements['key'] = tag_two.attrib['k']

                tags.append(tag_elements)

            return({'node': node_attr, 'node_tags': tags})

        elif element.tag == 'way':
            for obj in self.way_fields:
                way_attr[obj] = element.attrib[obj]

            for tag_two in element.iter('tag'):
                tag_elements = {}
                tag_elements['id'] = element.attrib['id']

                if 'v' in element.attrib.keys():
                    tag_elements['value'] == element.attrib['v']
                else:
                    tag_elements['value'] = 'None'

                tag_elements['type'] = 'regular'
                tag_elements['key'] = tag_two.attrib['k']

                tags.append(tag_elements)

            position = 0

            for node in element.iter('nd'):
                waynd_dt = {}
                waynd_dt['id'] = element.attrib['id']
                waynd_dt['node_id'] = node.attrib['ref']
                waynd_dt['position'] = position
                position += 1

                way_nodes.append(waynd_dt)

            return({'way': way_attr, 'way_nodes': way_nodes, 'way_tags': tags})

    def update_name(self, name):
        """
        This method updates bad records and formats them to our standard.
        """

        # Ensure all street names are capitalized correctly.
        lowercase_name = name.lower().replace('  ', ' ')

        t = lowercase_name.split(' ')
        change_name = t[0].capitalize()

        for i in range(1, len(t)):
            change_name += ' ' + t[i].capitalize()

        else:
            change_name = lowercase_name.capitalize()

        map_keys = self.mapping.keys()
        key_list = list(map_keys)

        # check if street is an abbreviation and if so replace with mapping.
        for abbrv in key_list:
            if abbrv in change_name.split():
                change_name = change_name.replace(
                                                abbrv,
                                                self.mapping[abbrv]
                                                 )

        return (change_name)

    def get_sample(self):
        """
        create sample of osm file.
        """
        k = 1
        with open(self.sample_osm, 'wb') as output:
            output.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
            output.write(b'<osm>\n  ')

            # Write every kth top level element
            for i, element in enumerate(self.retrieve_element()):
                if i % k == 0:
                    output.write(ET.tostring(element, encoding='utf-8'))

            output.write(b'</osm>')

    def process(self):
        """
        Method to write the .osm elements to the respective .csv file.
        """
        if self.sample_run == 'True':
            self.get_sample()

        # Open/create .csv files for writing.
        with codecs.open(self.ways_path, 'w') \
            as ways_file, \
            codecs.open(self.way_nodes_path, 'w') \
            as ways_nodes_file, \
            codecs.open(self.way_tags_path, 'w') \
            as ways_tags_file, \
            codecs.open(self.nodes_path, 'w') \
            as nodes_file, \
            codecs.open(self.node_tags_path, 'w') \
                as nodes_tags_file:

            ways_writer = csv.DictWriter(
                                         ways_file,
                                         delimiter=',',
                                         lineterminator='\n',
                                         fieldnames=self.way_fields
                                        )
            way_nodes_writer = csv.DictWriter(
                                            ways_nodes_file,
                                            delimiter=',',
                                            lineterminator='\n',
                                            fieldnames=self.way_nodes_fields
                                             )
            nodes_writer = csv.DictWriter(
                                          nodes_file, delimiter=',',
                                          lineterminator='\n',
                                          fieldnames=self.node_fields
                                         )
            node_tags_writer = csv.DictWriter(
                                              nodes_tags_file,
                                              delimiter=',',
                                              lineterminator='\n',
                                              fieldnames=self.node_tag_fields
                                             )

            # write headers to .csv files.
            nodes_writer.writeheader()
            node_tags_writer.writeheader()
            ways_writer.writeheader()
            way_nodes_writer.writeheader()

            # Retrieve each element and audit.
            for obj in self.retrieve_element(tags=('node', 'way')):
                element = self.shape_element(obj)

                # Write each element to respective .csv file if it is a node or way.
                if element:
                    try:
                        if obj.tag == 'node':
                            nodes_writer.writerow(element['node'])
                            # for node_tag in element['node_tags']:
                            node_tags_writer.writerows(element['node_tags'])
                            print('record written Node')
                        elif obj.tag == 'way':
                            ways_writer.writerow(element['way'])
                            way_nodes_writer.writerows(element['way_nodes'])
                            # for way_tag in element['way_tags']:
                            print('record written Way')
                    except:
                        pass
        return
