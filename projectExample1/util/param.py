import web


def __str_valueof(s, restrict=''):
    """
    usage:
    s : no restrict
    s(10) : string which length <= 10
    s(7-11) : string which length >= 7 and length <= 10
    """
    if not restrict:
        return s, None
    p, q = restrict.split('-', 2) if '-' in restrict else ('0', restrict)
    start_num = web.intget(p, '-1')
    range_to_num = web.intget(q, '-1')
    if start_num < 0 or range_to_num < 0:
        return None, {"code": 1, "message": "inner setting error"}
    if len(s) > range_to_num:
        return None, {"code": 1, "message": "too long"}
    if len(s) < start_num:
        return None, {"code": 1, "message": "too short"}
    return s, None


REFLECT_URL_MAP = {'s': __str_valueof}


def set_valueof(type_name, valueof_func):
    """
    usage:
    def postv_int_valueof(s):
        n = web.intget(s, 0)
        return (n, None) if n > 0 else (None, {"code": 1, "message": "wrong format"})

    param.set_valueof("n", postv_int_valueof)

    if parse failed, user will get {"code": 1, "message": "wrong format", "errorField": ??} as response
    """
    REFLECT_URL_MAP[type_name] = valueof_func


def input(param):
    """
    usage:
    @param.input("$1->uid:n? name->uname phone:s(7-11) icon:file")
    def POST(self, uid, uname, phone, icon):
        return {"data": [uid, uname, phone, [icon.filename, icon.value, icon.file.read()]]}  #file contents Or use a file(-like) object
    """
    def f(g):
        def h(*a, **b):
            it = web.input()
            for param_unit in param.split():
                param_unit, is_optional = (param_unit[:-1], True) if param_unit[-1] == '?' else (param_unit, False)
                left_seg, val_type = param_unit.split(':', 1) if ':' in param_unit else (param_unit, 's')
                front_key, back_key = left_seg.split('->', 1) if '->' in left_seg else (left_seg, left_seg)
                if val_type == 'file':
                    file_it = web.input(**{front_key: {}})
                    real_val = file_it[front_key]
                    if not real_val:
                        if is_optional:
                            real_val = None
                        else:
                            return {'code': 1, 'isEmpty': True, 'errorField': front_key}
                    b[back_key] = real_val
                    continue
                real_val_str = a[int(front_key[1:])] if front_key[0] == '$' else it.get(front_key, None)
                if real_val_str is None:
                    real_val_str = ''
                if real_val_str == '':
                    if is_optional:
                        b[back_key] = None
                        continue
                    else:
                        return {'code': 1, 'isEmpty': True, 'errorField': front_key}
                if '(' in val_type:
                    val_type, restrict = val_type.replace(')', '').split('(')
                    real_val, error_json = REFLECT_URL_MAP[val_type](real_val_str, restrict)
                else:
                    real_val, error_json = REFLECT_URL_MAP[val_type](real_val_str)
                if error_json:
                    error_json['errorField'] = front_key
                    return error_json
                b[back_key] = real_val
            return g(a[0], **b)

        return h

    return f