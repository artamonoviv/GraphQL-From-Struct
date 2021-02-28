|License| |Release| |Docs| |Code Coverage| |Build Status Travis CI| |Blog|

GraphQL-From-Struct
===================

A simple one-method library makes a `GraphQL <https://graphql.org/>`__
query from Python data structures.

Table of Contents
-----------------

1. `Installation`_
2. `Usage`_
3. `Exceptions`_
4. `Parameters`_
5. `Reserved keywords`_
6. `Examples`_

-  `Fields`_
-  `Arguments`_
-  `Default arguments`_
-  `Aliases`_
-  `Fragments`_
-  `Using variables inside fragments`_
-  `Operation name`_
-  `Variables`_
-  `Default variables`_
-  `Directives`_
-  `Mutations`_
-  `Inline Fragments`_
-  `Meta fields`_

Installation 
-------------

::

    pip install graphql_from_struct 

Usage 
------

::

    # 1. Import GqlFromStruct class

    from graphql_from_struct import GqlFromStruct

    # 2. Make a query 

    struct = {'hero':{'@fields':['name']}}

    # 3. Generate GraphQL

    gql = GqlFromStruct.from_struct(struct)

    # Or use OOP-style:

    foo = GqlFromStruct(struct)

    gql = foo.query()

    print (gql)

You should see such result:

::

    query{
            hero{
                    name
                }
        }

Exceptions 
----------

The module raises ``GqlFromStructException`` in case of empty or wrong
data structure input.

Parameters
----------

``GqlFromStruct()`` constructor and ``.from_struct()`` method take 3 arguments:
a **struct** (default None), a **minimize** (optional, default False) flag and a **force_quotes** (optional, default 0) setting.
Code:

::

    foo = GqlFromStruct({'hero':{'@fields':['name']}}, True)

    # or foo = GqlFromStruct(struct = {'hero':{'@fields':['name']}}, minimize = True) 

    gql = foo.query()

    # or 

    gql = GqlFromStruct.from_struct({'hero':{'@fields':['name']}}, True)

    print (gql)

gives you:

::

    query{hero{name}}

By default the GraphQL-From-Struct sets quotes for any string with spaces. You can change it with the **force_quotes** flag.  It enforces quoting parameters and arguments with 1 value, disables any quotes with -1 or enables only arguments quoting with 2:

::

    gql = GqlFromStruct.from_struct({'hero':{'@fields':['name']}}, True, 1)

    print (gql)

gives you:

::

    "query"{"hero"{"name"}}

Or

::

    gql = GqlFromStruct.from_struct({'he ro':{'@fields':['name']}}, True, -1)

    print (gql)

gives you:

::

    query{he ro{name}}

Or

::

    gql = GqlFromStruct.from_struct('human':{'@fields':['name', 'height'], '@args':{'id':['foo', 'bar']}}, True, 2)

    print (gql)

gives you:

::

    query{human(id:["foo", "bar"]){name height}}

Reserved keywords 
------------------

Words
``@alias, @args, @fields, @fragments, @fragment_name, @directives, @include, @mutations, @operation_name, @queries, @query, @skip, @variables``
are reserved and used for query constructing.

Examples 
---------

Examples are shown in the same order as in the
`GraphQL <https://graphql.org/learn/queries/>`__ documentation.

Fields
~~~~~~

Use ``@fields`` keyword:

::

    struct = {'hero':{'@fields':['name']}}

    print (GqlFromStruct.from_struct(struct))

Output:

::

    query{
            hero{
                    name
                }
        }

You can use arbitrary field nesting:

::

    struct = {'hero':{'@fields':['name', {'friends':{'@fields':['name']}}]}}

    print (GqlFromStruct.from_struct(struct))

Output:

::

    query{
            hero{
                    name
                    friends{
                            name
                        }
                }
        }

Arguments 
~~~~~~~~~~

Use ``@args`` keyword:

