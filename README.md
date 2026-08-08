# 🎬 ClipAI — Agente de IA para Criadores de Conteúdo

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SEU_USUARIO/ClipAI/blob/main/ClipAI.ipynb)

O **ClipAI** é um agente de Inteligência Artificial que roda gratuitamente no Google Colab, projetado para automatizar a criação de cortes virais para YouTube Shorts, TikTok e Instagram Reels — direto de qualquer vídeo do YouTube.

---

## 🚀 Como Executar (Sem Instalação)

1. Clique no badge **Abrir no Colab** acima
2. No menu superior: **Ambiente de execução → Executar tudo** (`Ctrl+F9`)
3. Aguarde ~3 minutos enquanto as dependências são instaladas
4. Clique em **🚀 ABRIR O CLIPAI** ao final

---

## 📐 Skills do Agente

| Skill | Ferramenta | O que faz |
|---|---|---|
| 🎬 Download YouTube | `yt-dlp` | Baixa em máxima qualidade (MP4) |
| ✂️ Detecção Viral | `Whisper` + heurística | Transcreve e pontua os momentos mais virais |
| 📝 Legendas / CC | `Whisper` + `srt` | Gera `.srt` e opcionalmente queima no vídeo |
| 📱 Reframe 9:16 | `ffmpeg` | Recorta e converte para formato TikTok/Reels |

---

## 🏗️ Arquitetura

```
ClipAI/
├── ClipAI.ipynb      ← Notebook Colab (ponto de entrada)
├── main.py           ← Agente principal (loop de menu + skills)
├── skills/
│   ├── viral_detector/   ← Detecção de momentos virais
│   ├── transcriber/      ← Geração de legendas
│   └── reframe/          ← Reformatação 9:16
└── README.md
```

O notebook clona este repositório, instala as dependências via `pip`/`apt`, e abre um **terminal interativo** (`ttyd`) diretamente no navegador — sem precisar de nenhuma instalação local.

---

## ⚙️ Stack Tecnológica

| Componente | Tecnologia |
|---|---|
| Download | [yt-dlp](https://github.com/yt-dlp/yt-dlp) |
| Transcrição & IA | [OpenAI Whisper](https://github.com/openai/whisper) (`small`, roda localmente) |
| Edição de vídeo | [FFmpeg](https://ffmpeg.org/) |
| Legendas | [srt](https://pypi.org/project/srt/) |
| Terminal interativo | [ttyd](https://github.com/tsl0922/ttyd) |
| Infraestrutura | Google Colab (gratuito) |

---

## 📁 Saída dos Arquivos

Todos os arquivos gerados são salvos automaticamente em:

```
Meu Drive/ClipAI/
├── nome_do_video_clips.json        ← Momentos virais detectados
├── nome_do_video.srt               ← Legendas
├── nome_do_video_legendado.mp4     ← Vídeo com legenda queimada
├── nome_do_video_clip01_916.mp4    ← Corte #1 em 9:16
└── nome_do_video_clip02_916.mp4    ← Corte #2 em 9:16
```

---

## 🤝 Como Contribuir

1. Faça um **Fork** do projeto
2. Crie uma branch (`git checkout -b feature/NovaSkill`)
3. Envie o **Pull Request**

Ideias para novas skills: detecção de faces para recorte inteligente, upload automático para TikTok/YouTube, geração de thumbnail com IA.

---

> Desenvolvido com 💜 para criadores de conteúdo brasileiros.
