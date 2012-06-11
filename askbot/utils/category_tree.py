"""This is temporary code to parse category
tree, stored in the settings.
The tree is plain text, with levels of branching 
reflected by indentation (2 spaces per level).
example of desired structure, when input is parsed

    cat_tree = [
        ['dummy', 
            [
                ['tires', [
                        ['michelin', [
                                ['trucks', []],
                                ['cars', []],
                                ['motorcycles', []]
                            ]
                        ],
                        ['good year', []],
                        ['honda', []],
                    ]
                ],
                ['abandonment', []],
                ['chile', []],
                ['vulcanization', []],
            ]
        ]
    ]
"""
from askbot.conf import settings as askbot_settings
from django.utils import simplejson

def _get_subtree(tree, path):
    clevel = tree
    for pace in path:
        clevel = clevel[1][pace]
    return clevel

def get_subtree(tree, path):
    """path always starts with 0,
    and is a list of integers"""
    assert(path[0] == 0)
    if len(path) == 1:#special case
        return tree[0]
    else:
        return _get_subtree(tree[0], path[1:])

def sort_tree(tree):
    """sorts contents of the nodes alphabetically"""
    tree = sorted(tree, lambda x,y: cmp(x[0], y[0]))
    for item in tree:
        item[1] = sort_tree(item[1])
    return tree

def get_data():
    """returns category tree data structure encoded as json
    or None, if category_tree is disabled
    """
    if askbot_settings.TAG_SOURCE == 'category-tree':
        return simplejson.loads(askbot_settings.CATEGORY_TREE)
    else:
        return None

def path_is_valid(tree, path):
    try:
        get_subtree(tree, path)
        return True
    except IndexError:
        return False
    except AssertionError:
        return False

def add_category(tree, category_name, path):
    subtree = get_subtree(tree, path)
    subtree[1].append([category_name, []])

def _has_category(tree, category_name):
    for item in tree:
        if item[0] == category_name:
            return True
        if _has_category(item[1], category_name):
            return True
    return False

def has_category(tree, category_name):
    """true if category is in tree"""
    #skip the dummy
    return _has_category(tree[0][1], category_name)

def save_data(tree):
    assert(askbot_settings.TAG_SOURCE == 'category-tree')
    tree = sort_tree(tree)
    tree_json = simplejson.dumps(tree)
    askbot_settings.update('CATEGORY_TREE', tree_json)