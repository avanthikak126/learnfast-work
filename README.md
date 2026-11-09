# Learn Fast Workbench

**Your lab bench for a Learn Fast internship.** One command, and you have every library the drill needs —
no `pip install` roulette, no CUDA, no version archaeology.

The workbench is **empty on purpose**. It contains the tools, not the answers. You write your own
notebooks in `work/`, and that folder becomes the repo you submit at the end of the drill.

---

## Start here

You'll make your own copy of this repository, run one command, and work inside it. Your copy is where
your notebooks live and it's what you submit at the end of the drill.

You need a **free GitHub account** and **Docker Desktop** installed. Nothing else.

**Prefer to watch?** The [setup video](https://youtu.be/Ko-nRVbjRxc) walks through all of this, from making your copy to running your first notebook.

### 1. Make your own copy

You're reading this on GitHub, so the button is right above you on this page:

1. Sign in to GitHub (the button doesn't appear until you do).
2. Click the green **Use this template** button at the top right of this page.
3. Choose **Create a new repository**.
4. Give it a name — `learnfast-work` is a good default — and click **Create repository**.

GitHub now has a copy under *your* account. It looks identical, but it belongs to you.

> **Why not Fork?** A fork stays tied to ours and carries our commit history. A template copy starts
> with a clean history, so the commits in it are yours — which matters, because how you build is part
> of what gets assessed.

> **Just want to look around?** You can `git clone` this repo directly and run it without making a copy.
> But you'll need your own repository to submit the drill, so the template route is the one to take.

### 2. Clone your copy and start the workbench

Replace `<your-username>` with your GitHub username, and `lfvision` with your drill's track from the
table below:

```bash
git clone https://github.com/<your-username>/learnfast-work.git
cd learnfast-work
docker compose -f lfvision/docker-compose.yml up
```

The first run downloads and builds the environment — several gigabytes, usually 5–15 minutes. After
that it starts in seconds.

### 3. Open it

<http://127.0.0.1:8889/?token=learnfast>

### 4. Work in the `work/` folder

Create notebooks, write code, break things. Everything you save there is on your own machine, inside
your own git repository.

### 5. Submit

```bash
git add work/ && git commit -m "my drill build" && git push
```

Paste that repository's URL on the drill page. Done.

To stop the workbench: `Ctrl-C`, or `docker compose -f lfvision/docker-compose.yml down`.

---

## Which workbench do I need?

Pick the folder matching your drill's track. Each one is a separate environment — start only the one
you need.

| Folder | Drills | API keys needed |
|---|---|---|
| `lfagenticworkflows/` | Agentic pipelines and orchestration | Yes — see `.env.example` |
| `lfagentinfra/` | MCP servers, A2A, multi-agent orchestration | Yes — see `.env.example` |
| `lfagents/` | Agent frameworks, RAG, LangGraph, multi-agent systems | Yes — see `.env.example` |
| `lfrecsys/` | Recommender systems | **None** |
| `lfretail/` | Retail: market baskets, and a language model trained on them | **None**. Lessons 8 to 11 need an Apple-silicon Mac for MLX; lessons 1 to 7 run in the container |
| `lfcybersecurity/` | Applied cryptography and secure engineering | **None** |
| `lfllm/` | Language modelling from first principles, Build GPT from scratch | **None** |
| `lflogistics/` | Freight and logistics: building a synthetic-data package, a carrier booking agent and a paperwork desk, with a local language model | **None**, but install [Ollama](https://ollama.com) on your machine |
| `lfml/` | Classical ML foundations | **None** |
| `lfpython/` | Python engineering: classes, typed CLI tools, testing, packaging, asyncio and concurrency, NumPy with a FastAPI service, securing an API (authentication, tokens, rate limits), and putting a database behind it (SQLAlchemy, migrations) | **None** |
| `lfrflearning/` | Q-Learning, Deep Q-Networks, Policy Gradients, Dynamic Pricing | **None** |
| `lfsecurity/` | Network traffic and threat classification | **None** |
| `lftools/` | Shipping and monetising AI tools | **None** |
| `lftransformers/` | Transformer architecture and fine-tuning | **None** |
| `lftour/` | AI Tour: PyTorch, Hugging Face, DuckDB, Ray, generative AI, hosting models, agents, and a map of the three clouds | **None** (two lessons offer an optional free-tier key) |
| `lfvision/` | CNNs, GANs, Quantization, Vision Transformers | **None** |

Each folder is a separate environment — start only the one your drill needs.

---

## Things worth knowing

**Give Docker enough memory.** Docker Desktop defaults to about 2 GB. Training anything real will be
killed mid-run and look like a broken image. Set **8 GB or more** in Docker Desktop → Settings →
Resources. This is the single most common "it doesn't work".

**The first start is slow.** Docker builds the image on your machine once, downloading a multi-gigabyte base. After that, seconds.

**Your files live on your machine.** `work/` is a mounted folder — the container reads and writes your
real directory. Delete the container, your work stays. But anything saved *outside* `work/` inside the
container is gone when it stops.

**No GPU needed, ever.** These images install CPU-only PyTorch deliberately. The drills are built around
small models so the internals stay visible on a laptop.

**Nothing leaves your machine.** The vision workbench needs no API keys and makes no outbound calls
except downloading model weights when you ask it to.

---

## Troubleshooting

| What you see | What's happening |
|---|---|
| `port is already allocated` | Something else uses 8889. Change the left-hand number in `docker-compose.yml` to `8890:8888`. |
| Kernel dies during training | Docker memory limit — raise it to 8 GB+ (above). |
| Notebook asks for a token | It's `learnfast`, or use the full URL above. |

---

## What's in here

```
<track>/
  Dockerfile          how the environment is built
  requirements.txt    the libraries, trimmed to what the drills actually use
  docker-compose.yml  how it starts
work/                 ← your notebooks go here (this is what you submit)
```

You're welcome to read and change any of it — it's your repo now. Adding a library is a line in
`requirements.txt` plus `docker compose -f <track>/docker-compose.yml build`.

---

MIT licensed. Built for [Learn Fast](https://learnfast.thili.ai) internships by [thili.ai](https://thili.ai).
