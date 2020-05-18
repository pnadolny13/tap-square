#!/usr/bin/env python3

"""singer-tap for square APIs"""

import os
import sys
import json
import collections
import requests
import singer
from singer import utils
from singer.schema import Schema
from genson import SchemaBuilder
from schemas import get_schemas, STREAMS
# from singer.catalog import Catalog, CatalogEntry


REQUIRED_CONFIG_KEYS = ["host", "access_token"]
LOGGER = singer.get_logger()


def get_abs_path(path):
    """ get the file path """
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def load_schemas():
    """ Load schemas from schemas folder """
    schemas = {}
    for filename in os.listdir(get_abs_path('schemas')):
        path = get_abs_path('schemas') + '/' + filename
        file_raw = filename.replace('.json', '')
        with open(path) as file:
            schemas[file_raw] = Schema.from_dict(json.load(file))
    return schemas


def get_columns(rows):

    """get common columns for all the rows"""

    columns = []
    for row in rows:
        columns = columns + list(row.keys() - columns)
    return columns


def merge_schema(rows, columns):

    """ add the empty values in missing columns for each row """

    new_rows = []
    for row in rows:
        for col in columns:
            if col not in row.keys():
                row[col] = ''
            if isinstance(row[col], bool):
                row[col] = str(row[col]).lower()
        json_data = json.dumps(row, indent=2, sort_keys=True)
        new_rows.append(json.loads(json_data))
    return new_rows


def flatten(data, parent_key='', sep='__'):

    """ Return flatte json from nested json """

    items = []
    collections_abc = collections.abc
    for key, val in data.items():
        new_key = parent_key + sep + key if parent_key else key
        if isinstance(val, collections_abc.MutableMapping):
            items.extend(flatten(val, new_key, sep=sep).items())
        else:
            items.append((new_key, str(val) if isinstance(val, list) else val))
    return dict(items)


def get_json_schemas(json_data):

    """Return the standared json schema for given json"""

    builder = SchemaBuilder()
    builder.add_schema({"type": "object", "properties": {}})
    builder.add_object(json_data)
    api_schema = builder.to_schema()
    return api_schema


def clean_api_data(response):

    """ To maintain same schema in json, flatting and merging the schema for all rows """

    key = [*response][0]
    rows = response[key]
    flatted_rows = []

    for row in rows:
        flatted_rows.append(flatten(row))

    columns = get_columns(flatted_rows)
    final_rows = merge_schema(flatted_rows, columns)
    schemas = get_json_schemas(final_rows)
    return final_rows, schemas


def get_api_data(token, url, method):

    """ Return api data """

    header = {"Authorization": "Bearer "+token, "Content-type": "application/json"}

    if method == "post":
        responses = requests.post(url, headers=header)
    else:
        responses = requests.get(url, headers=header)

    responses.raise_for_status()

    return responses.json()


def json_value_to_list(json_data):

    """ Return Json Data in list and the lenth of list """

    key = list(json_data.keys())[0]
    data = json_data[key]
    lenth_of_list = len(data)
    return data, lenth_of_list


def get_item_variation_id_location_id(config):

    """ Return the itrm_variant id and location id"""

    url_item_variant = config['host'] + "v2/catalog/list?types=ITEM_VARIATION"
    url_location = config['host'] + "v2/locations"

    item_variant = get_api_data(config['access_token'], url_item_variant, 'get')
    locations = get_api_data(config['access_token'], url_location, 'get')

    item_variant_data, lenth_of_item = json_value_to_list(item_variant)
    locations_data, lenth_of_location = json_value_to_list(locations)

    item_variant_id = []
    for item in range(lenth_of_item):
        item_variant_id.append(item_variant_data[item]['id'])

    location_id = []
    for location in range(lenth_of_location):
        location_id.append(locations_data[location]['id'])

    return item_variant_id, location_id


def singer_write(stream_name, json_data, schema):

    """ Write schema, records and state to singer """

    singer.write_schema(stream_name=stream_name, schema=schema, key_properties=[])
    singer.write_records(stream_name, json_data)
    singer.write_state({stream_name: 'Done'})


