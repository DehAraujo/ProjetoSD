const zmq = require("zeromq");

async function main() {
  const sock = new zmq.Request();
  await sock.connect("tcp://broker:5555");
  console.log("💬 Cliente conectado ao broker.");

  let clock = 0;
  process.stdin.setEncoding("utf8");
  console.log("Digite: publish <mensagem>");

  for await (const line of process.stdin) {
    const [cmd, ...rest] = line.trim().split(" ");
    if (cmd === "publish") {
      clock++;
      const msg = {
        service: "publish",
        data: { user: "CLI_User", content: rest.join(" ") },
        timestamp: new Date().toISOString(),
        clock,
      };
      await sock.send(JSON.stringify(msg));
      const [reply] = await sock.receive();
      console.log("✅ Resposta:", reply.toString());
    }
  }
}

main();
