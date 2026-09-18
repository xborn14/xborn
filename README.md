# 个人主页

基于 HTML/CSS 的单文件个人主页，托管于 GitHub Pages。

访问地址：https://xborn14.github.io/xborn/

## 目录结构

```
personal-homepage/
├── index.html   # 页面主体（样式与脚本内联，单文件自包含）
├── assets/
│   └── hero.jpg # 首屏主视觉（3:4）
└── README.md
```

## 页面内容

主页包含以下板块，内容来自《袁智勇_个人介绍.pdf》：

- **Hero**：姓名、专业身份、一句话简介，邮箱/电话直达入口
- **关于我**：个人简介与基本信息（专业、电话、邮箱、兴趣）
- **专业技能**：6 项技能熟练度（半导体器件 85%、集成电路设计 80%、C/C++ 80%、PCB 设计与制版 75%、Matlab/Simulink 72%、Python 数据分析 70%）
- **兴趣爱好**：足球、吉他
- **自我评价**：自我评价与职业期待
- **联系**：邮箱与电话按钮

## 修改内容

编辑 `index.html` 中的对应文本即可；替换 `assets/hero.jpg`（建议 3:4 竖图）可更换首屏视觉。若需调整技能百分比，同步修改 `.skill-pct` 文本与 `.skill-fill` 的 `style="width:xx%"` 两处。

## 本地预览与更新

- 本地预览：双击 `index.html`（依赖同目录 `assets/`）。
- 更新发布：

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