::

    struct = {'human':{'@fields':['name', 'height'], '@args':{'id':'"1000"'}}}

    print (GqlFromStruct.from_struct(struct))

Output:

::

    query{
            human(
                id : "1000"
                ){
                    name
                    height
                }
        }

or:

::

    struct = {
      'human': {
        '@fields': ['name', {
          'height': {
            '@args': {
              'unit': 'FOOT'
            }
          }
        }],
        '@args': {
          'id': "1000"
        }
      }
    }

    print (GqlFromStruct.from_struct(struct))

Output:

::

    query{
            human(
                id : 1000
                ){
                    name
                    height(
                        unit : FOOT
                        )
                }
        }

Note: GraphQL-From-Struct puts double quotes by default only for values
with spaces. Like that:

::

    query = {'human':{'@fields':['name', 'height'], '@args':{'id':'1000 meters'}}}

Output:

::

    query{
            human(
                id : "1000 meters"
                ){
                    name
                    height
                }
        }

Single words or numerical values are output in the form in which you
passed them.

::

    query = {'human':{'@fields':['name', 'height'], '@args':{'id':1000}}}
    query{
            human(
                id : 1000
                ){
                    name
                    height
                }
        }

Default arguments 
^^^^^^^^^^^^^^^^^^

You can set default values of arguments:

