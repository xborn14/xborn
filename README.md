# 个人主页

基于 HTML/CSS 的单文件个人主页，托管于 GitHub Pages。

访问地址：https://xborn14.github.io/xborn/

## 目录结构

```
personal-homepage/
├── index.html   # 页面主体（样式与脚本内联，单文件自包含）
├── assets/      # 图片素材
│   ├── hero.jpg          # 首屏主视觉
│   ├── project-read.jpg  # 项目 1 封面
│   ├── project-data.jpg  # 项目 2 封面
│   └── project-ui.jpg    # 项目 3 封面
└── README.md
```

## 自定义内容

打开 `index.html`，替换以下占位内容：

| 位置 | 当前占位 | 替换为 |
| --- | --- | --- |
| 页面标题 `<title>` | 陈屿 · 全栈开发者 | 你的姓名与身份 |
| Hero 姓名 | 陈屿. | 你的称呼 |
| 一句话简介 | 全栈开发者，专注 Web 产品…… | 你的简介 |
| 社交链接 | GitHub / 邮箱 / 博客 | 你的真实链接 |
| 关于我 | 自述与三个事实条目 | 你的经历要点 |
| 项目卡片 ×3 | 读光 / 城迹 / pine-ui | 你的真实项目 |
| 技能标签 | 前端/后端/工具 | 你的技术栈 |
| 经历时间轴 | 三条占位 | 你的教育与职业经历 |
| 邮箱 | hello@example.com | 你的邮箱 |

`assets/` 下的图片可替换为同尺寸的真实图片（hero 为 3:4，项目封面为 3:2），文件名保持不变即可。

## 本地预览与更新

- 本地预览：双击 `index.html`（依赖同目录 `assets/`）。
- 更新发布：修改文件后执行

```bash
git add .
git commit -m "update"
git push
```

几分钟内 GitHub Pages 会自动更新站点。

## 技术说明

- 单文件自包含：CSS/JS 内联，无构建步骤。
- 字体经自托管镜像加载（Noto Serif SC + Noto Sans SC），离线时回退系统字体。
- 响应式适配桌面与移动端，支持 `prefers-reduced-motion`。
