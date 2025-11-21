# Local LLM Setup Guide for Automated Coding Agent

## System Configuration

**Hardware:**
- GPU: NVIDIA GeForce RTX 5060 Ti (16GB VRAM)
- RAM: 32.5GB
- CPU: Intel (13th/14th gen) @ 3.4GHz
- Storage: F:\Ollama\models (for LLM models)

**Software:**
- Ollama: v0.13.0
- Claude Max: Subscription Active
- OS: Windows 11 Pro

---

## Installed Models

### 1. DeepSeek-Coder-V2 (16B) - Primary Model
- **Size**: 8.9GB on disk, ~10GB VRAM when loaded
- **Best For**: Complex coding tasks, multi-file edits, architecture decisions
- **Speed**: Medium (2-3 seconds per response)
- **Quality**: Rivals GPT-4 on most coding tasks

**Usage:**
```bash
# Run model
C:\Users\amazi\AppData\Local\Programs\Ollama\ollama.exe run deepseek-coder-v2:16b

# Test with a simple prompt
C:\Users\amazi\AppData\Local\Programs\Ollama\ollama.exe run deepseek-coder-v2:16b "Write a Python function to calculate fibonacci numbers"
```

---

## Hybrid Usage Strategy (Local + Claude Max)

### Task Routing Logic

```
┌─────────────────────────────────────────────────────────┐
│                    Incoming Coding Task                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ Assess Complexity    │
          └──────────┬───────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   ┌────────┐  ┌────────┐  ┌──────────┐
   │ Simple │  │ Medium │  │ Complex  │
   └───┬────┘  └───┬────┘  └────┬─────┘
       │           │             │
       ▼           ▼             ▼
  ┌──────────┐ ┌────────────┐ ┌───────────────┐
  │DeepSeek  │ │DeepSeek or │ │Claude Sonnet  │
  │ (Local)  │ │Claude Haiku│ │or Opus (Cloud)│
  │  $0      │ │ $0-$0.02   │ │ $0.05-$0.20   │
  └──────────┘ └────────────┘ └───────────────┘
```

### Task Type Classification

| Task Type | Complexity | Recommended Model | Estimated Cost |
|-----------|------------|-------------------|----------------|
| **Code Completion** | Simple | DeepSeek (Local) | $0 |
| **Bug Fixing** | Simple-Medium | DeepSeek (Local) | $0 |
| **Refactoring** | Medium | DeepSeek (Local) | $0 |
| **Writing Tests** | Medium | DeepSeek (Local) | $0 |
| **Documentation** | Simple | DeepSeek (Local) | $0 |
| **Code Review** | Medium | DeepSeek or Claude Sonnet | $0-$0.05 |
| **Architecture Design** | Complex | Claude Opus | $0.15-$0.30 |
| **Multi-File Features** | Complex | Claude Sonnet | $0.05-$0.15 |
| **System Integration** | Complex | Claude Sonnet | $0.05-$0.15 |
| **Performance Optimization** | Complex | Claude Opus | $0.15-$0.30 |

---

## Cost Optimization Strategy

### Monthly Usage Targets

**Goal: <$50/month total**

| Usage Category | Percentage | Model | Monthly Cost |
|----------------|------------|-------|--------------|
| Simple Tasks | 70% (350 tasks) | DeepSeek (Local) | $0 |
| Medium Tasks | 20% (100 tasks) | DeepSeek/Haiku Mix | $10-20 |
| Complex Tasks | 10% (50 tasks) | Claude Sonnet/Opus | $20-30 |
| **Total** | **100% (500 tasks)** | **Hybrid** | **$30-50** |

### Cost-Saving Rules

1. **Always try local first** - DeepSeek is capable of 80%+ of tasks
2. **Use Claude for validation** - Not initial implementation
3. **Batch similar tasks** - Load model once, process multiple items
4. **Cache context** - Reuse codebase context across sessions
5. **Monitor spending** - Track API usage daily

---

## Quick Start Commands

### Starting Ollama Service
```bash
# Check if Ollama is running
tasklist | findstr ollama

# If not running, start it (usually auto-starts)
start C:\Users\amazi\AppData\Local\Programs\Ollama\ollama.exe serve
```

### Using DeepSeek Coder V2

**Interactive Mode:**
```bash
C:\Users\amazi\AppData\Local\Programs\Ollama\ollama.exe run deepseek-coder-v2:16b
```

**One-Shot Command:**
```bash
# Example: Generate a function
C:\Users\amazi\AppData\Local\Programs\Ollama\ollama.exe run deepseek-coder-v2:16b "Create a TypeScript function to validate email addresses using regex"

# Example: Debug code
C:\Users\amazi\AppData\Local\Programs\Ollama\ollama.exe run deepseek-coder-v2:16b "Find the bug in this code: [paste code]"

# Example: Explain code
C:\Users\amazi\AppData\Local\Programs\Ollama\ollama.exe run deepseek-coder-v2:16b "Explain what this function does: [paste code]"
```

### API Usage (for automation)

```python
# Python example using requests
import requests
import json

def ask_deepseek(prompt, code_context=""):
    url = "http://localhost:11434/api/generate"

    full_prompt = f"{code_context}\n\n{prompt}" if code_context else prompt

    payload = {
        "model": "deepseek-coder-v2:16b",
        "prompt": full_prompt,
        "stream": False
    }

    response = requests.post(url, json=payload)
    return response.json()["response"]

# Example usage
result = ask_deepseek(
    "Add error handling to this function",
    code_context="def divide(a, b):\\n    return a / b"
)
print(result)
```

