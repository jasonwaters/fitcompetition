import operator


def attr(obj, key, defaultValue=None):
    if obj is None:
        return defaultValue
    elif type(obj) is dict:
        try:
            if obj[key] is None:
                return defaultValue
            else:
                return obj[key]
        except KeyError:
            return defaultValue
    else:
        return getattr(obj, key, defaultValue)


def groupBy(list, dictKeyName):
    list = sorted(list, key=lambda k: attr(k, dictKeyName))

    grouped = {}
    lastGroup = None

    for item in list:
        group = attr(item, dictKeyName)
        if group != lastGroup:
            grouped[group] = []

        lastGroup = group
        grouped[group].append(item)

    return grouped


def multikeysort(items, columns, getter=operator.itemgetter):
    """Sort a list of dictionary objects or objects by multiple keys bidirectionally.
    https://gist.github.com/malero/418204

    Keyword Arguments:
    items -- A list of dictionary objects or objects
    columns -- A list of column names to sort by. Use -column to sort in descending order
    getter -- Default "getter" if column function does not exist
              operator.itemgetter for Dictionaries
              operator.attrgetter for Objects
    """
    comparers = []
    for col in columns:

        if col.startswith('-'):
            comparers.append((getter(col[1:].strip()), -1))
        else:
            comparers.append((getter(col.strip()), 1))

    def comparer(left, right):
        for func, polarity in comparers:
            result = cmp(func(left), func(right))
            if result:
                return polarity * result
        else:
            return 0

    return sorted(items, cmp=comparer)


def createListFromProperty(list, propertyName):
    hash = {}
    result = []

    for item in list:
        value = getattr(item, propertyName)
        if value not in hash:
            hash[value] = True
            result.append(value)

    return result


def mappify(list, propertyToUseAsKey):
    map = {}
    for item in list:
        value = getattr(item, propertyToUseAsKey)
        map[value] = item

    return map


def wrapThem(list, clazz):
    newList = []
    for item in list:
        newList.append(clazz(item))
    return newList