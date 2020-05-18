
""" Handles the schema for the APIs """

import os
import json
from singer import metadata

STREAMS = {
    'catalog_category': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    },
    'catalog_discount': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    },
    'catalog_image': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    },
    'catalog_item': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    },
    'catalog_item_variation': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    },
    'catalog_modifier': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    },
    'catalog_modifier_list': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    },
    'catalog_tax': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    },
    'customer_groups': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    },
    'customers_segments': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    },
    'labor_break_types': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['id']
    },
    'labor_employee_wages': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['id']
    },
    'labor_shifts': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    },
    'labor_workweek_configs': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    },
    'list_customers': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    },
    'list_employees': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    },
    'list_locations': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['id']
    },
    'merchants': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['id']
    },
    'retrieve_break_type': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    },
    'retrieve_customer': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    },
    'retrieve_customer_group': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    },
    'retrieve_customer_segment': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    },
    'retrieve_employee': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['id']
    },
    'retrieve_labor_employee_wages': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['id']
    },
    'retrieve_labor_shifts': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['date_modified']
    },
    'retrieve_location': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['id']
    },
    'retrieve_merchants': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['id']
    },
    'inventory_physical_count': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['id']
    },
    'inventory_adjustment': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['id']
    },
    'inventory_count': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['catalog_object_id']
    },
    'devices_codes': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['id']
    },
    'retrieve_device_code': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['id']
    },
    'terminals_checkouts': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['id']
    },
    'retrieve_terminal_checkout': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['id']
    },
    'list_disputes': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['dispute_id']
    },
    'retrieve_disputes': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['dispute_id']
    },
    'orders': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['id']
    },
    'list_payments': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    },
    'list_refunds': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    },
    'retrieve_payment': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    },
    'retrieve_refund': {
        'replication_method': 'FULL_TABLE',
        'replication_keys': ['updated_at']
    }
}


def get_abs_path(path):
    """ returns the file path"""
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def get_schemas():

    """ Reads the schemas for all the apis and returns stream sets """

    schemas = {}
    schemas_metadata = {}

    for stream_name, stream_metadata in STREAMS.items():

        schema_path = get_abs_path('schemas/{}.json'.format(stream_name))
        with open(schema_path) as file:
            schema = json.load(file)
        meta = metadata.get_standard_metadata(
            schema=schema,
            valid_replication_keys=stream_metadata.get('replication_keys', None),
            replication_method=stream_metadata.get('replication_method', None)
        )
        schemas[stream_name] = schema
        schemas_metadata[stream_name] = meta

    return schemas, schemas_metadata