---

## Performance Expectations

### DeepSeek-Coder-V2 (16B) on RTX 5060 Ti

| Metric | Value |
|--------|-------|
| **Load Time** | 3-5 seconds (first run) |
| **Response Speed** | 15-25 tokens/second |
| **VRAM Usage** | ~10GB (leaves 6GB free) |
| **Context Window** | 16,384 tokens (~12,000 words) |
| **Quality** | Comparable to GPT-4 for coding |

### Real-World Timings

| Task | Time |
|------|------|
| Simple function (10-20 lines) | 2-5 seconds |
| Medium function (50-100 lines) | 10-15 seconds |
| Complex multi-file change | 30-60 seconds |
| Code review (200 lines) | 15-30 seconds |
| Full file generation (500 lines) | 60-120 seconds |

---

## When to Use Claude Max Instead

Use your Claude Max subscription when:

1. **Architecture Decisions** - System design needs strategic thinking
2. **Critical Bugs** - Production issues requiring high confidence
3. **Complex Refactoring** - Large-scale code restructuring
4. **Security Reviews** - Vulnerability analysis
5. **Performance Optimization** - Algorithmic improvements
6. **DeepSeek Fails** - If local model gives poor results, escalate to Claude

**Rule of Thumb**: If a task could cost your company money if done wrong, use Claude. If it's routine development work, use DeepSeek.

---

## Integration with Coding Agent System

### Phase 1: Local-Only Testing (Current State)
- All development and testing on DeepSeek
- Verify model works for your use cases
- Build confidence with local models

### Phase 2: Hybrid Router (Next Step)
- Create decision logic to route tasks
- Track success rates by model
- Optimize routing based on performance

### Phase 3: Full Automation
- MCP server integration
- Workflow orchestration with Temporal
- Cost monitoring and alerts

---

## Troubleshooting

### Model Not Loading
```bash
# Check if Ollama service is running
tasklist | findstr ollama

# Restart Ollama
taskkill /F /IM ollama.exe
start C:\Users\amazi\AppData\Local\Programs\Ollama\ollama.exe serve
```

### Out of VRAM Error
- Close other GPU-intensive applications
- Use smaller model (download qwen2.5-coder:7b)
- Reduce context window in requests

### Slow Performance
- Check GPU usage: `nvidia-smi`
- Ensure model is using GPU, not CPU
- Restart Ollama service

### Model Not Found
```bash
# List installed models
C:\Users\amazi\AppData\Local\Programs\Ollama\ollama.exe list

# Verify F: drive path
echo %OLLAMA_MODELS%
# Should show: F:\Ollama\models

# Re-pull model if needed
C:\Users\amazi\AppData\Local\Programs\Ollama\ollama.exe pull deepseek-coder-v2:16b
```

---

## Additional Models to Consider (Optional)

If you want more variety or faster responses:

### Qwen2.5-Coder (14B) - Alternative to DeepSeek
- **Size**: ~8GB
- **VRAM**: ~9GB
- **Speed**: Slightly faster than DeepSeek
- **Quality**: Excellent, comparable to DeepSeek

```bash
C:\Users\amazi\AppData\Local\Programs\Ollama\ollama.exe pull qwen2.5-coder:14b
```

### CodeGemma (7B) - Fast Option
- **Size**: ~4GB
- **VRAM**: ~5GB
- **Speed**: 2x faster than DeepSeek
- **Quality**: Good for simple tasks

```bash
C:\Users\amazi\AppData\Local\Programs\Ollama\ollama.exe pull codegemma:7b
```

### Running Multiple Models
Your 16GB VRAM can fit:
- DeepSeek (10GB) + CodeGemma (5GB) = 15GB ✓
- OR Qwen (9GB) + CodeGemma (5GB) = 14GB ✓

Use CodeGemma for quick completions, DeepSeek/Qwen for complex work.

---

## Next Steps

1. ✅ Ollama installed and configured
2. ⏳ DeepSeek-Coder-V2 downloading (currently in progress)
3. ⬜ Test model with sample coding tasks
4. ⬜ Build hybrid router (local + Claude Max)
5. ⬜ Integrate with MCP servers
6. ⬜ Set up cost monitoring
7. ⬜ Deploy full automation workflow

---

## Cost Tracking Template

Track your usage in a simple spreadsheet:

| Date | Task Type | Model Used | Tokens | Cost | Notes |
|------|-----------|------------|--------|------|-------|
| 2025-11-20 | Bug Fix | DeepSeek | 2,500 | $0 | Fixed auth issue |
| 2025-11-20 | Architecture | Claude Opus | 8,000 | $0.25 | Designed API structure |
| 2025-11-21 | Refactoring | DeepSeek | 5,000 | $0 | Cleaned up utils |

**Monthly Target**: <$50
**Actual Spend**: [Track here]

---

## Support & Resources

- **Ollama Documentation**: https://ollama.com/docs
- **DeepSeek-Coder**: https://github.com/deepseek-ai/DeepSeek-Coder
- **Claude Max**: https://claude.ai
- **This Project**: C:\Users\amazi\Desktop\automated-coding-agent-network

For issues or questions, refer back to the main roadmap document: `ai_coding_agent_roadmap.md`
