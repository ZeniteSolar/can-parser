#!/usr/bin/env python3
import json
import sys
import itertools
import pandas as pd


def parse_line(line):
    timestamp, interface, msg = line.split()
    timestamp = timestamp.strip('()')
    topic_id, payload = msg.split('#')
    topic_id = int(topic_id, 16)
    payload = [byte for byte in bytearray.fromhex(payload)]
    return {
        'timestamp': timestamp,
        'interfacee': interface,
        'topic_id': topic_id,
        'payload': payload
    }


def main():
    with open('can_ids.json') as schema_file:
        schema = json.load(schema_file)

    print(f'Loaded {len(schema["modules"])} modules:')
    for i, _ in enumerate(schema['modules']):
        print(
            f'\t{schema["modules"][i]["name"]}({schema["modules"][i]["signature"]})')
    print('')

    parsed_dataset = []
    parsed_dict = {}

    with open('test_big.log') as candump_file:
        for line_number, line in enumerate(candump_file):
            try:
                parsed = parse_line(line)
                # print(parsed)

                parsed_timestamp = parsed['timestamp']
                parsed_signature = parsed['payload'][0]
                parsed_payload = parsed['payload'][1:]

                for module in schema['modules']:
                    if module['signature'] == parsed_signature:
                        parsed_module_name = module['name']
                        parsed_module_description = module['description']
                        for topic in module['topics']:
                            parsed_topic_id = parsed['topic_id']
                            if topic['id'] == parsed_topic_id:
                                parsed_topic_name = topic['name']
                                for b, byte in enumerate(topic['bytes'][1:]):
                                    if byte != None:
                                        try:
                                            parsed_byte_type = byte['type']
                                            parsed_byte_units = byte['units']
                                            parsed_byte_name = byte['name']

                                            if parsed_byte_type == 'u8':
                                                parsed_byte_data = parsed_payload[b]
                                            elif parsed_byte_type == 'u16':
                                                if parsed_byte_name[-2:] == '_H':
                                                    continue
                                                parsed_byte_name = parsed_byte_name[:-2]
                                                parsed_byte_data = (
                                                    parsed_payload[b]) + (parsed_payload[b + 1] * 256)
                                            elif parsed_byte_type == 'bitfield':
                                                for parsed_bit, parsed_bit_name in enumerate(byte['bits']):
                                                    if parsed_bit_name != None:
                                                        parsed_byte_data = (
                                                            parsed_payload[b] >> parsed_bit) & 1

                                                        parsed_dict = {
                                                            "timestamp": parsed_timestamp,
                                                            "module_name": parsed_module_name,
                                                            "topic_name": parsed_topic_name,
                                                            "byte_name": parsed_byte_name + parsed_bit_name,
                                                            "data": parsed_byte_data,
                                                            "unit": ''
                                                        }
                                                        parsed_dataset += [
                                                            parsed_dict]

                                            if parsed_byte_units == '%':
                                                parsed_byte_scale = 1 / 255
                                                parsed_byte_data *= parsed_byte_scale

                                                parsed_dict = {
                                                    "timestamp": parsed_timestamp,
                                                    "module_name": parsed_module_name,
                                                    "topic_name": parsed_topic_name,
                                                    "byte_name": parsed_byte_name,
                                                    "data": parsed_byte_data,
                                                    "unit": parsed_byte_units
                                                }
                                                parsed_dataset += [parsed_dict]
                                            else:
                                                if parsed_byte_units != '':
                                                    parsed_byte_units = ["".join(x) for _, x in itertools.groupby(
                                                        parsed_byte_units, key=str.isdigit)]
                                                    parsed_byte_scale = 1 / \
                                                        float(
                                                            parsed_byte_units[1])
                                                    parsed_byte_units = parsed_byte_units[0].replace(
                                                        '/', '')
                                                    parsed_byte_data *= parsed_byte_scale

                                                parsed_dict = {
                                                    "timestamp": parsed_timestamp,
                                                    "module_name": parsed_module_name,
                                                    "topic_name": parsed_topic_name,
                                                    "byte_name": parsed_byte_name,
                                                    "data": parsed_byte_data,
                                                    "unit": parsed_byte_units
                                                }
                                                parsed_dataset += [parsed_dict]
                                        except Exception as e:
                                            # sys.stderr.write(f'Failed to parse:\n {parsed}\n \t\t-> %{e}\n')
                                            pass

            except Exception as e:
                sys.stderr.write('Failed to parse input file line %d: %s\n' % (
                    line_number + 1, str(e)))
                sys.exit(1)

    df = pd.DataFrame(parsed_dataset)
    df.to_csv(r'parsed.csv', index=False)
    print(df.tail())


if __name__ == '__main__':
    main()
