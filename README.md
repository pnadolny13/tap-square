#tap-square
This is a [Singer](https://singer.io) tap that reads data from Square API's and produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

## How to use it
[Singer](https://www.singer.io/) tap that extracts data from a [square](https://developer.squareup.com/us/en) and produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md).


### Install

```bash
$ mkvirtualenv -p python3 tap-square
$ pip install tap-square
```

### Configuration
Here is an example of basic config file containing the suare connection credentials,e.g.:

```
{
  "host":"https://connect.squareup.com/",
  "access_token": "EAAAECSSMwBOsBidYdffsghjjjjS"
}
```


- **host**:This is suare host name.
- **access_token**:This is the square access_token which is uinque for each and every account.

### Discovery mode

The tap can be invoked in discovery mode to find the available API's and
schema of the respective square API data:

```bash
$ tap-square --config config.json --discover

```
A discovered catalog is output, with a JSON-schema description of each API's.

```json
        {
      "stream": "list_employees",
      "tap_stream_id": "list_employees",
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "custom_arguments": {},
        "selected": true,
        "api": "v2/employees",
        "properties": {
          "employees": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "id": {
                  "type": "string"
                },...
              "required": [
                "created_at",
                "email",
                "id",
                "is_owner",
                "location_ids",
                "status",
                "updated_at"
              ]
            }
          }
        },
        "required": [
          "employees"
        ]
      },
      "metadata": [
        {
          "breadcrumb": [],
          "metadata": {
            "table-key-properties": [
              "id"
            ],
            "forced-replication-method": "INCREMENTAL",
            "valid-replication-keys": [
              "date_modified"
            ],
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "employees"
          ],
          "metadata": {
            "inclusion": "available"
          }
        }
      ],
      "key_properties": [
        "id"
      ]
    },
	{
      "stream": "retrieve_employee",
      "tap_stream_id": "retrieve_employee",
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "custom_arguments": {
          "id": []
        },
        "selected": false,
        "api": "v2/employees/{id}",
        "properties": {
          "employee": {
            "type": "object",
            "properties": {
              "id": {
                "type": "string"
              },
              "location_ids": {
                "type": "array",
                "items": {
                  "type": "string"
                },
            "required": [
              "created_at",
              "email",
              "id",
              "is_owner",
              "location_ids",
              "status",
              "updated_at"
            ]
          }
        },
        "required": [
          "employee"
        ]
      },
      "metadata": [
        {
          "breadcrumb": [],
          "metadata": {
            "table-key-properties": [
              "id"
            ],
            "forced-replication-method": "INCREMENTAL",
            "valid-replication-keys": [
              "date_modified"
            ],
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "employee"
          ],
          "metadata": {
            "inclusion": "available"
          }
        }
      ],
      "key_properties": [
        "id"
      ]
    },
```
	
### Property file Creation

In API selection, `tap-square` consumes the property and looks for API's and fields
have been marked as _selected_ in their associated metadata entries.

Redirect output from the tap's discovery mode to a properties file so that it can be
modified

```bash
$ tap-square --config config.json --discover > properties.json
```

Then edit `properties.json` to make selections. In this example we want the
`list_employees` API & `retrieve_employee`, The list_employee does not need any patameater,
But the retrieve_employee `custom_arguments` need to be passed to get the desired output. 

```json
        {
      "stream": "list_employees",
      "tap_stream_id": "list_employees",
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "custom_arguments": {},
        "selected": true,
        "api": "v2/employees",
        "properties": {
          "employees": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "id": {
                  "type": "string"
                },
                "location_ids": {
                  "type": "array",
                  "items": {
                    "type": "string"
                  }
                },
              "required": [
                "created_at",
                "email",
                "id",
                "is_owner",
                "location_ids",
                "status",
                "updated_at"
              ]
            }
          }
        },
        "required": [
          "employees"
        ]
      },
      "metadata": [
        {
          "breadcrumb": [],
          "metadata": {
            "table-key-properties": [
              "id"
            ],
            "forced-replication-method": "INCREMENTAL",
            "valid-replication-keys": [
              "date_modified"
            ],
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "employees"
          ],
          "metadata": {
            "inclusion": "available"
          }
        }
      ],
      "key_properties": [
        "id"
      ]
    },
      "stream": "retrieve_employee",
      "tap_stream_id": "retrieve_employee",
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "custom_arguments": {
          "id": ["XCPRM0XZNM4QK"]
        },
        "selected": true,
        "api": "v2/employees/{id}",
        "properties": {
          "employee": {
            "type": "object",
            "properties": {
              "id": {
                "type": "string"
              },
              "location_ids": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              },...
            "required": [
              "created_at",
              "email",
              "id",
              "is_owner",
              "location_ids",
              "status",
              "updated_at"
            ]
          }
        },
        "required": [
          "employee"
        ]
      },
      "metadata": [
        {
          "breadcrumb": [],
          "metadata": {
            "table-key-properties": [
              "id"
            ],
            "forced-replication-method": "INCREMENTAL",
            "valid-replication-keys": [
              "date_modified"
            ],
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "employee"
          ],
          "metadata": {
            "inclusion": "available"
          }
        }
      ],
      "key_properties": [
        "id"
      ]
    },
```
### API's Selection on properties.jon file

In properties file mark the required API as ` "selected": true` to retrive the specific API data.
If we mark ` "selected": false` then that API will not return data. 
Some of the API need to be  marked as ` "selected": true` and pass the parameater `custom_arguments` which is mandatary filed to fetch
the data corespondding to that ID.We can pass multiple `custom_arguments` in the list as mensioned.

```
	{
      "stream": "retrieve_employee",
      "tap_stream_id": "retrieve_employee",
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "custom_arguments": {
          "id": ["XCPRM0XZNM4QK","XCGUJD13HUBDHO"]
        },
        "selected": true,
        "api": "v2/employees/{id}",
        "properties": {
          "employee": {
            "type": "object",
            "properties": {
              "id": {
                "type": "string"
              }
```

### How to run singer tap with property file.

With a properties catalog that describes field and API selections the tap can be invoked:

```bash
$ tap-square --config config.json --properties properties.json
```

Messages are written to standard output following the Singer specification. The
resultant stream of JSON data can be consumed by a Singer target.



### How to run the singer tap with target


```bash
$ tap-square --config config.json --properties properties.json | target -stich --config config.json
```

We can choose any of the singer target ,according to singer target specification we want to give the connection details in the config file.

### List of Square API"s

List of square API is is available inside [square_API_list.xlsx](square_API_list.xlsx)

