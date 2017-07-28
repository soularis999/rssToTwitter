def encode(section_name):
    """
    Given the section name the method is "standardizing" the name for consistent lookup and use
    :param section_name:
    :return:
    """
    section_name = section_name.strip().upper() if section_name else None
    return section_name if section_name else None
