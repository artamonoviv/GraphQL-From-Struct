
import unittest

from graphql_from_struct import GqlFromStruct, GqlFromStructException


class TestGqlFromStruct(unittest.TestCase):

  def __start_test(self, query, force_quotes = 0):
    self.maxDiff = None
    gql = GqlFromStruct(query['q'], False, force_quotes)
    #self.assertEqual((GqlFromStruct.from_struct(query['q'])), query['a'])
    gql = GqlFromStruct(query['q'], True, force_quotes)
    print (gql.query())
    print ("\n\n")
    print (query['m'])
    self.assertEqual(gql.query(), query['m'])

  def test_exception_1(self):
    with self.assertRaises(GqlFromStructException) as context:
        GqlFromStruct.from_struct()
    self.assertTrue('An empty structure was passed' == str(context.exception))

  def test_exception_2(self):
    with self.assertRaises(GqlFromStructException) as context:
        GqlFromStruct.from_struct('foobar')
    self.assertTrue('A wrong structure was passed' == str(context.exception))

  def test_exception_3(self):
    with self.assertRaises(GqlFromStructException) as context:
        GqlFromStruct.from_struct({'human':{'@fields':['name', 'height'], '@args':{'$first': {'Int':'3', 'Boolean':'true'}}}})
    self.assertTrue('Dict of arg $first must contain only one key-pair.' == str(context.exception))

  def test_exception_4(self):
    with self.assertRaises(GqlFromStructException) as context:
        GqlFromStruct.from_struct({'human':{'@fields':['name', 'height']}, 'robot':{'@fields':['name', 'purpose']}})
    self.assertTrue('Field dict must contain only one key-pair.' == str(context.exception))

  def test_exception_5(self):
    with self.assertRaises(GqlFromStructException) as context:
        GqlFromStruct.from_struct({'human':['name', 'height']})
    self.assertTrue('A value of the field "human" must be a dict.' == str(context.exception))

  def test_exception_6(self):
    with self.assertRaises(GqlFromStructException) as context:
        GqlFromStruct.from_struct( {
              '@queries': [{'@operation_name': 'Hero',
                            '@query': {'hero': {'@args': {'episode': '$episode'},
                                                '@fields': ['name', {'friends': {
                                                    '@fields': ['name'],
                                                    '@directives': {'@import': '$withFriends'}
                                                }}]}}}],
              '@variables': {"episode": "JEDI"}
          })
    self.assertTrue("Directive of friends field must be @include or @skip" == str(context.exception))

  def test_quotes(self):
    query = {"q":{'hero':{'@fields':['name']}},
             "a":"""query{
        \"hero\"{
                \"name\"
            }
    }""",
             "m":"""\"query\"{\"hero\"{\"name\"}}"""}

    self.__start_test(query, 1)

  def test_quotes2(self):
    query = {"q":{'he ro':{'@fields':['name']}},
             "a":"""query{
        he ro{
                name
            }
    }""",
             "m":"""query{he ro{name}}"""}

    self.__start_test(query, -1)

  def test_quotes3(self):
    query = {"q": {'human':{'@fields':['name', 'height'], '@args':{'id':['foo', 'bar']}}},
             "a": """query{
        human(
            id : ["foo", "bar"]
            ){
                name
                height
            }
    }""",
             "m": """query{human(id:["foo", "bar"]){name height}}"""}

    self.__start_test(query,2)

  def test_quotes4(self):
    query = {"q": {'human':{'@fields':['name', 'height'], '@args':{'id':['foo', 'bar']}}},
             "a": """query{
        human(
            id : [foo, bar]
            ){
                name
                height
            }
    }""",
             "m": """query{human(id:[foo, bar]){name height}}"""}

    self.__start_test(query, -1)

  def test_quotes5(self):
    query = {"q": {'human':{'@fields':['name', 'height'], '@args':{'id':['foo', 'bar']}}},
             "a": """query{
        human(
            id : [foo, bar]
            ){
                name
                height
            }
    }""",
             "m": """query{human(id:[foo, bar]){name height}}"""}

    self.__start_test(query)

  def test_quotes6(self):
    query = {"q": {'human':{'@fields':['name', 'height'], '@args':{'id':["1", 'bar']}}},
             "a": """query{
        human(
            id : ["1", "bar"]
            ){
                name
                height
            }
    }""",
             "m": """query{human(id:["1", "bar"]){name height}}"""}

    self.__start_test(query, 2)

  def test_quotes7(self):
    query = {"q": {'human':{'@fields':['name', 'height'], '@args':{'id':[1, 'bar']}}},
             "a": """query{
        human(
            id : [1, "bar"]
            ){
                name
                height
            }
    }""",
             "m": """query{human(id:[1, "bar"]){name height}}"""}

    self.__start_test(query, 2)

  def test_fields(self):

    query = {"q":{'hero':{'@fields':['name']}},
             "a":"""query{
        hero{
                name
            }
    }""",
             "m":"""query{hero{name}}"""}

    self.__start_test(query)

  def test_fields2(self):

    query = {"q": {'hero':{'@fields':['name', {'friends':{'@fields':['name']}}]}},
             "a": """query{
        hero{
                name
                friends{
                        name
                    }
            }
    }""",
             "m": """query{hero{name friends{name}}}"""}

    self.__start_test(query)

  def test_args(self):
    query = {"q": {'human':{'@fields':['name', 'height'], '@args':{'id':'"1000"'}}},
             "a": """query{
        human(
            id : "1000"
            ){
                name
                height
            }
    }""",
             "m": """query{human(id:"1000"){name height}}"""}

    self.__start_test(query)

  def test_args2(self):
    query = {"q": {'human':{'@fields':['name', 'height'], '@args':{'$first': {'Int':'3'}}}},
             "a": """query{
        human(
            $first : Int = 3
            ){
                name
                height
            }
    }""",
             "m": """query{human($first:Int=3){name height}}"""}

    self.__start_test(query)

  def test_args3(self):
    query = {"q": {'human':{'@fields':['na me', {'height': {'@args':{'unit':'FOOT'}}}], '@args':{'id':"1000"}}},
             "a": """query{
        human(
            id : 1000
            ){
                "na me"
                height(
                    unit : FOOT
                    )
            }
    }""",
             "m": """query{human(id:1000){"na me" height(unit:FOOT)}}"""}

    self.__start_test(query)

  def test_aliases(self):
    query = {"q": [{'hero':{'@alias':'empireHero', '@args':{'episode':"EMPIRE"}, '@fields':['name']}}, {'hero':{'@alias':'jediHero', '@args':{'episode':"JEDI"}, '@fields':['name']}}],
             "a": """query{
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
    }""",
             "m": """query{empireHero:hero(episode:EMPIRE){name} jediHero:hero(episode:JEDI){name}}"""}

    self.__start_test(query)

  def test_fragments(self):
      query = {"q":
          {
              "@queries": [{'@query': [{'hero': {'@alias': 'leftComparison', '@args': {'episode': "EMPIRE"},
                                                 '@fields': ['...comparisonFields']}},
                                       {'hero': {'@alias': 'rightComparison', '@args': {'episode': "JEDI"},
                                                 '@fields': ['...comparisonFields']}}]}],
              "@fragments": [{'Character': {'@fragment_name': 'comparisonFields',
                                            '@fields': ['name', 'appearsIn', {'friends': {'@fields': ['name']}}]}}]
          }
          ,
          "a": """query{
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
    }""",
          "m": """query{leftComparison:hero(episode:EMPIRE){...comparisonFields} rightComparison:hero(episode:JEDI){...comparisonFields}} fragment comparisonFields on Character{name appearsIn friends{name}}"""}

      self.__start_test(query, -1)

  def test_operation_name(self):
      query = {"q":
                   {'@queries': [{'@operation_name': 'HeroNameAndFriends',
                                  '@query': {'hero': {'@fields': ['name', {'friends': {'@fields': ['name']}}]}}}]}
          ,
          "a": """query HeroNameAndFriends{
        hero{
                name
                friends{
                        name
                    }
            }
    }""",
          "m": """query HeroNameAndFriends{hero{name friends{name}}}"""}

      self.__start_test(query)

  def test_variables(self):
      query = {"q":
          {
              '@queries': [{'@operation_name': 'HeroNameAndFriends',
                            '@query': {'hero': {'@fields': ['name', {'friends': {'@fields': ['name']}}]}}}],
              '@variables': {"episode": "JEDI"}
          }
          ,
          "a": """query HeroNameAndFriends{
        hero{
                name
                friends{
                        name
                    }
            }
    }
{
    "episode": "JEDI"
}""",
          "m": """query HeroNameAndFriends{hero{name friends{name}}} {"episode": "JEDI"}"""}

      self.__start_test(query)

  def test_default_variables(self):
      query = {"q":
          {
              '@queries': [{'@operation_name': 'HeroNameAndFriends', '@args': {'$episode': {'Episode': 'JEDI'}},
                            '@query': {'hero': {'@fields': ['name', {'friends': {'@fields': ['name']}}]}}}],
              '@variables': {"episode": "JEDI"}
          }
          ,
          "a": """query HeroNameAndFriends (
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
}""",
          "m": """query HeroNameAndFriends ($episode:Episode=JEDI){hero{name friends{name}}} {"episode": "JEDI"}"""}

      self.__start_test(query)

  def test_directives(self):
      query = {"q":
          {
              '@queries': [{'@operation_name': 'Hero', '@args': {'$episode': 'Episode', '$withFriends': 'Boolean!'},
                            '@query': {'hero': {'@args': {'episode': '$episode'},
                                                '@fields': ['name', {'friends': {
                                                    '@fields': ['name'],
                                                    '@directives': {'@include': '$withFriends'}
                                                }}]}}}],
              '@variables': {"episode": "JEDI"}
          }
          ,
          "a": """query Hero (
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
}""",
          "m": """query Hero ($episode:Episode, $withFriends:Boolean!){hero(episode:$episode){name friends @include(if: $withFriends){name}}} {"episode": "JEDI"}"""}

      self.__start_test(query)

  def test_mutations(self):
      query = {"q":
          {
              '@mutations': [{'@operation_name': 'CreateReviewForEpisode',
                              '@args': {'$episode': 'Episode!', '$review': 'ReviewInput!'},
                              '@query': {'createReview': {'@args': {'episode': '$ep', 'review': '$review'},
                                                          '@fields': ['stars', 'commentary']}}}],
              '@variables': {"episode": "JEDI", "review": {
                  "stars": 5,
                  "commentary": "This is a great movie!"
              }}}
          ,
          "a": """mutation CreateReviewForEpisode (
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
}""",
          "m": """mutation CreateReviewForEpisode ($episode:Episode!, $review:ReviewInput!){createReview(episode:$ep, review:$review){stars commentary}} {"episode": "JEDI", "review": {"stars": 5, "commentary": "This is a great movie!"}}"""}

      self.__start_test(query)

  def test_inline_fragments(self):
      query = {"q":
          {
              "@queries": [{'@args': {'$ep': 'Episode!'}, '@operation_name': 'HeroForEpisode',
                            '@query': [{'hero': {'@args': {'episode': '$ep'},
                                                 '@fields': ['name',
                                                             {'... on Droid': {'@fields': ['primaryFunction']}},
                                                             {'... on Human': {'@fields': ['height']}}
                                                             ]}}]}]
          }
          ,
          "a": """query HeroForEpisode (
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
    }""",
          "m": """query HeroForEpisode ($ep:Episode!){hero(episode:$ep){name ... on Droid{primaryFunction} ... on Human{height}}}"""}

      self.__start_test(query, -1)

  def test_meta_fields(self):
      query = {"q":
                   {'search': {'@args': {'text': 'an'}, '@fields': ['__typename',
                                                                    {'... on Human': {'@fields': ['name']}},
                                                                    {'... on Droid': {'@fields': ['name']}},
                                                                    {'... on Starship': {'@fields': ['name']}}
                                                                    ]}}
          ,
          "a": """query{
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
    }""",
          "m": """query{search(text:an){__typename ... on Human{name} ... on Droid{name} ... on Starship{name}}}"""}

      self.__start_test(query, -1)

  def setUp(self):
    self.queries = list()


if __name__ == "__main__":
  unittest.main()