def retrieve_api_data(token, url, method):

    """ return the api data """

    header = {"Authorization": "Bearer "+token, "Content-type": "application/json"}

    if method == 'get':
        responses = requests.get(url, headers=header)
    else:
        responses = requests.post(url, headers=header)

    responses.raise_for_status()

    return responses.json()


def retrieve_api_json_data(token, url, json_body):

    """ return the api data with json as input"""

    header = {"Authorization": "Bearer "+token, "Content-type": "application/json"}
    responses = requests.post(url, json=json_body, headers=header)
    responses.raise_for_status()

    return responses.json()


def sync_retrieve_api_data(config, custom_arguments, api):

    """ collect the api data for specific ids """

    keys = list(custom_arguments.keys())
    ids = list(custom_arguments[keys[0]])

    rows = list()

    for _id in ids:

        url = config['host'] + api.replace(keys[0], "").format(_id)
        row = retrieve_api_data(config['access_token'], url, "get")

        if [*row][0] == 'errors':
            sys.exit("invalid id {} to retrieve api data".format(_id))
        else:
            if bool(row):
                rows.append(flatten(row))

    if len(rows) > 0:
        columns = get_columns(rows)
        final_rows = merge_schema(rows, columns)
        schemas = get_json_schemas(final_rows[0])
        is_sync = True
    else:
        final_rows = list()
        schemas = {}
        is_sync = False

    return final_rows, schemas, is_sync


def sync_direct_api_get(config, _custom_arguments, api):

    """ get the dirrect api data get method"""

    url = config['host'] + api
    response = get_api_data(config['access_token'], url, "get")

    if bool(response):
        final_rows, schemas = clean_api_data(response)
        is_sync = True
    else:
        final_rows = list()
        schemas = {}
        is_sync = False

    return final_rows, schemas, is_sync


def sync_direct_api_post(config, _custom_arguments, api):

    """ get the dirrect api data post method"""

    url = config['host'] + api
    response = get_api_data(config['access_token'], url, "post")

    if bool(response):
        final_rows, schemas = clean_api_data(response)
        is_sync = True
    else:
        final_rows = list()
        schemas = {}
        is_sync = False

    return final_rows, schemas, is_sync


def sync_inventory_physical(config, _custom_arguments, api):

    """ get the inventory physical count api data in post method"""

    item_variant_id, location_id = get_item_variation_id_location_id(config)
    json_physical_count = {"catalog_object_ids": item_variant_id,
                           "location_ids": location_id, "types": ["PHYSICAL_COUNT"]}
    url = config['host'] + api
    response = retrieve_api_json_data(config['access_token'], url, json_physical_count)

    if bool(response):
        final_rows, schemas = clean_api_data(response)
        is_sync = True
    else:
        final_rows = list()
        schemas = {}
        is_sync = False

    return final_rows, schemas, is_sync


def sync_inventory_adjustment(config, _custom_arguments, api):

    """ get the inventory adjustment count api data in post method"""

    item_variant_id, location_id = get_item_variation_id_location_id(config)
    json_adjustment_count = {"catalog_object_ids": item_variant_id,
                             "location_ids": location_id, "types": ["ADJUSTMENT"]}
    url = config['host'] + api
    response = retrieve_api_json_data(config['access_token'], url, json_adjustment_count)

    if bool(response):
        final_rows, schemas = clean_api_data(response)
        is_sync = True
    else:
        final_rows = list()
        schemas = {}
        is_sync = False

    return final_rows, schemas, is_sync


def sync_inventory_count(config, _custom_arguments, api):

    """ get the inventory current count api data in post method"""

    item_variant_id = get_item_variation_id_location_id(config)[0]
    json_count = {"catalog_object_ids": item_variant_id}
    url = config['host'] + api
    response = retrieve_api_json_data(config['access_token'], url, json_count)

    if bool(response):
        final_rows, schemas = clean_api_data(response)
        is_sync = True
    else:
        final_rows = list()
        schemas = {}
        is_sync = False

    return final_rows, schemas, is_sync


