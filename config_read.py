def get_mapping_from_file(filename='config.txt', controller_type=None, override=0):
    with open(filename) as f:
        content = f.readlines()

    content = [x.strip() for x in content if (x[0] != '#' and len(x.strip()))]
    
    
    if override:
        config_type = content[0].split('=')[1]

    elif not override and controller_type is not None: 
        config_type = controller_type

    else: 
        print('Could not load mappings: Please set valid controller type and override settings in config.txt')
        return None

    content = [x for x in content[1:] if config_type in x]
    print(content)

    mapping = {}
    for item in content:
        val, key = item.split('=')
        mapping[key.split('_')[1]] = val


    #print(mapping)
    return mapping

def get_controller_type(filename='config.txt'):
    # Get controller type from config file, NOT from Pygame's Joystick object
    with open(filename) as f:
        content = f.readlines()

    content = [x.strip() for x in content if (x[0] != '#' and len(x.strip()))]

    config_type = content[0].split('=')[1]

    return config_type

def get_override(filename='config.txt'):
    with open(filename) as f:
        content = f.readlines()

    content = [x.strip() for x in content if (x[0] != '#' and len(x.strip()))]
    override = int(content[1].split('=')[1])

    return override