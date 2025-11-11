from agents.assistant_agent import AssistantAgent
from servers.osm_server import OSMServer
from servers.osrm_server import OSRMServer


def repl():
    osm = OSMServer()
    osrm = OSRMServer()
    agent = AssistantAgent({'osm': osm, 'osrm': osrm})
    print('Map Agent Assistant - simple demo. Type \"exit\" to quit.')
    while True:
        txt = input('> ')
        if not txt:
            continue
        if txt.strip().lower() in ('exit', 'quit'):
            break
        try:
            out = agent.handle(txt)
            import json
            print(json.dumps(out, indent=2, ensure_ascii=False))
        except Exception as e:
            print('Error:', e)


if __name__ == '__main__':
    repl()