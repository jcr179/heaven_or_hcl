def get_mapping_from_file(filename='config.txt'):
    with open(filename) as f:
        content = f.readlines()

    content = [x.strip() for x in content if (x[0] != '#' and len(x.strip()))]

    config_type = content[0].split('=')[1]
    #print(config_type)

    content = [x for x in content[1:] if config_type in x]
    #print(content)

    mapping = {}
    for item in content:
        val, key = item.split('=')
        mapping[key.split('_')[1]] = val


    #print(mapping)
    return mapping