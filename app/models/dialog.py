from .status import Status


class DialogRequest:
    request_id = ""
    query = ""
    session_id = ""
    user_id = ""
    session = []
    stream = False


class DialogResponse:
    status = Status
    answer = ""
    title = ""
    recommend_topic = ""
    chunks = ""