::

    struct = {'human':{'@fields':['name', 'height'], '@args':{'$first': {'Int':'3'}}}

    print (GqlFromStruct.from_struct(struct))

Output:

::

    query{
            human(
                $first : Int = 3
                ){
                    name
                    height
                }
        }

Aliases 
~~~~~~~~

Use ``@alias`` keyword:

::

    struct = [{
      'hero': {
        '@alias': 'empireHero',
        '@args': {
          'episode': "EMPIRE"
        },
        '@fields': ['name']
      }
    }, {
      'hero': {
        '@alias': 'jediHero',
        '@args': {
          'episode': "JEDI"
        },
        '@fields': ['name']
      }
    }]

    print (GqlFromStruct.from_struct(struct))

Output:

::

    query{
            empireHero : hero(
                episode : EMPIRE
                ){
                    name
                }
            jediHero : hero(
                episode : JEDI
                ){
                    name
                }
        }

Fragments 
~~~~~~~~~~

Use ``@fragments`` and ``@fragment_name`` keywords for fragments setting
up. Use ``@query`` and ``@queries`` for join some queries into one.

::

    struct = {
                "@queries": [{
                  '@query': [{
                      'hero': {
                        '@alias': 'leftComparison',
                        '@args': {
                          'episode': "EMPIRE"
                        },
                        '@fields': ['...comparisonFields']
                      }
                    },
                    {
                      'hero': {
                        '@alias': 'rightComparison',
                        '@args': {
                          'episode': "JEDI"
                        },
                        '@fields': ['...comparisonFields']
                      }
                    }
                  ]
                }],
                "@fragments": [{
                  'Character': {
                    '@fragment_name': 'comparisonFields',
                    '@fields': ['name', 'appearsIn', {
                      'friends': {
                        '@fields': ['name']
                      }
                    }]
                  }
                }]
              }

    print (GqlFromStruct.from_struct(struct))

Output:

::

    query{
            leftComparison : hero(
                episode : EMPIRE
                ){
                    ...comparisonFields
                }
            rightComparison : hero(
                episode : JEDI
                ){
                    ...comparisonFields
                }
        }
    fragment comparisonFields on Character{
            name
            appearsIn
            friends{
                    name
                }
        }

Using variables inside fragments 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    struct = {
      "@queries": [{
        '@args': {
          '$first': {
            'Int': '3'
          }
        },
        '@operation_name': 'HeroComparison',
        '@query': [{
            'hero': {
              '@alias': 'leftComparison',
              '@args': {
                'episode': "EMPIRE"
              },
              '@fields': ['...comparisonFields']
            }
          },
          {
            'hero': {
              '@alias': 'rightComparison',
              '@args': {
                'episode': "JEDI"
              },
              '@fields': ['...comparisonFields']
            }
          }
        ]
      }],
      "@fragments": [{
        'Character': {
          '@fragment_name': 'comparisonFields',
          '@fields': ['name', {
            'friendsConnection': {
              '@args': {
                'first': '$first'
              },
              '@fields': ['totalCount', {
                'edges': {
                  '@fields': [{
                    'node': {
                      '@fields': ['name']
                    }
                  }]
                }
              }]
            }
          }]
        }
      }]
    }

    print (GqlFromStruct.from_struct(struct))

Output:

::

    query HeroComparison (
    $first : Int = 3
    ){
            leftComparison : hero(
                episode : EMPIRE
                ){
                    ...comparisonFields
                }
            rightComparison : hero(
                episode : JEDI
                ){
                    ...comparisonFields
                }
        }
    fragment comparisonFields on Character{
            name
            friendsConnection(
                first : $first
                ){
                    totalCount
                    edges{
                            node{
                                    name
                                }
                        }
                }
        }

Operation name 
~~~~~~~~~~~~~~~

Use ``@operation_name`` keyword:

::

    struct =  {
       '@queries': [{
         '@operation_name': 'HeroNameAndFriends',
         '@query': {
           'hero': {
             '@fields': ['name', {
               'friends': {
                 '@fields': ['name']
               }
             }]
           }
         }
       }]
     }

    print (GqlFromStruct.from_struct(struct))

Output:

::

    query HeroNameAndFriends{
            hero{
                    name
                    friends{
                            name
                        }
                }
        }

Variables 
~~~~~~~~~~

Use ``@variables`` block at the same high level nesting as ``@queries``:

::

    struct = {
                '@queries': [{
                  '@operation_name': 'HeroNameAndFriends',
                  '@query': {
                    'hero': {
                      '@fields': ['name', {
                        'friends': {
                          '@fields': ['name']
                        }
                      }]
                    }
                  }
                }],
                '@variables': {
                  "episode": "JEDI"
                }
              }

    print (GqlFromStruct.from_struct(struct))

Output:

::

    query HeroNameAndFriends{
            hero{
                    name
                    friends{
                            name
                        }
                }
        }
    {
        "episode": "JEDI"
    }

Default variables 
^^^^^^^^^^^^^^^^^^

Use ``@fields`` keyword:

::

    struct =  {
                '@queries': [{
                  '@operation_name': 'HeroNameAndFriends',
                  '@args': {
                    '$episode': {
                      'Episode': 'JEDI'
                    }
                  },
                  '@query': {
                    'hero': {
                      '@fields': ['name', {
                        'friends': {
                          '@fields': ['name']
                        }
                      }]
                    }
                  }
                }],
                '@variables': {
                  "episode": "JEDI"
                }
              }

    print (GqlFromStruct.from_struct(struct))

Output:

::

    query HeroNameAndFriends (
    $episode : Episode = JEDI
    ){
            hero{
                    name
                    friends{
                            name
                        }
                }
        }
    {
        "episode": "JEDI"
    }

Directives 
~~~~~~~~~~~

Use ``@directives`` keyword and ``@skip`` or ``@include`` as directives:

::

    struct = {
      '@queries': [{
        '@operation_name': 'Hero',
        '@args': {
          '$episode': 'Episode',
          '$withFriends': 'Boolean!'
        },
        '@query': {
          'hero': {
            '@args': {
              'episode': '$episode'
            },
            '@fields': ['name', {
              'friends': {
                '@fields': ['name'],
                '@directives': {
                  '@include': '$withFriends'
                }
              }
            }]
          }
        }
      }],
      '@variables': {
        "episode": "JEDI"
      }
    }

    print (GqlFromStruct.from_struct(struct))

Output:

::

    query Hero (
    $episode : Episode, 
    $withFriends : Boolean!
    ){
            hero(
                episode : $episode
                ){
                    name
                    friends @include (if :  $withFriends){
                            name
                        }
                }
        }
    {
        "episode": "JEDI"
    }

Mutations 
~~~~~~~~~~

Use ``@mutations`` keyword:

::

    struct = {
      '@mutations': [{
        '@operation_name': 'CreateReviewForEpisode',
        '@args': {
          '$episode': 'Episode!',
          '$review': 'ReviewInput!'
        },
        '@query': {
          'createReview': {
            '@args': {
              'episode': '$ep',
              'review': '$review'
            },
            '@fields': ['stars', 'commentary']
          }
        }
      }],
      '@variables': {
        "episode": "JEDI",
        "review": {
          "stars": 5,
          "commentary": "This is a great movie!"
        }
      }
    }

    print (GqlFromStruct.from_struct(struct))

Output:

::

    mutation CreateReviewForEpisode (
    $episode : Episode!, 
    $review : ReviewInput!
    ){
            createReview(
                episode : $ep, 
                review : $review
                ){
                    stars
                    commentary
                }
        }
    {
        "episode": "JEDI",
        "review": {
            "stars": 5,
            "commentary": "This is a great movie!"
        }
    }

Inline Fragments 
~~~~~~~~~~~~~~~~~

Nothing special needed.

::

    struct =  {
       "@queries": [{
         '@args': {
           '$ep': 'Episode!'
         },
         '@operation_name': 'HeroForEpisode',
         '@query': [{
           'hero': {
             '@args': {
               'episode': '$ep'
             },
             '@fields': ['name',
               {
                 '... on Droid': {
                   '@fields': ['primaryFunction']
                 }
               },
               {
                 '... on Human': {
                   '@fields': ['height']
                 }
               }
             ]
           }
         }]
       }]
     }

    print (GqlFromStruct.from_struct(struct))

Output:

::

    query HeroForEpisode (
    $ep : Episode!
    ){
            hero(
                episode : $ep
                ){
                    name
                    ... on Droid{
                            primaryFunction
                        }
                    ... on Human{
                            height
                        }
                }
        }

Meta fields 
~~~~~~~~~~~~

Use meta field as usual field:

::

    struct = {
      'search': {
        '@args': {
          'text': 'an'
        },
        '@fields': ['__typename',
          {
            '... on Human': {
              '@fields': ['name']
            }
          },
          {
            '... on Droid': {
              '@fields': ['name']
            }
          },
          {
            '... on Starship': {
              '@fields': ['name']
            }
          }
        ]
      }
    }

    print (GqlFromStruct.from_struct(struct))

Output:

::

    query{
            search(
                text : an
                ){
                    __typename
                    ... on Human{
                            name
                        }
                    ... on Droid{
                            name
                        }
                    ... on Starship{
                            name
                        }
                }
        }


.. |Release| image:: https://img.shields.io/github/v/release/artamonoviv/graphql-from-struct.svg
   :target: https://github.com/artamonoviv/graphql-from-struct/releases
.. |Code Coverage| image:: https://codecov.io/gh/artamonoviv/graphql-from-struct/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/artamonoviv/graphql-from-struct
.. |Build Status Travis CI| image:: https://travis-ci.org/artamonoviv/graphql-from-struct.svg?branch=master
    :target: https://travis-ci.org/artamonoviv/graphql-from-struct
.. |Blog| image:: https://img.shields.io/badge/site-my%20blog-yellow.svg
    :target:  https://artamonoviv.ru
.. |License| image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target:  https://opensource.org/licenses/MIT
.. |Docs| image:: https://readthedocs.org/projects/graphql-from-struct/badge/?version=latest&style=flat
    :target:  https://graphql-from-struct.readthedocs.io/en/latest/