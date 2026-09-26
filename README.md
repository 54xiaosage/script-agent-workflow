# 剧本智能体工作流

本地 Web 应用：用**人设圣经 + 正史时间线 + 节拍大纲**约束生成，并用人设守卫、贯通校验、改写循环压住 OOC 和跳轴。

## 工作流

1. **规划师**：根据未完成节拍、正史、近场，给出下一场目标、冲突、必做/禁止。
2. **编剧**：按人设声口与规划写一场。
3. **人设守卫**：检查锁定人设、能力边界、关系态度、台词声口。
4. **贯通编辑**：检查时间地点、不该有的知情、物品伤势、契诃夫之枪。
5. **改写**：对 blocker/major 问题最多改 2 轮（可用环境变量改）。
6. **抽取器**：把已发生事实写入正史、更新角色当前状态。

数据都在 `data/projects/<slug>/`，JSON 可直接改。

## 运行

```powershell
cd C:\Users\script-agent-workflow
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY；可用兼容网关时改 OPENAI_BASE_URL 和 OPENAI_MODEL
uvicorn app.main:app --reload --port 8765
```

浏览器打开 http://127.0.0.1:8765

示例项目 **夜班** 会自动出现在下拉框。先打开人设/大纲看一遍，再点「生成下一场」。

## 怎样让人设稳、剧情连

- **锁定人设**：写进角色的 `locked_traits`，守卫会当硬约束。
- **绝不会说 / 台词样本**：用来钉死声口，避免全员同一张嘴。
- **正史 `locked: true`**：世界规则、已确认事件，生成时不得推翻。
- **节拍 status**：`pending` → `in_progress` → `done`，避免一场写飞到结局。
- **近场窗口**：默认带上最近 4 场正文，保持语气和信息连续。

没有配置密钥时，生成会返回明确错误，不会假装写成功。
