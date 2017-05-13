import collections as c
import yaml

def represent_ordereddict(dumper, data):
    """
    Generate a YAML representation of an OrderedDict that looks exactly
    like an ordinary YAML table. The default OrderedDict representation
    is a sequence of nested lists, which is pretty hard to work with
    in a text editor.
    """
    # Cribbed wholesale from http://stackoverflow.com/a/16782282
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)

def dumper(stream):
    """
    Configures a yaml.Dumper for the target stream, using defaults
    appropriate for the land registry metadata. These include:

    * default_flow_style=False. Avoid using {} syntax in YAML files.
    * explicit_start=True. Always output the leading --- preamble.
    * serialize OrderedDict objects as YAML tables, transparently.
    """
    dumper = yaml.Dumper(
        stream,
        default_flow_style=False,
        explicit_start=True,
    )
    dumper.add_representer(c.OrderedDict, represent_ordereddict)
    return dumper

def dump_all(documents, stream):
    """
    Dump a sequence of documents to stream, as YAML. This uses the
    Dumper defined by the dumper() function in this module.
    """
    d = dumper(stream)
    try:
        d.open()
        for data in documents:
            d.represent(data)
        d.close()
    finally:
        d.dispose()

def dump(document, stream):
    """
    Dump a single document to a stream, as YAML. This uses the Dumper
    defined by the dumper() function in this module.
    """
    return dump_all([document], stream)
