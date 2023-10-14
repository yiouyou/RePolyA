
def cost_usage(_history):
    _cost = []
    _usage = []
    _total_cost = 0
    _total_usage = 0
    for i in _history.keys():
        i_response = _history[i]['response']
        i_cost = i_response['cost']
        i_usage = i_response['usage']['total_tokens']
        _cost.append(i_cost)
        _usage.append(i_usage)
        _total_cost += i_cost
        _total_usage += i_usage
    # print(_cost, _usage)
    return round(_total_cost, 3), _total_usage