def sync_orders(config, _custom_arguments, api):

    """ get the orders api data in post method"""

    location_id = get_item_variation_id_location_id(config)[1]
    json_count = {"location_ids": location_id}
    url = config['host'] + api
    response = retrieve_api_json_data(config['access_token'], url, json_count)

    if bool(response):
        final_rows, schemas = clean_api_data(response)
        is_sync = True
    else:
        final_rows = list()
        schemas = {}
        is_sync = False

    return final_rows, schemas, is_sync


SYNC_FUNCTIONS = {
    'list_locations': sync_direct_api_get,
    'list_customers': sync_direct_api_get,
    'catalog_item': sync_direct_api_get,
    'catalog_category': sync_direct_api_get,
    'catalog_discount': sync_direct_api_get,
    'catalog_image': sync_direct_api_get,
    'catalog_item_variation': sync_direct_api_get,
    'catalog_modifier': sync_direct_api_get,
    'catalog_tax': sync_direct_api_get,
    'catalog_modifier_list': sync_direct_api_get,
    'list_employees': sync_direct_api_get,
    'customers_segments': sync_direct_api_get,
    'customer_groups': sync_direct_api_get,
    'merchants': sync_direct_api_get,
    'labor_break_types': sync_direct_api_get,
    'labor_employee_wages': sync_direct_api_get,
    'labor_shifts': sync_direct_api_post,
    'labor_workweek_configs': sync_direct_api_get,
    'retrieve_customer_segment': sync_retrieve_api_data,
    'retrieve_customer_group': sync_retrieve_api_data,
    'retrieve_labor_shifts': sync_retrieve_api_data,
    'retrieve_break_type': sync_retrieve_api_data,
    'retrieve_labor_employee_wages': sync_retrieve_api_data,
    'retrieve_merchants': sync_retrieve_api_data,
    'retrieve_location': sync_retrieve_api_data,
    'retrieve_customer': sync_retrieve_api_data,
    'retrieve_employee': sync_retrieve_api_data,
    'inventory_physical_count': sync_inventory_physical,
    'inventory_adjustment': sync_inventory_adjustment,
    'inventory_count': sync_inventory_count,
    'devices_codes': sync_direct_api_get,
    'retrieve_device_code': sync_retrieve_api_data,
    'terminals_checkouts': sync_direct_api_post,
    'retrieve_terminal_checkout': sync_retrieve_api_data,
    'list_disputes': sync_direct_api_get,
    'retrieve_disputes': sync_retrieve_api_data,
    'orders': sync_orders,
    'retrieve_payment': sync_retrieve_api_data,
    'retrieve_refund': sync_retrieve_api_data,
    'list_payments': sync_direct_api_get,
    'list_refunds': sync_direct_api_get
}


def discover():

    """Run discovery mode"""

    schemas, schemas_metadata = get_schemas()
    streams = []

    for schema_name, schema in schemas.items():
        schema_meta = schemas_metadata[schema_name]

        # create and add catalog entry
        catalog_entry = {
            'stream': schema_name,
            'tap_stream_id': schema_name,
            'schema': schema,
            'metadata': schema_meta
        }
        streams.append(catalog_entry)

    return {'streams': streams}


def sync(config, _state, catalog):

    """ Sync data from tap source """
    # Loop over selected streams in catalog
    for stream in catalog['streams']:

        if stream['schema'].get('selected', False):
            stream_id = stream['tap_stream_id']
            LOGGER.info("Syncing stream: %s", stream_id)
            custom_arguments = stream['schema']['custom_arguments']
            api = stream['schema']['api']
            sync_func = SYNC_FUNCTIONS[stream_id]
            final_rows, schemas, is_sync = sync_func(config, custom_arguments, api)

            if is_sync:
                singer_write(stream_id, final_rows, schemas)


@utils.handle_top_exception(LOGGER)
def main():

    """ main function """

    # Parse command line arguments
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)

    # If discover flag was passed, run discovery mode and dump output to stdout
    if args.discover:
        catalog = discover()
        print(json.dumps(catalog, indent=2))

    # Otherwise run in sync mode
    else:

        if args.properties:
            catalog = args.properties
        # 'catalog' is the current name
        elif args.catalog:
            catalog = args.catalog.to_dict()
        else:
            catalog = discover()

        state = args.state or {
            'bookmarks': {}
        }

        sync(args.config, state, catalog)


if __name__ == "__main__":
    main()
