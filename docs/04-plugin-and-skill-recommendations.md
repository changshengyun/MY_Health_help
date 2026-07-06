# 插件和 Skill 建议

## 1. 当前项目最有用的能力

| 能力 | 用途 | 是否建议 |
| --- | --- | --- |
| Browser 插件 / browser:control-in-app-browser skill | 启动本地页面后，在 Codex 内置浏览器中打开、截图、检查页面是否渲染正常 | 建议使用 |
| node_repl 工具 | 配合 Browser 插件做页面检查、自动化点击、截图验证 | 建议使用 |
| GitHub 插件 / github skills | 后续需要提交代码、开 PR、处理 CI 或 PR 评论时使用 | 可选 |
| Figma 插件 / figma skills | 如果后续想把页面设计稿同步到 Figma 或从 Figma 反推前端 | 可选 |
| Spreadsheets skill | 如果后续要导出饮食和训练数据为 Excel 或 CSV 报告 | 可选 |
| debug-retrospective-writer skill | 如果开发中遇到复杂环境、数据库、构建或调试问题，并且你同意写入中央 debug log 时使用 | 按需 |

## 2. 不建议第一版依赖的能力

| 能力 | 暂不建议原因 |
| --- | --- |
| 云数据库插件 | 当前要求本地 SQLite，云数据库会增加部署和隐私复杂度 |
| 登录鉴权插件 | 第一版只服务单人本地使用 |
| 复杂 AI 图像识别 | 第一版做文字饮食记录和估算即可 |
| 移动端原生插件 | 先完成 Web 版，再考虑移动端 |

## 3. 推荐开发插件组合

### 3.1 本地开发展示

用于边开发边看页面：

- Browser 插件
- node_repl 工具

使用场景：

1. 启动 Vite 本地服务。
2. 在内置浏览器打开 localhost 页面。
3. 截图检查布局。
4. 自动点击打卡、饮食记录、统计页面，验证功能闭环。

### 3.2 版本管理和发布

用于代码完成后的协作：

- GitHub 插件
- github:yeet skill
- github:gh-fix-ci skill
- github:gh-address-comments skill

使用场景：

1. 提交代码到 GitHub。
2. 创建 draft PR。
3. 检查 CI。
4. 处理 PR 评论。

### 3.3 设计稿和演示

用于需要更正式展示时：

- Figma 插件
- figma:figma-generate-design skill
- figma:figma-use skill

使用场景：

1. 把本地 Web 页面捕获到 Figma。
2. 生成可编辑设计稿。
3. 继续打磨 UI 风格。

## 4. 是否需要你额外下载

当前 Codex 环境里已经能搜索到 Browser、Figma、GitHub、node_repl 等相关能力。第一版开发不强制要求你额外下载插件。

建议优先确认：

| 插件 | 是否需要 |
| --- | --- |
| Browser | 强烈建议，用来预览和验收本地页面 |
| GitHub | 如果要推送仓库和开 PR，则建议 |
| Figma | 如果你想做设计稿展示，则建议 |

## 5. 结合本项目的实际建议

第一阶段先用 Browser 插件完成页面展示和交互验证。等本地 SQLite 功能跑通后，再考虑 GitHub 插件提交代码。如果页面想做成可展示设计稿，再使用 Figma 插件。

