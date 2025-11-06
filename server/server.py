import zmq, json, time, uuid, os
from datetime import datetime

BROKER = "tcp://broker:5556"
PROXY = "tcp://proxy:5557"
DATA_PATH = "/app/data/data.jsonl"

os.makedirs("/app/data", exist_ok=True)
server_name = os.getenv("SERVER_NAME", "ServerX")
clock = 0

ctx = zmq.Context()
rep = ctx.socket(zmq.REP)
rep.connect(BROKER)

pub = ctx.socket(zmq.PUB)
pub.connect(PROXY)

sub = ctx.socket(zmq.SUB)
sub.connect("tcp://proxy:5558")
sub.setsockopt_string(zmq.SUBSCRIBE, "replicate")

def persist(entry):
    with open(DATA_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

print(f"🧠 {server_name} ativo e conectado ao broker.")

poller = zmq.Poller()
poller.register(rep, zmq.POLLIN)
poller.register(sub, zmq.POLLIN)

while True:
    socks = dict(poller.poll(100))
    # Recebe pedido do broker
    if rep in socks:
        msg = rep.recv_json()
        clock = max(clock, msg.get("clock", 0)) + 1
        svc = msg["service"]

        if svc == "publish":
            entry = {
                "op_id": str(uuid.uuid4()),
                "type": "publish",
                "from": msg["data"]["user"],
                "content": msg["data"]["content"],
                "timestamp": datetime.utcnow().isoformat(),
                "clock": clock,
            }
            persist(entry)
            pub.send_multipart([b"replicate", json.dumps(entry).encode()])
            rep.send_json({"status": "OK", "clock": clock})
        else:
            rep.send_json({"status": "UNKNOWN_SERVICE", "clock": clock})

    # Recebe replicação
    if sub in socks:
        topic, raw = sub.recv_multipart()
        data = json.loads(raw)
        if data.get("op_id"):
            persist(data)
