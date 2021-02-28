"""A simple one-method library makes a GraphQL query from Python data structures."""
import json

class GqlFromStruct:
    """One and only module class"""
    def __init__(self, struct = None, minimize = False, force_quotes = 0) -> None:
        """Constructor"""
        self.object = None
        if (isinstance(struct, dict) and "@queries" not in struct.keys()
            and "@mutations" not in struct.keys()) or isinstance(struct, list):
            self.object = dict()
            self.object['@queries'] = list()
            self.object['@queries'].append({'@query':struct})
        elif isinstance(struct, dict) and (("@queries" in struct.keys())
                or "@mutations" in struct.keys()):
            self.object = struct
        if not(isinstance(self.object, dict) and ("@queries" in self.object.keys()
                                                  or "@mutations" in self.object.keys())):
            raise GqlFromStructException('A wrong structure was passed')
        self.spacing = '    '
        self.__minimize = minimize
        self.__force_quotes = force_quotes
        self.__force_quotes_args = False
        if self.__force_quotes == 2:
            self.__force_quotes_args = True
            self.__force_quotes = 0

    def query(self):
        """One and only class method"""
        result = []
        for query in self.object.get('@queries', list()):
            result.append(self.__operation_generate('query', query))
        for query in self.object.get('@mutations', list()):
            result.append(self.__operation_generate('mutation', query))
        for fragment in self.object.get('@fragments', list()):
            result.append(self.__fields_generate(fragment))
        if '@variables' in self.object.keys():
            result.append(json.dumps(self.object['@variables'],
                                     indent= None if self.__minimize else 4))
        if not self.__minimize:
            return self.__new_line().join(result)
        return ' '.join(result)

    @staticmethod
    def from_struct(struct = None, minimize = False, force_quotes = 0):
        """One and only static method"""
        if struct is None:
            raise GqlFromStructException('An empty structure was passed')
        gql = GqlFromStruct(struct, minimize, force_quotes)
        return gql.query()

    def __operation_generate(self, name, operation):
        name = self.__stringify_it(name) + ' ' + self.__stringify_it(operation['@operation_name']) if len(operation.get('@operation_name', '')) > 0 else self.__stringify_it(name)
        name = GString(name + ' ' + self.__args_generate(operation, 0)) if "@args" in operation.keys() else GString(name)
        return self.__fields_generate([{name: {'@fields': operation.get('@query', {})}}])

    def __fields_generate(self, query = None, depth = 0):
        if isinstance(query, dict):
            query = [query]
        array_field = []
        depth += 1
        for field in query:
            if isinstance(field, dict):
                array_field.append(self.__spacing(depth) + str(self.__fields_complex_generate(field, depth)))
            else:
                array_field.append(self.__spacing(depth) + self.__stringify_it(field))
        if not self.__minimize:
            return self.__new_line().join(array_field)
        return ' '.join(array_field)

    def __args_generate(self, field, depth):
        array_args = []
        for arg in field['@args']:
            if isinstance(field['@args'][arg], list):
                if self.__force_quotes_args:
                    self.__force_quotes = 1
                arg_values = self.__stringify_list(field['@args'][arg])
                if self.__force_quotes_args:
                    self.__force_quotes = 0
                array_args.append(self.__spacing(depth) + self.__stringify_it(arg) + self.__space() + ':[' + ', '.join(arg_values) + ']')
            elif isinstance(field['@args'][arg], dict):
                if len(field['@args'][arg]) > 1:
                    raise GqlFromStructException('Dict of arg %s must contain only one key-pair.' % arg)
                for key, value in field['@args'][arg].items():
                    array_args.append(self.__spacing(depth) +
                                      self.__no_stringify_arg(arg, str(key) +
                                                              self.__space() + "=" +
                                                              self.__space() + str(value)))
            else:
                if self.__force_quotes_args:
                    self.__force_quotes = 1
                array_args.append(self.__spacing(depth) + self.__stringify_arg(arg, field['@args'][arg]))
                if self.__force_quotes_args:
                    self.__force_quotes = 0
        if len(array_args) > 0:
            return '(' + self.__new_line() + (', ' + 
                                              self.__new_line()).join(array_args) + \
                   self.__new_line() + self.__spacing(depth) + ')'
        return ''

    def __fields_complex_generate(self, field, depth):
        array_field = ''
        if isinstance(field, dict):
            if len(field.keys()) > 1:
                raise GqlFromStructException('Field dict must contain only one key-pair.')
            if len(field.keys()) == 0:
                return ''
            field_name = list(field.keys())[0]

            if not isinstance(field[field_name], dict):
                raise GqlFromStructException('A value of the field "%s" must be a dict.' % field_name)
            depth += 1

            if '@args' in field[field_name].keys():
                array_field += self.__args_generate(field[field_name], depth)

            if '@directives' in field[field_name].keys() and  isinstance(field[field_name]['@directives'], dict):
                for directive in field[field_name]['@directives'].keys():
                    if directive not in ['@include', '@skip']:
                        raise GqlFromStructException("Directive of %s field must be @include or @skip" % field_name)
                    array_field += ' ' + directive + \
                                   self.__space() +'(if' + \
                                   self.__space() + ': '+ \
                                   self.__space() + field[field_name]['@directives'][directive] + ')'

            if '@fields' in field[field_name].keys():
                array_field +=  '{' + \
                                self.__new_line() + self.__fields_generate(field[field_name]['@fields'], depth) + \
                                self.__new_line() + self.__spacing(depth) + '}'

            if '@alias' in field[field_name].keys():
                field_name = field[field_name]['@alias'] + \
                             self.__space() + ":" + \
                             self.__space() + self.__stringify_it(field_name)

            elif '@fragment_name' in field[field_name].keys():
                field_name = 'fragment ' + field[field_name]['@fragment_name'] + " on " + self.__stringify_it(field_name)

            elif '@operation_name' in field[field_name].keys():
                field_name = self.__stringify_it(field[field_name]['@operation_name']) + " "

            array_field = self.__stringify_it(field_name) + array_field

        return array_field

    def __stringify_list(self, args):
        array_args=[]
        for arg in args:
            array_args.append(self.__stringify_it(arg))
        return array_args

    def __stringify_arg(self, arg, value):
        return arg + self.__space() + ":" + self.__space() + self.__stringify_it(value)

    def __no_stringify_arg(self,arg, value):
        return arg + self.__space() + ":" + self.__space() + value

    def __stringify_it(self, value):
        if isinstance(value, GString):
            return value
        if isinstance(value, str) and self.__force_quotes != 1:
            if value.find(' ') == -1 and self.__force_quotes != -1:
                return GString(value)
            elif value.find('"') == -1 and self.__force_quotes != -1:
                return GString('"' + value + '"')
            return GString(value)
        try:
            return GString(str(int(value)))
        except Exception:
            if self.__force_quotes == -1:
                return str(value)
            return GString('"' + str(value) + '"')

    def __spacing(self, depth):
        if not self.__minimize:
            return self.spacing * (depth-1)
        return ''

    def __space(self):
        if not self.__minimize:
            return ' '
        return ''

    def __new_line(self):
        if not self.__minimize:
            return '\n'
        return ''


class GString(str):
    def __add__(self, rhs):
        if isinstance(rhs, GString):
            return super().__add__(rhs)
        return super().__add__(GString(rhs))

    def __str__(self):
        return self


class GqlFromStructException(Exception):
    """Exception class"""
