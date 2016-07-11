def wolfram_query(question):
    import wolframalpha
    # Every service should have a general set of requirements under which
    # it is activated, this would be one of the ones that Wolfram Alpha
    # uses, it does have others as well. Consider having a single method
    # in the plugin system that returns a boolean determining whether
    # a plugin should be activated.
    if question:
        client = wolframalpha.Client(user_info.WOLFRAM_KEY)
        res = client.query(question)
        if len(res):
            if len(res.results):
                answer = res.results[0].text[0]
            else:
                answer = ' '.join([each_answer.subpods[0].text for each_answer in res.pods
                                   if each_answer.subpods[0].text])
        else:
            # answer = "Sorry, Wolfram doesn't know the answer."
            answer = ""

        # Replace some of its notation so it's more easily read.
        answer = answer.replace('\n', '. ').replace('~~', ' or about ')
        # Get the result to a computation and don't bother reading the original question.
        if '=' in answer:
            answer = answer[answer.index('=')+1:].strip()
        return answer
    else:
        print("Wolfram got no question.")


def wolfram_query_old(question):
    import wolframalpha
    # Every service should have a general set of requirements under which
    # it is activated, this would be one of the ones that Wolfram Alpha
    # uses, it does have others as well. Consider having a single method
    # in the plugin system that returns a boolean determining whether
    # a plugin should be activated.
    if question.lower().startswith('wolfram'):
        question = question[8:]
    client = wolframalpha.Client(user_info.WOLFRAM_KEY)
    res = client.query(question)
    try:
        return next(res.results).text  # This really needs to be changed.
        # I shouldn't have to rely upon error catching for my flow control.
    except StopIteration:
        pass
    try:
        answer = '   '.join([each_answer.text for each_answer in res.pods if each_answer])
    except TypeError:
        answer = None
    if not answer:
        answer = "Sorry, Wolfram doesn't know the answer."

    # Replace some of its notation so it's more easily read.
    answer = answer.replace('\n', '; ').replace('~~', ' or about ')
    # Get the result to a computation and don't bother reading the original question.
    if '=' in answer:
        answer = answer[answer.index('=')+1:]
    return [answer, None]  # Follows answer format of [text, action]

