# 用户系统 v1 体验研究

目标：从用户任务出发，确定前台自助能力、后台支持能力及第一版稳定体验的验收条件。当前材料是源码审查与合成人格研究的起点，不代表已完成访谈或已经通过生产体验验收。

## 工作材料

- [用例集](use-cases.md)：任务、失败恢复、前后台责任与验收标准。
- [v1 体验基线](v1-experience-baseline.md)：范围、人格假设、优先级与发布门槛。
- [模拟方案](simulation-plan.md)：LiteLLM 认知走查及后续真实界面执行边界。
- [Project 配置](project-spec.json)：GitHub 原生 Project 的一次性创建输入，非持续同步控制器。
- [初始研究任务](research-backlog.json)：10 个可直接建立为私有 Project 草稿的任务，包含验收与用例关联。
- [第一轮走查记录](pilot-2026-10-30.md)：五场景 Codex 多 agent 假设及实际未登录页验证；未执行 LiteLLM。

## 证据规则

每个结论记录来源版本、用例 ID、观察、影响、证据类型、复现步骤与待验证问题。源码检查、合成模型意见、浏览器操作证据、真实用户观察分别标记；模型投票不能把假设升级成用户事实。研究产出不得把“配置存在”“检查通过”当作运行时成功。

GitHub Project 管理状态、负责人和后续任务；此目录管理可评审的规范版本。产品实现回到 `re8ch/user-hub` 或相关后端产品仓库；本仓库不承载产品 Deployment。研究不创建新的 GitOps 控制器。

## 数据边界

仓库实际可见性以 GitHub API 为准；2026-10-30 读取结果为 public，不能按根 README 的 private 描述处理研究数据。本目录只保存通用用例、合成数据和可公开的代码引用。真实访谈、用户身份、会话、原始截图、模型原始输出留在批准的受限存储；公开材料仅引用脱敏证据摘要。Project 使用 private。

## 执行状态（2026-10-30）

- workspace doctor 通过；使用独立 task worktree，从目标仓库 `origin/main` 创建（该 remote 指向 GitHub）。
- 三个 agent 分别编写用例、体验基线、模拟工具，主 agent 汇总与检查。
- GitHub 已安装的 Maintenance App 具备 `organization_projects:write`、`contents:write`、`pull_requests:write`；只读核对并未授予新权限。本次用户明确批准使用当前 `gh` 登录身份执行 Project/PR 操作；后续自动化仍使用现有 App 边界。
- LiteLLM 健康检查成功不代表有推理调用授权；当前插件没有推理工具，真实模型调用待批准入口与模型别名。
- 初稿阶段浏览器工具曾报告禁用；本轮重试已可用，并完成未登录页邮箱入口及空字段验证，详见第一轮走查记录。没有完整登录旅程成功证据。
- 初稿包含 23 个用例、5 个统一编号的行为人格和 5 个模拟场景。UC-14/UC-20 为条件 P0，只有相关能力进入发布范围才启用门槛。
- 本地验证：6 项模拟证据契约测试通过；5 场景 dry-run 全部标记未执行；Identity 策略校验通过（294 个对象）；Kustomize 渲染与 diff whitespace 检查通过。GitHub Actions 尚待 PR 检查；不能视为交付上线。
- 已创建私有 [Identity v1 用户体验研究 Project](https://github.com/orgs/re8ch/projects/3)，关联本仓库，并建立 10 个带优先级、前后台范围、证据级别及验收条件的研究任务。R08（LiteLLM 接口与试验）正在进行，其余待执行。

## GitHub 原生能力依据

使用 [Projects CLI](https://cli.github.com/manual/gh_project) 创建字段、草稿项并关联仓库；使用 [GitHub 官方 Projects 自动化授权说明](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/automating-projects-using-actions) 核对组织 Projects 权限。现有能力满足研究管理，不增加轮询服务、自动发通知或凭证同步器。
